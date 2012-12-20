#! /usr/env/bin python

'''
Tests the ephem.py module
'''

import ephem
from ephem import *
import os

path_to_code = str(ephem.__file__)[:-20]
TEST_FILE = os.path.join(path_to_code, 'test-files/u40n0102m_c0m_slice_single_sci.fits')

print 'Testing with ' + TEST_FILE

def test_get_header_info():
	'''
	Test the test_get_header_info function.
	'''
	header_dict = get_header_info(TEST_FILE)
	assert header_dict['targname'] == 'neptune', 'targname should be neptune'
	assert header_dict['date_obs'] == '1997-07-03', 'date_obs should be 1997-07-03'
	assert header_dict['time_obs'] == '09:17:13', 'time_obs should be 09:17:13'
	assert header_dict['ra_targ'] == 301.1233313134, 'ra_targ should be 301.1233313134'
	assert header_dict['dec_targ'] == -19.93255391992, 'dec_targ should be -19.93255391992'
