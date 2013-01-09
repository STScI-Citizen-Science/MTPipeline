#! /usr/bin/env python

'''
Nosetest module for imaging/mtpipeline.py
'''

from mtpipeline import make_output_file_dict

def make_desired_result():
    '''
    Generated the dictionary of expected results.
    '''
    desired_result = {}
    desired_result['input_file'] = 'test_path/u2eu0101f_c0m.fits'
    desired_result['cr_reject_output'] = ['test_path/u2eu0101f_c0m.fits', 
        'test_path/u2eu0101f_cr_c0m.fits']
    desired_result['drizzle_output'] = ['test_path/u2eu0101f_c0m_wide_single_sci.fits', 
        'test_path/u2eu0101f_c0m_center_single_sci.fits', 
        'test_path/u2eu0101f_cr_c0m_wide_single_sci.fits', 
        'test_path/u2eu0101f_cr_c0m_center_single_sci.fits'] 
    return desired_result


def make_output_file_dict_test():
    '''
    Test the make_output_file_dict function. First generate the test 
    dictionary, then a dictionary of expected results, and finally
    compare them.
    '''
    # Generate the dictionaries.
    test_result = make_output_file_dict('test_path/u2eu0101f_c0m.fits')
    desired_result = make_desired_result()

    # Compare the input_file keys.
    assert desired_result['input_file'] == test_result['input_file'], \
        '\nExpected: ' + desired_result['input_file'] + '\nGot:' + test_result['input_file']
    
    # Compare the cr_rejected keys.
    for desired_item, test_item in \
            zip(desired_result['cr_reject_output'], test_result['cr_reject_output']): 
        assert desired_item == test_item, \
            '\nExpected: ' + str(desired_item) + '\nGot: ' + str(test_item)
    
    # Compare for drizzled_outputs.
    for desired_item, test_item in \
            zip(desired_result['drizzle_output'], test_result['drizzle_output']):
        assert desired_item == test_item, \
            '\nExpected: ' + str(desired_item) + '\nGot: ' + str(test_item)