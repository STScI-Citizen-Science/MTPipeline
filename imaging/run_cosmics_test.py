#! /usr/bin/env python

'''
Test module for the run_cosmics.py module.
'''

import os
from run_cosmics import make_c1m_link  

def teardown():
    query = os.access('u2eu0101f_cr_c1m.fits', os.F_OK)
    if query == True:
        os.remove('u2eu0101f_cr_c1m.fits')


def make_c1m_link_test():
    '''
    Test the make_c1m_link function. Uses a cleanup function to remove
    the link.
    '''
    make_c1m_link('u2eu0101f_c0m.fits')

