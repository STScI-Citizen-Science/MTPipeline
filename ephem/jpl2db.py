#! /usr/bin/env python

'''
This module defines the behavior for interacting with the JPL New 
Horizons project via a TELNET connection to obtain ephemerides in RA 
and DEC degree coordinates. This information is written to a MySQL 
database using the SQLAlchemy module.
'''

__version__ = 3

import argparse
import coords
import datetime
import glob
import os
import pyfits
import telnetlib
import time
import logging
import sys

from getpass import getuser
from socket import gethostname
from platform import machine
from platform import platform
from platform import architecture

from database_interface import counter
from database_interface import check_type
from urllib2 import urlopen

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database_interface import loadConnection
from database_interface import MasterImages
from database_interface import MasterFinders

from database_interface import session

LOGFOLDER = "/astro/3/mutchler/mt/logs/"

#----------------------------------------------------------------------------
# Low-Level Functions
#----------------------------------------------------------------------------

def cgi_session(command_list):
    '''
    Interact with NASA JPL HORIZONS via a CGI interface.

    The command_list list characters are replaced to make them URL 
    safe. The urllib2 module is used to connect. A 5 sec pause is 
    enforced to prevent the code from hammering the HORIZONS servers.

    *** NOTE (FROM HORIZONS) ***

    This service is in the beta test and development stage. Support 
    will only be offered to those who've been specifically invited 
    to use this tool. 
    '''
    command_list = [item.replace(' ','%20').replace(':','%3A') for item in command_list]
    url = "http://ssd.jpl.nasa.gov/horizons_batch.cgi?batch=1&COMMAND='{0[0]}'&TABLE_TYPE='{0[2]}'&CENTER='{0[3]}'&START_TIME='{0[4]}'&STOP_TIME='{0[5]}'&STEP_SIZE='{0[6]}'&QUANTITIES='{0[8]}'&CSV_FORMAT='YES'".format(command_list)
    html = urlopen(url).read()
    time.sleep(5.0)
    return html

# ----------------------------------------------------------------------------

def convert_datetime(header_dict):
    '''
    Builds a datetime object from header keywords and returns a 
    datetime object in the JPL Horizons format.
    '''
    header_dict['header_time'] = datetime.datetime.strptime(
        header_dict['date_obs'] + ' ' + header_dict['time_obs'],
        '%Y-%m-%d %H:%M:%S')
    header_dict['horizons_start_time'] = header_dict['header_time'].strftime('%Y-%b-%d %H:%M')
    header_dict['horizons_end_time'] = header_dict['header_time'] + datetime.timedelta(minutes=1)
    header_dict['horizons_end_time'] = header_dict['horizons_end_time'].strftime('%Y-%b-%d %H:%M')
    return header_dict

# ----------------------------------------------------------------------------

