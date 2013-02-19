#! /usr/bin/env python

'''
This module defines the behavior for interacting with the JPL New 
Horizons project via a TELNET connection to obtain ephemerides in RA 
and DEC degree coordinates. This information is written to a MySQL 
database using the SQLAlchemy module.
'''

__version__ = 2

import argparse
import coords
import datetime
import glob
import os
import pyfits
import telnetlib

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database_interface import loadConnection
from database_interface import MasterImages
from database_interface import MasterFinders

session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')

#----------------------------------------------------------------------------
# Low-Level Functions
#----------------------------------------------------------------------------

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

def get_jpl_data(moon_dict):
    '''
    Talk to JPL and get the ephemeris information.
    '''
    command_list = [moon_dict['id'],
        'e', 'o', 'geo',
        moon_dict['horizons_start_time'],
        moon_dict['horizons_end_time'],
        '1m', 'y','1,2,3,4', 'n']
    jpl_data = None
    while jpl_data == None:
        jpl_data = telnet_session(command_list, verbose=True)
    jpl_dict = parse_jpl(jpl_data)
    return jpl_dict

# ----------------------------------------------------------------------------

def make_all_moon_dict(filename, file_dict):
    '''
    Parses the text file for id numbers of the moons and the planet. 
    Returns a dict.
    '''
    path_to_code = os.path.dirname(__file__)
    f = open(os.path.join(path_to_code, 'planets_and_moons.txt'))
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
    output = tn.read_until('Horizons>', timeout = 10)
    if verbose:
        print output
    for command in command_list:
        tn.write(command + '\r\n')
        output = tn.read_until('] :', timeout = 10)
        if command == '1,2,3,4':     
            data = output
        if verbose:
            print output
    tn.close()
    return data

# ----------------------------------------------------------------------------

def parse_jpl(data):
    '''
    Grab the relevant information from the telnet output.
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
        help = 'Search string for files. Wildcards accepted.')
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
    assert isinstance(filelist, list), \
        'Expected list for filelist, got ' + str(type(filelist))
    for filename in filelist:
        jpl2db_main(filename, args.reproc)
