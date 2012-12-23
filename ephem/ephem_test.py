#! /usr/env/bin python

'''
Tests the ephem.py module
'''

import datetime
import ephem
from ephem import *
import os

path_to_code = str(ephem.__file__)[:-20]
TEST_FILE = os.path.join(path_to_code, 'test-files/u40n0102m_c0m_slice_single_sci.fits')
print 'Testing with ' + TEST_FILE

class test_ephem(object):

    def test_get_header_info(self):
        '''
        Test the test_get_header_info function.
        '''
        header_dict = get_header_info(TEST_FILE)
        assert header_dict['targname'] == 'neptune', 'targname should be neptune'
        assert header_dict['date_obs'] == '1997-07-03', 'date_obs should be 1997-07-03'
        assert header_dict['time_obs'] == '09:17:13', 'time_obs should be 09:17:13'
        assert header_dict['ra_targ'] == 301.1233313134, 'ra_targ should be 301.1233313134'
        assert header_dict['dec_targ'] == -19.93255391992, 'dec_targ should be -19.93255391992'

    def test_convert_datetime(self):
        '''
        Tests the test_convert_datetime function.
        '''
        header_dict = get_header_info(TEST_FILE)
        header_dict = convert_datetime(header_dict)
        assert header_dict['header_time'] == datetime.datetime(1997, 7, 3, 9, 17, 13), 'header_time should be datetime.datetime(1997, 7, 3, 9, 17, 13)'
        assert header_dict['horizons_start_time'] == '1997-Jul-03 09:17', 'horizons_start_time should be 1997-Jul-03 09:17'
        assert header_dict['horizons_end_time'] == '1997-Jul-03 09:18', 'horizons_end_time should be 1997-Jul-03 09:18'

    def test_make_moon_dict(self):
        '''
        Tests the make_moon_dict function.
        '''
        header_dict = get_header_info(TEST_FILE)
        header_dict = convert_datetime(header_dict)
        moon_dict = make_moon_dict(TEST_FILE, header_dict)
        assert moon_dict['triton'] == {'id': '801'}, 'unexpected value in moon_dict'
        assert moon_dict['nereid'] ==  {'id': '802'}, 'unexpected value in moon_dict'
        assert moon_dict['psamathe'] ==  {'id': '810'}, 'unexpected value in moon_dict'
        assert moon_dict['sao'] ==  {'id': '811'}, 'unexpected value in moon_dict'
        assert moon_dict['thalassa'] ==  {'id': '804'}, 'unexpected value in moon_dict'
        assert moon_dict['laomedeia'] ==  {'id': '812'}, 'unexpected value in moon_dict'
        assert moon_dict['naiad'] ==  {'id': '803'}, 'unexpected value in moon_dict'
        assert moon_dict['halimede'] ==  {'id': '809'}, 'unexpected value in moon_dict'
        assert moon_dict['despina'] ==  {'id': '805'}, 'unexpected value in moon_dict'
        assert moon_dict['neso'] ==  {'id': '813'}, 'unexpected value in moon_dict'
        assert moon_dict['proteus'] ==  {'id': '808'}, 'unexpected value in moon_dict'
        assert moon_dict['galatea'] ==  {'id': '806'}, 'unexpected value in moon_dict'
        assert moon_dict['larissa'] ==  {'id': '807'}, 'unexpected value in moon_dict'