def get_header_info(filename):
    '''
    Gets the header info from the FITS file. Checks to ensure that the 
    target name, after string parsing, matches a known planet name.
    '''
    assert os.path.splitext(filename)[1] == '.fits', \
        'Expected .fits got ' + filename
    output = {}
    output['targname'] = pyfits.getval(filename, 'targname').lower().split('-')[0]
    output['date_obs'] = pyfits.getval(filename, 'date-obs')
    output['time_obs'] = pyfits.getval(filename, 'time-obs')
    planet_list = ['mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    assert output['targname'] in planet_list, \
        'Header TARGNAME not in planet_list'
    return output

# ----------------------------------------------------------------------------

def get_jpl_data(moon_dict, connection_type='cgi'):
    '''
    Talk to JPL and get the ephemeris information.
    '''
    assert connection_type in ['telnet', 'cgi'], 'Unexpected connection type.'
    command_list = [moon_dict['id'],
        'e', 'o', 'geo',
        moon_dict['horizons_start_time'],
        moon_dict['horizons_end_time'],
                # '1m', 'y','1,2,3,4', 'n']
        '1m', 'y','1,2,3,4,9,13', 'n']
    if connection_type == 'telnet':
        jpl_data = None
        while jpl_data == None:
            jpl_data = telnet_session(command_list, verbose=True)
        jpl_dict = parse_jpl_telnet(jpl_data)
    elif connection_type == 'cgi':
        jpl_data = cgi_session(command_list)
        jpl_dict = parse_jpl_cgi(jpl_data)
    return jpl_dict

# ----------------------------------------------------------------------------

def make_all_moon_dict(filename, file_dict):
    '''
    Parses the text file for id numbers of the moons and the planet. 
    Returns a dict.
    '''
    path_to_code = os.path.dirname(__file__)
    f = open(os.path.join(path_to_code, 'planets_and_moons.txt'), 'r')
    full_moon_list = f.readlines()
    f.close()

    all_moon_dict = {}
    moon_switch = False
    for line in full_moon_list:
        line = line.strip().split()
        if line != [] and line[-1] == file_dict['targname']:
            moon_switch = True
        if moon_switch:
            if line != []:
                all_moon_dict[line[1]] = {'id': line[0], 'object': line[1]}
            else:
                break
    return all_moon_dict

# ----------------------------------------------------------------------------

def insert_record(moon_dict,  master_images_id):
    '''
    Make a new record to be in the master_finders table.
    '''
    record = MasterFinders()
    record.object_name = moon_dict['object']
    record.jpl_ra = moon_dict['jpl_ra']
    record.jpl_dec = moon_dict['jpl_dec']
    try:
        record.diameter = float(moon_dict['jpl_ang_diam'])
    except Exception as err:
        logger.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    try:
        record.magnitude = float(moon_dict['jpl_APmag'])
    except Exception as err:
        logger.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    record.master_images_id = master_images_id
    record.version = __version__
    session.add(record)
    session.commit()

# ----------------------------------------------------------------------------

def telnet_session(command_list, verbose=False):
    '''
    Performs the telnet operations and returns the ephemeride data.
    '''
    tn = telnetlib.Telnet()
    tn.open('ssd.jpl.nasa.gov', '6775')
    output = tn.read_until('Horizons>', timeout = 30)
    if verbose:
        print output
    for command in command_list:
        tn.write(command + '\r\n')
        output = tn.read_until('] :', timeout = 30)
        if command == '1,2,3,4':     
            data = output
        if verbose:
            print output
    tn.close()
    return data

# ----------------------------------------------------------------------------

def parse_jpl_cgi(data):
    '''
    Parses the relevant information from the cgi output.
    '''
    check_type(data, str)
    output = {}
    soe_switch = False
    data = data.split('\n')
    for line in data:
        if line == '$$EOE':
            break
        if soe_switch:
            line = line.split(',')
            line = [item.strip() for item in line if item != ',']
            output['date'] = line[0]
            output['jpl_ra'] = line[3].replace(' ',':')
            output['jpl_dec'] = line[4].replace(' ',':')
            output['jpl_ra_apparent'] = line[5].replace(' ',':')
            output['jpl_dec_apparent'] = line[6].replace(' ',':')
            output['jpl_ra_delta'] = line[7]
            output['jpl_dec_delta'] = line[8]
            output['jpl_APmag'] = line[11]
            output['jpl_ang_diam'] = line[13]
            return output
        if line == '$$SOE':
            soe_switch = True

# ----------------------------------------------------------------------------

def parse_jpl_telnet(data):
    '''
    Grab the relevant information from the telnet output. 
    (Not updated to include magnitude and diameter information)
    '''
    section = 0
    output = {}
    keys = []
    data = data.split('\n')
    for line in data:
        line = line.strip()
        if line != '':
            if line[0] == '*':
                section += 1
            elif section == 1:
                line = line.split()
                if line[0] == 'Target':
                    output['target'] = line[3]
            elif section == 2:
                pass
            elif section == 4:
                pass
            elif section == 5:
                if line[0] != '$':
                    line = line.split()
                    output['date'] = line[0] + ' ' + line[1]
                    output['jpl_ra'] = line[2] + ':' + line[3] + ':' + line[4]
                    output['jpl_dec'] = line[5] + ':' + line[6] + ':' + line[7]
                    output['jpl_ra_apparent'] = line[8] + ':' + line[9] + ':' + line[10]
                    output['jpl_dec_apparent'] = line[11] + ':' + line[12] + ':' + line[13]
                    output['jpl_ra_delta'] = line[14]
                    output['jpl_dec_delta'] = line[15]
                    # output['']
                    return output

# ----------------------------------------------------------------------------

def update_record(moon_dict, master_images_id):
    '''
    Update a record in the master_finders table.
    '''
    update_dict = {}
    update_dict['object_name'] = moon_dict['object']
    update_dict['jpl_ra'] = moon_dict['jpl_ra']
    update_dict['jpl_dec'] = moon_dict['jpl_dec']
    try:
        update_dict['magnitude'] = float(moon_dict['jpl_APmag'])
    except Exception as err:
        logger.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    try:
        update_dict['diameter'] = float(moon_dict['jpl_ang_diam'])
    except Exception as err:
        logger.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    update_dict['master_images_id'] = master_images_id
    update_dict['version'] = __version__
    session.query(MasterFinders).filter(\
        MasterFinders.master_images_id == master_images_id, 
        MasterFinders.object_name == moon_dict['object']).update(update_dict)
    session.commit()

#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------

def jpl2db_main(filename, reproc=False):
    '''
    The main controller. 
    '''
    # Get the unique record from the master_images table.
    assert os.path.splitext(filename)[1] == '.fits', \
        'Expected .fits got ' + filename
    master_images_query = session.query(MasterImages).filter(\
        MasterImages.fits_file == os.path.basename(filename)).one()

    # Gather some file information and iterate over the moons
    file_dict = get_header_info(os.path.abspath(filename))
    file_dict = convert_datetime(file_dict)
    all_moon_dict = make_all_moon_dict('planets_and_moons.txt', file_dict)
    for moon in all_moon_dict.keys():
        moon_dict = all_moon_dict[moon]
        moon_dict.update(file_dict)

        # Check if a record exists. If there's no record insert one.
        master_finders_count = session.query(MasterFinders).filter(\
            MasterFinders.master_images_id == master_images_query.id).filter(\
            MasterFinders.object_name == moon).count()
        if master_finders_count == 0:
            jpl_dict = get_jpl_data(moon_dict)
            moon_dict.update(jpl_dict)
            insert_record(moon_dict, master_images_query.id)

        # When a record exists, check if it has jpl_ra info. If it 
        # doesn't then update.        
        else:
            master_finders_count = session.query(MasterFinders).filter(\
                MasterFinders.master_images_id == master_images_query.id).filter(\
                MasterFinders.object_name == moon).filter(\
                MasterFinders.jpl_ra == None).count()
            if master_finders_count == 1 or reproc == True:
                jpl_dict = get_jpl_data(moon_dict)
                moon_dict.update(jpl_dict)
                update_record(moon_dict, master_images_query.id)

    session.close()

#----------------------------------------------------------------------------
# For Command Line Execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Populate the database with the jpl coordinates.')
    parser.add_argument(
        '-filelist',
        required = True,
        help = 'Search string for FITS files. Wildcards accepted.')
    parser.add_argument(
        '-reproc',
        required = False,
        action = 'store_true',        
        default = False,
        dest = 'reproc',
        help = 'Overwrite existing entries.')
    args = parser.parse_args()
    return args

#----------------------------------------------------------------------------
    
if __name__ == '__main__':
    args = parse_args()
    filelist = glob.glob(args.filelist)
    logger = logging.getLogger('jpl2db')
    logger.setLevel(logging.DEBUG)
    log_file = logging.FileHandler(
        os.path.join(
            LOGFOLDER, 
            'jpl2db-' + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'))
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_file)
    logger.info('User: {0}'.format(getuser()))
    logger.info('Host: {0}'.format(gethostname())) 
    logger.info('Machine: {0}'.format(machine()))
    logger.info('Platform: {0}'.format(platform()))
    logger.info("Command-line arguments used:")
    for arg in args.__dict__:
        logger.info(arg + ": " + str(args.__dict__[arg]))
    rootfile_list = glob.glob(args.filelist)
    rootfile_list = [x for x in rootfile_list if len(os.path.basename(x)) == 18]
    assert isinstance(filelist, list), \
        'Expected list for filelist, got ' + str(type(filelist))
    assert filelist != [], 'No files found.'
    print 'Processing ' + str(len(filelist)) + ' files.'
    logger.info('Processing' + str(len(filelist)) + 'f iles.')
    count = 0
    for filename in filelist:
        logger.info ('Now running for ' + filename)
        try:
            jpl2db_main(filename, args.reproc)
            logger.info ("Completed for  : " + filename)
        except Exception as err:
            logger.critical('{0} {1} {2}'.format(
                type(err), err.message, sys.exc_traceback.tb_lineno))
        count = counter(count, update = 10)