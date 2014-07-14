"""Nosetest unit test module for build_master_images_table.py

This module creates an in-memory sqlite3 database to perform the tests.

Currently this module is a bit of a mess but it runs. 

Authors:
    Alex Viana, July 2014

Use:
    >>> nosetests test_build_master_images_table.py
"""

from mtpipeline.database.database_interface import loadConnection
from mtpipeline.database.database_interface import MasterImages

import os

session, Base, engine = loadConnection('sqlite:///:memory:', echo=True)

header = {}
header['proposid'] = 6741
header['targname'] = 'MARS-CML345'
header['NAXIS1'] = 450
header['NAXIS2'] = 450
header['RA_TARG'] = 183.540921043
header['DEC_TARG'] = -1.29559572252
header['FILTNAM1'] = 'F255W'
header['LINENUM'] = '19.821'

max_set_id = 0
existing_set_dict = {}
path = '/astro/mtpipeline/mtpipeline_outputs/wfpc2/06741_mars/'
fits_file = os.path.join(path, 'u3gi8201m_c0m_center_single_sci.fits')
png_file = os.path.join(path, 'png/u3gi8201m_c0m_center_single_sci_linear.png')
mi = MasterImages(header, fits_file, png_file)
existing_set_dict, max_set_id = mi.set_set_values(existing_set_dict, max_set_id)

true_dict = {
    'project_id':6741,
    'name':'u3gi8201m_c0m_center_single_sci_linear.png', 
    'fits_file':'u3gi8201m_c0m_center_single_sci.fits', 
    'object_name':'MARS-CML345', 
    'set_id':1,
    'set_index':1,
    'width':450,
    'height':450,
    'minimum_ra':183.53508771,
    'minimum_dec':-1.30149155585133,
    'maximum_ra':183.54133771,
    'maximum_dec':-1.29524155585133,
    'pixel_resolution':0.05,
    'description':'F255W',
    'file_location':'/astro/mtpipeline/mtpipeline_outputs/wfpc2/06741_mars/png',
    'visit':'19',
    'orbit':'821', 
    'drz_mode':'center',
    'cr_mode':'no_cr'} 


def check_value(test_value, true_value, name):
    try:
        test_value = round(test_value, 9)       
        true_value = round(true_value, 9)   
    except:
        pass
    error_string = 'expected {} for {} got {} instead'.format(
        true_value, name, test_value)
    assert test_value == true_value, error_string


def test_foo():
    for key in true_dict:
        yield check_value, getattr(mi, key), true_dict[key], key
