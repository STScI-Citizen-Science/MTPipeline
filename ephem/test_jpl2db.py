'''
Nosetest testing suite for the jpl2db module.
'''

from database_interface import check_type

from jpl2db import telnet_session
from jpl2db import cgi_session
from jpl2db import parse_jpl_telnet
from jpl2db import parse_jpl_cgi

COMMAND_LIST = ['899',
    'e', 'o', 'geo',
    '1997-Jul-03 09:17',
    '1997-Jul-03 09:18',
    '1m', 'y','1,2,3,4', 'n']


def test_cgi_connection():
    '''
    Tests the functionality of the CGI connection to NASA JPL by 
    checking the output dictionary.
    '''
    jpl_data = cgi_session(COMMAND_LIST)
    jpl_data = parse_jpl_cgi(jpl_data)
    check_values(jpl_data)


def test_telnet_connection():
    '''
    Tests the functionality of the TELNET connection to NASA JPL by 
    checking the output dictionary.
    '''
    jpl_data = telnet_session(COMMAND_LIST)
    jpl_data = parse_jpl_telnet(jpl_data)
    check_values(jpl_data)


def check_values(data):
    '''
    Checks the returned values.
    '''
    check_type(data, dict)
    assert data['date'] == '1997-Jul-03 09:17'
    assert data['jpl_dec'] == '-19:55:57.3'
    assert data['jpl_dec_apparent'] == '-19:56:11.1'
    assert data['jpl_dec_delta'] == '-0.80270'
    assert data['jpl_ra'] == '20:04:29.56'
    assert data['jpl_ra_apparent'] == '20:04:21.95'
    assert data['jpl_ra_delta'] == '-3.74238'