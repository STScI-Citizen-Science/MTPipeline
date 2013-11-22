'''
Nose tests for the run_trim.py module.
'''

from run_trim import get_value_by_pixel_count
from run_trim import clip
from run_trim import positive 
import numpy as N 

class test_get_value_by_pixel_count(object):
    '''
    Test for the get_value_by_pixel_count function from run_trim.     
    '''
    def __init__(self):
        self.input_array = N.resize(range(9),(3,3))
    
    def bottom_test(self):
        '''
        Test that the value of the 2nd pixel from the bottom is 1.
        '''
        bottom_test_result = get_value_by_pixel_count(self.input_array, 2, 'bottom')
        error = 'bottom_test gave ' + str(bottom_test_result) + ' expected 2.'
        assert bottom_test_result == 1, error
    
    def top_test(self):
        '''
        Test that the value of the 2nd pixel from the top is 7.
        '''
        top_test_result = get_value_by_pixel_count(self.input_array, 7, 'top')
        error = 'top_test gave ' + str(top_test_result) + ' expected 7.'
        assert top_test_result == 7, error

class test_clip(object):
    '''
    Test for the clip function in run_trim.
    '''
    def __init__(self): 
        self.input_array = N.resize(range(100),(10,10))

    def bottom_test(self):
        '''
        Test that the bottom 10 pixels are rescaled to 9.
        '''
        bottom_test_result = clip(self.input_array, 9.0, 'bottom')
        bottom_test_result = N.sum(bottom_test_result == 9)
        error = 'test_clip.bottom_test got ' + str(bottom_test_result) + ' expected 10'
        assert bottom_test_result == 10, error

    def top_test(self):
        '''
        Test that the top 10 pixels are rescaled to 90.
        '''
        top_test_result = clip(self.input_array, 90.0, 'top')
        top_test_result = N.sum(top_test_result == 90)
        error = 'test_clip.bottom_test got ' + str(top_test_result) + ' expected 10'
        assert top_test_result == 10, error

class test_positive(object):
    '''
    Test for the positive function in run_trim. Because it's hard 
    (impossible?) to exactly match two floats we look at the detla.
    '''
    def __init__(self):
        #self.input_array = N.resize(range(-99,1),(10,10))
        self.input_array = N.array([-1,0])

    def positive_test(self):
        result = positive(self.input_array)
        expected = N.array([0,1]) + 0.0001
        difference = round(abs(N.sum(result - expected)))
        assert difference == 0, 'positive is not working.'