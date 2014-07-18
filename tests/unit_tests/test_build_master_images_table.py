"""Nosetest unit test module for build_master_images_table.py

This module creates an in-memory sqlite3 database to perform the tests.

Authors:
    Alex Viana, July 2014

Use:
    >>> nosetests test_build_master_images_table.py
"""

from mtpipeline.database.database_interface import loadConnection
from mtpipeline.database.database_interface import MasterImages

import os

# This is required to run the tests on the Travis server
#session, Base, engine = loadConnection('sqlite:///:memory:', echo=True)

# Create common header dictionary to serve as a mock hdu.header object 
# for the tests.
header = {
    'proposid':6741,
    'targname':'MARS-CML345',
    'NAXIS1':450,
    'NAXIS2':450,
    'RA_TARG':183.540921043,
    'DEC_TARG':-1.29559572252,
    'FILTNAM1':'F255W',
    'LINENUM':'19.821'}

# This dictionary tests the case where there are 4 images that have
# the same rootname but different cr and drz setting so they should 
# have different set_id's each with a set_index of 1. 
test_1_dict = {
    'fits_file_list':[
        'u3gi8201m_c0m_center_single_sci.fits',
        'u3gi8201m_c0m_wide_single_sci.fits',
        'u3gi8201m_cr_c0m_center_single_sci.fits',
        'u3gi8201m_cr_c0m_wide_single_sci.fits'],
    'u3gi8201m_c0m_center_single_sci.fits':{
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
        'cr_mode':'no_cr'},
    'u3gi8201m_c0m_wide_single_sci.fits':{
        'project_id':6741,
        'name':'u3gi8201m_c0m_wide_single_sci_linear.png', 
        'fits_file':'u3gi8201m_c0m_wide_single_sci.fits', 
        'object_name':'MARS-CML345', 
        'set_id':2,
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
        'drz_mode':'wide',
        'cr_mode':'no_cr'},
    'u3gi8201m_cr_c0m_center_single_sci.fits':{
        'project_id':6741,
        'name':'u3gi8201m_cr_c0m_center_single_sci_linear.png', 
        'fits_file':'u3gi8201m_cr_c0m_center_single_sci.fits', 
        'object_name':'MARS-CML345', 
        'set_id':3,
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
        'cr_mode':'cr'},
    'u3gi8201m_cr_c0m_wide_single_sci.fits':{
        'project_id':6741,
        'name':'u3gi8201m_cr_c0m_wide_single_sci_linear.png', 
        'fits_file':'u3gi8201m_cr_c0m_wide_single_sci.fits', 
        'object_name':'MARS-CML345', 
        'set_id':4,
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
        'drz_mode':'wide',
        'cr_mode':'cr'}}

# This dictionary tests the case where there are 4 images that should 
# have the same set_id and thus an incimenting set_index.
test_2_dict = {
    'fits_file_list':[
        'u3gi8201m_c0m_center_single_sci.fits',
        'u3gi8202m_c0m_center_single_sci.fits',
        'u3gi8203m_c0m_center_single_sci.fits',
        'u3gi8204m_c0m_center_single_sci.fits'],
    'u3gi8201m_c0m_center_single_sci.fits':{
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
        'cr_mode':'no_cr'},
    'u3gi8202m_c0m_center_single_sci.fits':{
        'project_id':6741,
        'name':'u3gi8202m_c0m_center_single_sci_linear.png', 
        'fits_file':'u3gi8202m_c0m_center_single_sci.fits', 
        'object_name':'MARS-CML345', 
        'set_id':1,
        'set_index':2,
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
        'cr_mode':'no_cr'},    
    'u3gi8203m_c0m_center_single_sci.fits':{
        'project_id':6741,
        'name':'u3gi8203m_c0m_center_single_sci_linear.png', 
        'fits_file':'u3gi8203m_c0m_center_single_sci.fits', 
        'object_name':'MARS-CML345', 
        'set_id':1,
        'set_index':3,
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
        'cr_mode':'no_cr'},    
    'u3gi8204m_c0m_center_single_sci.fits':{
        'project_id':6741,
        'name':'u3gi8204m_c0m_center_single_sci_linear.png', 
        'fits_file':'u3gi8204m_c0m_center_single_sci.fits', 
        'object_name':'MARS-CML345', 
        'set_id':1,
        'set_index':4,
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
        'cr_mode':'no_cr'}}

test_dict_list = [test_1_dict, test_2_dict]

def check_value(test_value, true_value, name, filename):
    """Runs the acutal assert statement used for testing. 

    This function is designed to be called by a yield statement in the 
    test function so that every `assert` counts as a seperate test. 
    This pattern is described in the `nosetests` docs: 
    https://nose.readthedocs.org/en/latest/writing_tests.html#test-generators

    Also, because floats representation is inherantly inaccurate 
    all float values are rounded to the 9th decimal place to allow 
    comparison. 

    Parameters: 
        test_value : object
            The value being tested.
        true_value : object 
            The expected value for `test_value`.
        name : str
            The sting name for the value being tested. Used to build a 
            descrptive error message if the assert failes.
        filename : str
            The filename of the test being run. Used to build a 
            descrptive error message if the assert failes.

    Returns:
        nothing 
    """
    float_list = ['minimum_ra', 'minimum_dec', 'maximum_ra','maximum_dec']
    if name in float_list:
        test_value = round(test_value, 9)       
        true_value = round(true_value, 9)   
    error_string = '{}: expected {} for {} got {} instead'.format(
        filename, true_value, name, test_value)
    assert test_value == true_value, error_string


def test_build_master_images_table():
    """Nosetests testing function.

    This function iterates over the test_dict_list list created at the 
    module level of of this module to generate the values for testing.

    This pattern is described in the `nosetests` docs: 
    https://nose.readthedocs.org/en/latest/writing_tests.html#test-generators

    Parameters: 
        nothing

    Returns: 
        nothing

    Yields:
        check_value : function
            Yields instances of the check_value function so that each 
            assert will count as a seperate test. 
    """
    for test_dict in test_dict_list:

        # Set the non-file specific variables for this set of tests.
        max_set_id = 0
        existing_set_dict = {}
        path = '/astro/mtpipeline/mtpipeline_outputs/wfpc2/06741_mars/'
        fits_file_list = test_dict['fits_file_list']

        # Build the MasterImages instance for each test iteration. 
        for fits_file in fits_file_list:
            fits_file = os.path.join(path, fits_file)
            png_file = fits_file.replace('.fits','_linear.png')
            png_file = os.path.join(path, 'png', os.path.basename(png_file))
            mi = MasterImages(header, fits_file, png_file)
            existing_set_dict, max_set_id = mi.set_set_values(existing_set_dict, max_set_id)

            # Run the tests. 
            true_dict = test_dict[os.path.basename(fits_file)]
            for key in true_dict:
                yield (check_value, getattr(mi, key), true_dict[key], key, 
                       os.path.basename(fits_file))
