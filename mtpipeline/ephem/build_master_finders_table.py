#! /usr/bin/env python

"""Calculate the ephemerides positions in pixels from the information 
in the FITS file and the database. Write the results back to the 
database."""

import argparse
import coords
import glob
import logging
import os
import pyfits

from mt_logging import setup_logging
from socket import gethostname

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from mtpipeline.database.database_interface import MasterImages
from mtpipeline.database.database_interface import MasterFinders
from mtpipeline.database.database_interface import session
from mtpipeline.database.database_tools import counter

from sqlalchemy import or_
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm import subqueryload_all

#----------------------------------------------------------------------------
# Low-Level Functions
#----------------------------------------------------------------------------

def calc_delta(file_dict, record):
    '''
    Find the difference between the JPL coordinates at the HST 
    reference pixel coordinates. Perform the difference in degrees and 
    return the result in pixels.
    '''
    assert isinstance(file_dict, dict), \
        'Expected dict got ' + str(type(file_dict))
    assert isinstance(record, MasterFinders), \
        'Expected dict got ' + str(type(record))

    # Convert the coordinates to coords instances in degrees.
    jpl_pos = coords.Hmsdms(record.jpl_ra + ' ' + record.jpl_dec)
    jpl_ra, jpl_dec = jpl_pos._calcinternal()
    refpic_coords = coords.Degrees((file_dict['CRVAL1'], file_dict['CRVAL2']))
    file_dict['CRVAL1'], file_dict['CRVAL2'] = refpic_coords.a1, refpic_coords.a2

    # Take the difference and convert to pixels.
    # RA increases to the East (left) so we switch the sign on the delta.
    delta_x = -1 * (jpl_ra - file_dict['CRVAL1']) * (3600. / 0.05)
    delta_y = (jpl_dec - file_dict['CRVAL2']) * (3600. / 0.05)
    assert isinstance(delta_x, float), \
        'Expected float got ' + str(type(delta_x))
    assert isinstance(delta_y, float), \
        'Expected float got ' + str(type(delta_y))
    return delta_x, delta_y

# ----------------------------------------------------------------------------

def calc_pixel_position(file_dict, delta_x, delta_y):
    '''
    Calculate the x and y position of the ephemeris in detector
    coordinates.
    '''
    assert isinstance(file_dict, dict), \
        'Expected dict type got ' + str(type(file_dict))
    assert isinstance(delta_x, float), \
        'Expected dict type got ' + str(type(delta_x))
    assert isinstance(delta_y, float), \
        'Expected dict type got ' + str(type(delta_y))
    ephem_x = file_dict['CRPIX1'] + delta_x
    ephem_y = file_dict['CRPIX2'] + delta_y  
    assert isinstance(ephem_x, float), \
        'Expected dict type got ' + str(type(ephem_x))
    assert isinstance(ephem_y, float), \
        'Expected dict type got ' + str(type(ephem_y))
    return ephem_x, ephem_y

# ----------------------------------------------------------------------------

def convert_coords(moon_dict):
    '''
    Convert the JPL coordinates to coords instances in degrees.
    '''
    assert isinstance(moon_dict, dict), \
            'Expected dict for moon_dict, got ' + str(type(moon_dict))
    jpl_pos = coords.Hmsdms(
        moon_dict['jpl_ra'] + ' ' + moon_dict['jpl_dec'])
    moon_dict['jpl_ra'], moon_dict['jpl_dec'] = jpl_pos._calcinternal()
    return moon_dict

#----------------------------------------------------------------------------

def get_planets_moons():
    planets_moons_list = ['jup-', 'gany-', 'sat-', 'copernicus', 'gan-', 'io-']
    pm_file = open('mtpipeline/ephem/planets_and_moons.txt', 'r')
    for pm in pm_file:
        obj = pm.split(' ')
        if len(obj) > 3:
            planets_moons_list.append(obj[1])
    return planets_moons_list

#----------------------------------------------------------------------------

def get_header_info(filename):
    '''
    Gets the header info from the FITS file. Checks to ensure that the 
    target name, after string parsing, matches a known planet name.
    '''
    assert os.path.splitext(filename)[1] == '.fits', \
        'Expected .fits got ' + filename
    header = pyfits.getheader(filename)
    output = {}
    output['targname'] = header['targname'].lower().split('-')[0]
    output['ra_targ']  = header['ra_targ']
    output['dec_targ'] = header['dec_targ']
    output['CRVAL1']   = header['CRVAL1']
    output['CRVAL2']   = header['CRVAL2']
    output['CRPIX1']   = header['CRPIX1']
    output['CRPIX2']   = header['CRPIX2']
    status = False
    for pm in planet_list:
        if pm in output['targname']:
            status = True
    assert status, \
        'Header TARGNAME not in planet_list'
    return output

#----------------------------------------------------------------------------
# The main controller for the module
#----------------------------------------------------------------------------

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

#----------------------------------------------------------------------------
# For command line execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Generate the ephemeride data.')
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
    setup_logging('build_master_finders_table')
    logging.info('Host: {0}'.format(gethostname()))
    planet_list = get_planets_moons()
    run_ephem_main(args.reproc)
