#! /usr/bin/env python

"""Module for populating the `master_finders` table.

The module will populate the `master_finders` table of the 
database specified in the connection strong of the `settings.yaml` 
file. 

The ephemerides data is retrieved from NASA JPL HORIZONS via an
undocumented CGI interface. Permission to use this interface was
specifically granted by JPL HORIZONS software engineers. JPL queries
are built using the header information in each FITS file.

These values catalog the expected position of the known
gravitationally-bound minor bodies of solar system planets (including
Pluto). Specifically, this is not a "cone search" for other targets in
the field of view of the image. Instead this catalogs the positions
for all the known moons in for planets in the solar system at the date
and time specified in the image header. There are no criteria for accepting 
the ephemerides returned Field of view and magnitude
cutoffs are not used to reject records. The record will include
predicted magnitude, diameter, and x and y positions in units of
pixels and relative to the camera reference pixels. 

Database interactions are implemented using the SQLAlchemy ORM module
with the declarative base bindings. Further information can be found 
in the `mtpipeline.database` module. 

Authors:
    Alex Viana, January 2013
    Wally Barbosa, July 2014

Use:
    XXX

Outputs:
    Updates the `master_finders` table.
"""

import argparse
import coords
import datetime
import glob
import logging
import os
import sys
import time

from astropy.io import fits
from mtpipeline.database.database_tools import counter
from mtpipeline.database.database_tools import check_type
from mtpipeline.setup_logging import setup_logging
from urllib2 import urlopen

#----------------------------------------------------------------------------
# SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from mtpipeline.database.database_interface import MasterImages
from mtpipeline.database.database_interface import MasterFinders
from mtpipeline.database.database_interface import session

#----------------------------------------------------------------------------
# Deprecated Functions for TELNET JPL HORIZONS interface.
#----------------------------------------------------------------------------

def _parse_jpl_telnet(data):
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
                    return output


