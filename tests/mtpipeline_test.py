#! /usr/bin/env python

'''
Nosetest module for imaging/mtpipeline.py
'''

import os
from mtpipeline import check_for_outputs
from mtpipeline import make_output_file_dict


def make_desired_result():
    '''
    Generated the dictionary of expected results.
    '''
    desired_result = {}
    desired_result['input_file'] = 'test_path/u2eu0101f_c0m.fits'
    cr_reject_list = ['test_path/u2eu0101f_c0m.fits', 
        'test_path/u2eu0101f_cr_c0m.fits']
    desired_result['cr_reject_output'] = cr_reject_list
    drizzle_list = ['test_path/u2eu0101f_c0m_wide_single_sci.fits', 
        'test_path/u2eu0101f_c0m_center_single_sci.fits',
        'test_path/u2eu0101f_cr_c0m_wide_single_sci.fits', 
        'test_path/u2eu0101f_cr_c0m_center_single_sci.fits']
    desired_result['drizzle_output'] = drizzle_list
    drizzle_weight_list = ['test_path/u2eu0101f_c0m_wide_single_wht.fits', 
        'test_path/u2eu0101f_c0m_center_single_wht.fits',
        'test_path/u2eu0101f_cr_c0m_wide_single_wht.fits', 
        'test_path/u2eu0101f_cr_c0m_center_single_wht.fits']
    desired_result['drizzle_weight'] = drizzle_weight_list
    png_output_list = ['test_path/u2eu0101f_c0m_wide_single_sci_log.png', 
        'test_path/u2eu0101f_c0m_center_single_sci_log.png',
        'test_path/u2eu0101f_cr_c0m_wide_single_sci_log.png', 
        'test_path/u2eu0101f_cr_c0m_center_single_sci_log.png',
        'test_path/u2eu0101f_c0m_wide_single_sci_median.png', 
        'test_path/u2eu0101f_c0m_center_single_sci_median.png',
        'test_path/u2eu0101f_cr_c0m_wide_single_sci_median.png', 
        'test_path/u2eu0101f_cr_c0m_center_single_sci_median.png']
    desired_result['png_output'] = png_output_list
    return desired_result


def make_output_file_dict_test():
    '''
    Test the make_output_file_dict function. First generate the test 
    dictionary, then a dictionary of expected results, and finally
    compare them.

    Comparing is done by first checking that both dicts have the same
    keys. To avoid the issue of the lists in each value being in 
    a different order they are first compared in length and then a set
    object constructed from each dict value is compared. 
    '''
    # Generate the dictionaries.
    test_result = make_output_file_dict('test_path/u2eu0101f_c0m.fits')
    desired_result = make_desired_result()
    assert test_result.keys() == desired_result.keys(), \
        'Dict keys are not the same: ' + str(test_result.keys()) + ' ' + \
            str(desired_result.keys())
    for key in desired_result.keys():
        assert len(desired_result) == len(test_result), \
            'Dict values are not the same lenght'
        assert set(desired_result[key]) == set(test_result[key]), \
            'Sets of the dict values are not the same.'


class TestCheckForOutputs(object):
    '''
    Tests for the check_for_outputs function. The setup and teardown 
    methods create and remove the files the function will test for.
    '''
    def __init__(self):
        '''
        Creare the filename_dict and path attribues for use by all the 
        other methods.
        '''
        self.filename_dict = make_desired_result()
        self.path = os.path.split(self.filename_dict['input_file'])[0]

    def make_file(self, filename):
        '''
        Create an empty dummy file.
        '''
        file_object = open(filename, 'w')
        file_object.close()

    def setup(self):
        '''
        Make the 'test_path' folder and dummy files for all the 
        test files.
        '''
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        for value in self.filename_dict.itervalues():
            if isinstance(value, str):
                self.make_file(value)
            elif isinstance(value, list):
                for item in value:
                    self.make_file(item)

    def test_check_for_outputs_true(self):
        '''
        Test for files that exist.
        '''
        for value in self.filename_dict.itervalues():
            query = check_for_outputs(value)
            assert query == True, 'Exepected True for ' + str(value)

    def test_check_for_outputs_false(self):
        '''
        Test for files that don't exist.
        '''
        for value in self.filename_dict.itervalues():
            if isinstance(value, list):
                value.append('does_not_exist.txt')
            elif isinstance(value, str):
                value = 'does_not_exist.txt'
            query = check_for_outputs(value)
            assert query == False, 'Exepected False for ' + str(value)

    def teardown(self):
        '''
        Clean up all the test files.
        '''
        for filename in os.listdir(self.path):
            os.remove(os.path.join(self.path, filename))
        os.removedirs(self.path)