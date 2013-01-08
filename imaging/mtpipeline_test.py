#! /usr/bin/env python

'''
Nosetest module for imaging/mtpipeline.py
'''

from mtpipeline import make_output_file_dict

def make_output_file_dict_test():
    '''
    Test the make_output_file_dict function. First generate the test 
    dictionary, then a dictionary of expected results, and finally
    compare them.
    '''
    # Generate the test dictionary.
    test_result = make_output_file_dict('u2eu0101f_c0m.fits')

    # Generated the dictionary of expected results.
    desired_result = {}
    desired_result['input_file'] = 'u2eu0101f_c0m.fits'
    desired_result['cr_reject_output'] = ['u2eu0101f_c0m.fits', 'u2eu0101f_cr_c0m.fits']
    desired_result['drizzle_output'] = ['u2eu0101f_c0m_wide_single_sci.fits', 
        'u2eu0101f_c0m_center_single_sci.fits', 'u2eu0101f_cr_c0m_wide_single_sci.fits', 
        'u2eu0101f_cr_c0m_center_single_sci.fits'], 
    
    # Compare the dictionaries.
    assert desired_result['input_file'] == test_result['input_file'], \
        'Unexpected value in input_file.' 
    assert desired_result['cr_reject_output'] == test_result['cr_reject_output'], \
        'Unexpected value in cr_reject_output.'     
    assert desired_result['drizzle_output'] == test_result['drizzle_output'], \
        'Unexpected value in drizzle_output.' 
