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
from astropy.io import fits
import telnetlib
import time
import logging
import sys

from getpass import getuser
from socket import gethostname
from platform import machine
from platform import platform
from platform import architecture

from mtpipeline.database.database_tools import counter
from mtpipeline.database.database_tools import check_type

from mtpipeline.setup_logging import setup_logging

from urllib2 import urlopen

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from mtpipeline.database.database_interface import loadConnection
from mtpipeline.database.database_interface import MasterImages
from mtpipeline.database.database_interface import MasterFinders
from mtpipeline.database.database_interface import session

#----------------------------------------------------------------------------
# Low-Level Functions
#----------------------------------------------------------------------------

def cgi_session(command_list):
    '''
    Interact with NASA JPL HORIZONS via a CGI interface.

    The command_list list characters are replaced to make them URL 
    safe. The urllib2 module is used to connect. 

    *** NOTE (FROM HORIZONS) ***

    This service is in the beta test and development stage. Support 
    will only be offered to those who've been specifically invited 
    to use this tool. 
    '''
    command_list = [item.replace(' ','%20').replace(':','%3A') for item in command_list]
    url = "http://ssd.jpl.nasa.gov/horizons_batch.cgi?batch=1&COMMAND='{0[0]}'&TABLE_TYPE='{0[2]}'&CENTER='{0[3]}'&START_TIME='{0[4]}'&STOP_TIME='{0[5]}'&STEP_SIZE='{0[6]}'&QUANTITIES='{0[8]}'&CSV_FORMAT='YES'".format(command_list)
    html = urlopen(url).read()
    return html

# ----------------------------------------------------------------------------

def calc_delta(hdulist, record):
    '''
        Find the difference between the JPL coordinates at the HST
        reference pixel coordinates. Perform the difference in degrees and
        return the result in pixels.
    '''
    assert isinstance(record, dict), \
        'Expected dict got ' + str(type(record))

    crval1 = hdulist[0].header['CRVAL1']
    crval2 = hdulist[0].header['CRVAL2']

    # Convert the coordinates to coords instances in degrees.
    record = convert_coords(record)
    refpic_coords = coords.Degrees((crval1, crval2))
    crval1, crval2 = refpic_coords.a1, refpic_coords.a2

    #fits.update(filename, refpic_coords.a1, 'CRVAL1')
    #fits.update(filename, refpic_coords.a2, 'CRVAL2')
    
    # Take the difference and convert to pixels.
    # RA increases to the East (left) so we switch the sign on the delta.
    delta_x = -1 * (record['jpl_ra'] - crval1) * (3600. / 0.05)
    delta_y = (record['jpl_dec'] - crval2) * (3600. / 0.05)

    assert isinstance(delta_x, float), \
        'Expected float got ' + str(type(delta_x))
    assert isinstance(delta_y, float), \
        'Expected float got ' + str(type(delta_y))
    return delta_x, delta_y

# ----------------------------------------------------------------------------

def calc_pixel_position(hdulist, delta_x, delta_y):
    '''
        Calculate the x and y position of the ephemeris in detector
        coordinates.
    '''
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

#----------------------------------------------------------------------------

def convert_coords(moon_dict):
    '''
        Convert the JPL coordinates to coords instances in degrees.
    '''
    assert isinstance(moon_dict, dict), \
        'Expected dict for moon_dict, got ' + str(type(moon_dict))
    jpl_pos = coords.Hmsdms(moon_dict['jpl_ra'] + ' ' + moon_dict['jpl_dec'])
    moon_dict['jpl_ra'], moon_dict['jpl_dec'] = jpl_pos._calcinternal()
    return moon_dict

#----------------------------------------------------------------------------

def planets_moons_list():
    '''
       Returns list of planets and moons.
    '''
    pm_list = ['jup-', 'gany-', 'sat-', 'copernicus', 'gan-', 'io-']
    pm_file = open('mtpipeline/ephem/planets_and_moons.txt', 'r')
    for pm in pm_file:
        obj = pm.split(' ')
        if len(obj) > 3:
            pm_list.append(obj[1])
    return pm_list

# ----------------------------------------------------------------------------

def get_header_info(hdulist):
    '''
        Gets the header info from the FITS file. Checks to ensure that the
        target name, after string parsing, matches a known planet name.
    '''
    output = {}
    output['targname'] = hdulist[0].header['targname'].lower().split('-')[0]
    output['date_obs'] = hdulist[0].header['date-obs']
    output['time_obs'] = hdulist[0].header['time-obs']
    status = False
    for pm in PLANETS_MOONS:
        if pm in output['targname']:
            status = True
    assert status, \
        'Header TARGNAME not in planet_list'
    return output

def update_record(hdulist, moon_dict, master_images_id, nome):
    '''
    Update a record in the master_finders table.
    '''
    update_dict = {}
    delta_x, delta_y = calc_delta(hdulist, moon_dict)
    ephem_x, ephem_y = calc_pixel_position(hdulist, delta_x, delta_y)
    update_dict['ephem_x'] = int(ephem_x)
    update_dict['ephem_y'] = int(ephem_y)

    session.query(MasterFinders).filter(\
        MasterFinders.master_images_id == master_images_id, 
        MasterFinders.object_name == nome).update(update_dict)
    session.commit()

def ephem_main(filename, nome):
    '''
    The main controller. 
    '''
    # Get the unique record from the master_images table.
    assert filename[-5:] == '.fits', \
        'Expected .fits got ' + filename
    master_images_query = session.query(MasterImages).filter(\
        MasterImages.fits_file == os.path.basename(filename)).one()
    hdulist = fits.open(filename)

    mf = session.query(MasterFinders).filter(MasterFinders.master_images_id == master_images_query.id).filter(MasterFinders.object_name == nome).one()

    moon_dict = {'jpl_ra': mf.jpl_ra,
                'jpl_dec': mf.jpl_dec}

    update_record(hdulist, moon_dict, master_images_query.id, nome)

    
if __name__ == '__main__':
    
    mm = session.query(MasterFinders).\
            filter(MasterFinders.ephem_x == None).\
            group_by(MasterFinders.object_name).all()

    for nome in mm:
        
        ob_nome = nome.object_name
        
        PLANETS_MOONS = planets_moons_list()

        master_finders_query = session.query(MasterImages).\
                            outerjoin(MasterFinders).\
                            filter(MasterFinders.object_name == ob_nome).\
                            filter(MasterFinders.ephem_x == None).all()
        filelist = [os.path.join(record.file_location[:-4], record.fits_file) \
                for record in master_finders_query]

        print 'Processing ' + str(len(filelist)) + ' files.'

        for filename in filelist:
            ephem_main(filename, ob_nome)
            print 'Completed for: ' + filename

    session.close()