def _telnet_session(command_list, verbose=False):
    '''
    Performs the telnet operations and returns the ephemeride data.

    Requires: 
        telnetlib package
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


#----------------------------------------------------------------------------
# Functions
#----------------------------------------------------------------------------


def cgi_session(command_list):
    """Interact with NASA JPL HORIZONS via a CGI interface.

    The command_list list characters are replaced to make them URL 
    safe. The urllib2 module is used to connect. 

    Parameters: 
        command_list : list
            List of strings of inputs for the JPL HORIZONS CGI 
            interface.

    Returns: 
        html : iterable
            iterable object from `urlopen().read()`

    Outputs:
        nothing

    Notes:
        This service is in the beta test and development stage. Support 
        will only be offered to those who've been specifically invited 
        to use this tool. There is no rate limit on the requests but 
        requests should only be issued serially (not in parallel).
    
    References:
        The standard web interface, which mirrors the CGI API can be 
        found here: http://ssd.jpl.nasa.gov/horizons.cgi
    """
    command_list = [item.replace(' ','%20').replace(':','%3A') 
                    for item 
                    in command_list]
    url = ("http://ssd.jpl.nasa.gov/horizons_batch.cgi?batch=1&"
           "COMMAND='{0[0]}'&TABLE_TYPE='{0[2]}'&CENTER='{0[3]}'&"
           "START_TIME='{0[4]}'&STOP_TIME='{0[5]}'&STEP_SIZE='{0[6]}'&"
           "QUANTITIES='{0[8]}'&CSV_FORMAT='YES'").format(command_list)
    html = urlopen(url).read()
    return html


def calc_delta(hdulist, record):
    """Calculate JPL coordinate and HST reference pixel deltas.

    The calculation is performed in degrees and then converted to 
    pixels in the return the result in pixels. The unit conversion is 
    performed using a `Coord` class in `coords.py`. This module was 
    directly copied from the `position.py` module of the 
    `astrolib.coords` library. 

    Parameters: 
        hdulist : HDUList instance
            pyfits.io.fits.hdulist object
        record : dict
            The record dictionary

    Returns: 
        delta_x : float
            Float of the delta_x shift in pixels.
        delta_y : float
            Float of the delta_y shift in pixels.

    Outputs:
        nothing

    Notes: 
        If this function requires updates in the future it would
        probably  be preferable to update this to use `astropy` 
        library instead.  Also, the values for the degree to pixel 
        conversion are currently only for WFPC2. 
    """ 
    assert isinstance(record, dict), \
        'Expected dict got ' + str(type(record))

    crval1 = hdulist[0].header['CRVAL1']
    crval2 = hdulist[0].header['CRVAL2']

    # Convert the coordinates to coords instances in degrees.
    record = convert_coords(record)
    refpic_coords = coords.Degrees((crval1, crval2))
    crval1, crval2 = refpic_coords.a1, refpic_coords.a2
    
    # Take the difference and convert to pixels.
    # RA increases to the East (left) so we switch the sign on the delta.
    # Note these values are for WFPC2 only.
    delta_x = -1 * (record['jpl_ra'] - crval1) * (3600. / 0.05)
    delta_y = (record['jpl_dec'] - crval2) * (3600. / 0.05)

    assert isinstance(delta_x, float), \
        'Expected float got ' + str(type(delta_x))
    assert isinstance(delta_y, float), \
        'Expected float got ' + str(type(delta_y))
    return delta_x, delta_y


def calc_pixel_position(hdulist, delta_x, delta_y):
    """Return the x and y position of the ephemeris in pixel space.

    This function takes the ephemerides deltas (in pixels) and applies 
    them to the reference pixel locations used to determine to the 
    pointing to calculate the ephemerides position in detector pixel 
    space.

    Parameters: 
        hdulist : HDUList instance
            pyfits.io.fits.hdulist object
        delta_x : float
            Float of the delta_x shift in pixels.
        delta_y : float
            Float of the delta_y shift in pixels.

    Returns: 
        ephem_x : float
            Float of the ephem_x in pixels.
        ephem_y : float
            Float of the ephem_y in pixels.
    """
    assert isinstance(delta_x, float), \
        'Expected float type got ' + str(type(delta_x))
    assert isinstance(delta_y, float), \
        'Expected float type got ' + str(type(delta_y))
    ephem_x = hdulist[0].header['CRPIX1'] + delta_x
    ephem_y = hdulist[0].header['CRPIX2'] + delta_y
    assert isinstance(ephem_x, float), \
        'Expected float type got ' + str(type(ephem_x))
    assert isinstance(ephem_y, float), \
        'Expected float type got ' + str(type(ephem_y))
    return ephem_x, ephem_y


def convert_datetime(header_dict):
    """Update the header_dict with datetime information. 
        
    Uses the `datetime` module to transform header keywords in the 
    `header_dict` to strings in the expected JPL Horizons format
    used to build the CGI query.
    
    Parameters: 
        header_dict : dict
            Header of information copied from or derived from the 
            image header.

    Returns: 
        header_dict : dict
            Header of information copied from or derived from the 
            image header.
    """
    header_dict['header_time'] = datetime.datetime.strptime(
        header_dict['date_obs'] + ' ' + header_dict['time_obs'],
        '%Y-%m-%d %H:%M:%S')
    header_dict['horizons_start_time'] = header_dict['header_time'].strftime('%Y-%b-%d %H:%M')
    header_dict['horizons_end_time'] = header_dict['header_time'] + datetime.timedelta(minutes=1)
    header_dict['horizons_end_time'] = header_dict['horizons_end_time'].strftime('%Y-%b-%d %H:%M')
    return header_dict


def convert_coords(moon_dict):
    """
    Convert the JPL coordinates to degrees.

    The unit conversion is performed using a `Coord` class in 
    `coords.py`. This module was  directly copied from the
    `position.py` module of the  `astrolib.coords` library.

    Parameters: 
        moon_dict : dict
            Dictionary of ephemerides information for a moon from 
            headers and JPL results. 
    
    Returns: 
        moon_dict : dict
            Dictionary of ephemerides information for a moon from 
            headers and JPL results. 

    Notes: 
        If this function requires updates in the future it would
        probably  be preferable to update this to use `astropy` 
        library instead.  Also, the values for the degree to pixel 
        conversion are currently only for WFPC2. 
    """
    assert isinstance(moon_dict, dict), \
        'Expected dict for moon_dict, got ' + str(type(moon_dict))
    jpl_pos = coords.Hmsdms(moon_dict['jpl_ra'] + ' ' + moon_dict['jpl_dec'])
    moon_dict['jpl_ra'], moon_dict['jpl_dec'] = jpl_pos._calcinternal()
    return moon_dict


def get_planet_and_moons_list():
    """Return a list of valid JPL HORIZONS targets.

    The JPL HORIZONS interface accepts a strict set of target names. 
    In order to 

    XXX

    Parameters: 
        nothing

    Returns: 
        planet_and_moon_list: list
            List of terms that match all the planet and moon targets 
            in the WFPC2 dataset.

    Outputs:
        nothing
    """
    planet_and_moon_list = ['jup-', 'gany-', 'sat-', 'copernicus', 'gan-', 
                            'io-']
    with open('mtpipeline/ephem/planets_and_moons.txt', 'r') as f:
        planets_and_moons_file = f.readlines()
    for line in planets_and_moons_file:
        line = pm.split(' ')
        if len(line) > 3:
            planet_and_moon_list.append(line[1])
    return planet_and_moon_list


def get_header_info(hdulist):
    """Gets the header info from the FITS file. 

    Checks to ensure that the target name, after string parsing, 
    matches a known planet name.

    Parameters: 
        hdulist : HDUList instance

    Returns: 
        output : dict
            A dict containing the header information needed to build 
            the JPL HORIZONS request. 

    Outputs:
        nothing
    """
    output = {}
    output['targname'] = hdulist[0].header['targname'].lower().split('-')[0]
    output['date_obs'] = hdulist[0].header['date-obs']
    output['time_obs'] = hdulist[0].header['time-obs']
    for pm in PLANETS_MOONS:
        if pm in output['targname']:
            return output
    assert status, 'Header TARGNAME not in planet_list'


def get_jpl_data(moon_dict):
    """Get the ephemeris information from JPL HORIZONS.

    This function builds a list of the JPL "commands" and then
    calls the functions to request and parse and ephemerides data. 

    Parameters: 
        moon_dict : dict
            A dictionary of with the information needed to build the 
            JPL request.

    Returns: 
        jpl_dict : dict
            A dict containing the ephemerides data. 

    Outputs:
        nothing
    """
    command_list = [moon_dict['id'], 'e', 'o', 'geo',
                    moon_dict['horizons_start_time'],
                    moon_dict['horizons_end_time'],
                    '1m', 'y', '1,2,3,4,9,13', 'n']
    jpl_data = cgi_session(command_list)
    jpl_dict = parse_jpl_cgi(jpl_data)
    return jpl_dict


def make_all_moon_dict(file_dict):
    """Get the JPL HORIZONS id number for each moon.

    Using the target name retrieve a list of object names and JPL 
    HORISONS ids associated with that target name. 

    Parameters: 
        file_dict : dict
            A dictionary of FITS file information.

    Returns: 
        all_moon_dict : dict
            A dict containing the JPL id and object information 
            for each

    Outputs:
        nothing

    Notes:
        This is an inefficient design pattern. It requires that the 
        table be read in from the disk on every iteration and then 
        parsed using custom code. This should be reimplemented so that 
        (1) the data is stored in a standard file format like YAML so 
        it can be read in more easily and (2) the information should 
        be read in once and then kept in memory. 
    """
    path_to_code = os.path.dirname(__file__)
    file_name = os.path.join(path_to_code, 'planets_and_moons.txt')
    with open(file_name, 'r') as f:
        full_moon_list = f.readlines()

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


def insert_record(hdulist, moon_dict,  master_images_id):
    """Insert a new record into the `master_finders` table.

    If there is no magnitude or diameter information, this raises an 
    excepted error and is logged in the log file. This was originally 
    implemented to help debug the cases where these keys were NULL in 
    the database because JPL did not have magnitude or diameter for 
    those moons. But this is not handled by setting those values to 
    -999 in `parse_jpl_cgi` so these exceptions should never happen.

    Parameters: 
        hdulist : HDUList instance
            pyfits.io.fits.hdulist object
        all_moon_dict : dict
            A dict containing the JPL id and object information 
            for each
        master_images_id: int
            The foreign key from the master_images parent table.

    Outputs:
        Issues a SQL `COMMIT` statement to write the `INSERT` 
        statement to the master_finders database table. 

    Notes:
        This is an inefficient design pattern in that it write to 
        the database every time the function is executed. Because 
        there are hundred of thousands of records to write and 
        roughly 5 records are processed a second it would be more 
        efficient to only commit periodically, say every hundred or 
        thousand records.
    """
    record = MasterFinders()
    record.object_name = moon_dict['object']
    record.jpl_ra = moon_dict['jpl_ra']
    record.jpl_dec = moon_dict['jpl_dec']
    delta_x, delta_y = calc_delta(hdulist, moon_dict)
    ephem_x, ephem_y = calc_pixel_position(hdulist, delta_x, delta_y)
    record.ephem_x = int(ephem_x)
    record.ephem_y = int(ephem_y)
    try:
        record.diameter = float(moon_dict['jpl_ang_diam'])
    except Exception as err:
        logging.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    try:
        record.magnitude = float(moon_dict['jpl_APmag'])
    except Exception as err:
        logging.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    record.master_images_id = master_images_id
    record.version = __version__
    session.add(record)
    session.commit()


def parse_jpl_cgi(data):
    """Parses the JPL HORIZONS CGI output.

    Build an instance of the MasterFinders ORM class and populate the 
    fields using the instance attributes. Occasionally, but not 
    infrequently, there is no magnitude or diameter information, 
    these values are instead entered as -999.

     Parameters: 
        data : iterable
            The HTML data from the CGI output.

    Returns:
        output : dict
            A dictionary of the relevant strings from the CGI data.

    Outputs:
        nothing
    """
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
            for key in ['jpl_APmag', 'jpl_ang_diam']:
                if output[key] == 'n.a.':
                    output[key] = '-999'
            return output
        if line == '$$SOE':
            soe_switch = True


def update_record(hdulist, moon_dict, master_images_id): # changed this function. added hdulist as a parameter and added the ephemerides calculations.
    '''
    Update a record in the master_finders table.
    '''
    update_dict = {}
    update_dict['object_name'] = moon_dict['object']
    update_dict['jpl_ra'] = moon_dict['jpl_ra']
    update_dict['jpl_dec'] = moon_dict['jpl_dec']
    delta_x, delta_y = calc_delta(hdulist, moon_dict)
    ephem_x, ephem_y = calc_pixel_position(hdulist, delta_x, delta_y)
    update_dict['ephem_x'] = int(ephem_x)
    update_dict['ephem_y'] = int(ephem_y)
    try:
        update_dict['magnitude'] = float(moon_dict['jpl_APmag'])
    except Exception as err:
        logging.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    try:
        update_dict['diameter'] = float(moon_dict['jpl_ang_diam'])
    except Exception as err:
        logging.critical('{0} {1} {2}'.format(
            type(err), err.message, sys.exc_traceback.tb_lineno))
    update_dict['master_images_id'] = master_images_id
    update_dict['version'] = __version__
    session.query(MasterFinders).filter(\
            MasterFinders.master_images_id == master_images_id,
            MasterFinders.object_name == moon_dict['object']).update(update_dict)
    session.commit()

"""
    def run_ephem_main(reproc=False):
    '''
    The main controller for the module. It executes the code in ephem_main
    and writes the output to the database.
    '''
    
    # Build the record list and log the length.
    query_all_records = session.query(MasterFinders, MasterImages).\
    join(MasterImages).\
    options(subqueryload('master_images_rel'))
    logging.info('{} total records in master_finders.'.\
    format(query_all_records.count()))
    if reproc == True:
    query_list = query_all_records.all()
    logging.info('reproc == True, Reprocessing all records')
    else:
    logging.info('reproc == False')
    query_list = session.query(MasterFinders, MasterImages).\
    join(MasterImages).\
    options(subqueryload('master_images_rel')).\
    filter(or_(MasterFinders.jpl_ra != None, MasterFinders.jpl_dec != None)).\
    all()
    logging.info('Processing {} files where ephem_x or ephem_y IS NULL.'.\
    format(len(query_list)))
    
    for counter, record in enumerate(query_list):
    logging.info('Working on {}'.\
    format(record.MasterImages.name, record.MasterFinders.object_name))
    file_dict = get_header_info(\
    os.path.join(\
    record.MasterImages.file_location[0:-4],
    record.MasterImages.fits_file))
    delta_x, delta_y = calc_delta(file_dict, record.MasterFinders)
    ephem_x, ephem_y = calc_pixel_position(file_dict, delta_x, delta_y)
    update_dict = {}
    update_dict['ephem_x'] = int(ephem_x)
    update_dict['ephem_y'] = int(ephem_y)
    session.query(MasterFinders).\
    filter(MasterFinders.id == record.MasterFinders.id).\
    update(update_dict)
    if counter % 100 == 0:
    session.commit()
    session.close()
"""

#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------

def ephem_main(filename, reproc=False):
    '''
    The main controller. 
    '''
    # Get the unique record from the master_images table.
    assert filename[-5:] == '.fits', \
        'Expected .fits got ' + filename
    master_images_query = session.query(MasterImages).filter(\
        MasterImages.fits_file == os.path.basename(filename)).one()
    hdulist = fits.open(filename)

    # Gather some file information and iterate over the moons
    file_dict = get_header_info(hdulist)
    file_dict = convert_datetime(file_dict)
    all_moon_dict = make_all_moon_dict(file_dict)
    for moon in all_moon_dict:
        logging.info('Processing {} for {}'.format(moon, filename))
        moon_dict = all_moon_dict[moon]
        moon_dict.update(file_dict)

        # Check if a record exists. If there's no record insert one.
        master_finders_count = session.query(MasterFinders).filter(\
            MasterFinders.master_images_id == master_images_query.id).filter(\
            MasterFinders.object_name == moon).count()
        if master_finders_count == 0:
            jpl_dict = get_jpl_data(moon_dict)
            moon_dict.update(jpl_dict)
            insert_record(hdulist, moon_dict, master_images_query.id)

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
                update_record(hdulist, moon_dict, master_images_query.id)

    session.close()

#----------------------------------------------------------------------------
# For Command Line Execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Populate the database with the jpl coordinates.',
        epilog='-missing_only and -filelist are mutually exclusive.')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-filelist',
        required = False,
        help = 'Search string for FITS files. Wildcards accepted. \
            Must be used if missing_only is not used.')
    group.add_argument(
        '-missing_only',
        action = 'store_true',        
        default = None,
        required = False)
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
    
    PLANETS_MOONS = get_planet_and_moon_list()
    
    # Set up the inputs and logging.
    args = parse_args()
    setup_logging('build_master_finders_table')
   
    # Log the system and user information.
    logging.info("Command-line arguments used:")
    for arg in args.__dict__:
        logging.info(arg + ": " + str(args.__dict__[arg]))

    # Create the filelist.
    if args.filelist != None:
        filelist = glob.glob(args.filelist)
        filelist = [x for x in filelist if 'c0m_wide_single_sci.fits' in x]
        assert isinstance(filelist, list), \
            'Expected list for filelist, got ' + str(type(filelist))
        assert filelist != [], 'No files found.'
    elif args.missing_only == True:
        master_finders_query = session.query(MasterImages).\
                               outerjoin(MasterFinders).\
                               filter(MasterFinders.object_name == None).all()
        filelist = [os.path.join(record.file_location[:-4], record.fits_file) \
                    for record in master_finders_query]
    print 'Processing ' + str(len(filelist)) + ' files.'
    logging.info('Processing ' + str(len(filelist)) + ' files.')

    # Run with exception handling.
    count = 0
    for filename in filelist:
        logging.info ('Now running for ' + filename)
        try:
            ephem_main(filename, args.reproc)
            logging.info ("Completed for  : " + filename)
            print 'Completed for: ' + filename
        except Exception as err:
            logging.critical('{0} {1} {2}'.format(
                type(err), err.message, sys.exc_traceback.tb_lineno))
        count = counter(count, update = 10)