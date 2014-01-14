#! /usr/bin/env python

'''
Calculate the ephemeride positions in pixels from the infomation in 
the FITS file and the database. Write the results back to the database.
'''

import argparse
import coords
import glob
import os
import pyfits

#from build_master_table import get_fits_file

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database.database_interface import counter
from database.database_interface import session
from database.database_interface import MasterImages
from database.database_interface import MasterFinders

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

def get_header_info(filename):
    '''
    Gets the header info from the FITS file. Checks to ensure that the 
    target name, after string parsing, matches a known planet name.
    '''
    assert os.path.splitext(filename)[1] == '.fits', \
        'Expected .fits got ' + filename
    output = {}
    output['targname'] = pyfits.getval(filename, 'targname').lower().split('-')[0]
    output['ra_targ']  = pyfits.getval(filename, 'ra_targ')
    output['dec_targ'] = pyfits.getval(filename, 'dec_targ')
    output['CRVAL1']   = pyfits.getval(filename, 'CRVAL1')
    output['CRVAL2']   = pyfits.getval(filename, 'CRVAL2')
    output['CRPIX1']   = pyfits.getval(filename, 'CRPIX1')
    output['CRPIX2']   = pyfits.getval(filename, 'CRPIX2')
    planet_list = ['mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    assert output['targname'] in planet_list, \
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
    #print 'Processing ' + str(len(file_list)) + ' files.'
    count = 0
    query_list = session.query(MasterFinders, MasterImages).\
        join(MasterImages).\
        options(subqueryload('master_images_rel')).\
        filter(or_(MasterFinders.jpl_ra != None, MasterFinders.jpl_dec != None)).\
        all()

    print 'Processing ' + str(len(query_list)) + ' files.' 
    for record in query_list:
        if record.MasterFinders.ephem_x == None \
                or record.MasterFinders.ephem_y == None \
                or reproc == True:
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
        count = counter(count)
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
    run_ephem_main(args.reproc)
