#! /usr/bin/env python

'''
Test module for the run_cosmics.py module.
'''

import os
from run_cosmicx import make_c1m_link  

def setup():
    query = os.path.islink('u2eu0101f_cr_c1m.fits')
    if query == True:
        os.remove('u2eu0101f_cr_c1m.fits')

def teardown():
    query = os.path.islink('u2eu0101f_cr_c1m.fits')
    if query == True:
        os.remove('u2eu0101f_cr_c1m.fits')

def make_c1m_link_test():
    '''
    Test the make_c1m_link function. Uses a cleanup function to remove
    the link.
    '''
    make_c1m_link('u2eu0101f_c0m.fits')
    assert os.path.islink('u2eu0101f_cr_c1m.fits'), 'Link does not exist.'

