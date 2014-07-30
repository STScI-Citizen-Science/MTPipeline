#! /usr/bin/env python

from mtpipeline.imaging.imaging_pipeline import make_output_file_dict

expected_output_list = [
                        {'input_file': 'u2eu0101t_c0m.fits',
                        'cr_reject_output': ['u2eu0101t_c0m.fits', 'u2eu0101t_cr_c0m.fits'],
                        'drizzle_output': ['u2eu0101t_c0m_wide_single_sci.fits',
                                           'u2eu0101t_c0m_center_single_sci.fits',
                                           'u2eu0101t_cr_c0m_wide_single_sci.fits',
                                           'u2eu0101t_cr_c0m_center_single_sci.fits'],
                        'png_output': ['png/u2eu0101t_c0m_wide_single_sci_linear.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_1.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_2.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_3.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_4.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_5.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_6.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_7.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_8.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_9.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_10.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_11.png',
                                       'png/u2eu0101t_c0m_wide_single_sci_linear_12.png',
                                       'png/u2eu0101t_c0m_center_single_sci_linear.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_1.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_2.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_3.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_4.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_5.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_6.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_7.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_8.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_9.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_10.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_11.png',
                                       'png/u2eu0101t_cr_c0m_wide_single_sci_linear_12.png',
                                       'png/u2eu0101t_cr_c0m_center_single_sci_linear.png'],
                        'drizzle_weight': ['u2eu0101t_c0m_wide_single_wht.fits',
                                           'u2eu0101t_c0m_center_single_wht.fits',
                                           'u2eu0101t_cr_c0m_wide_single_wht.fits',
                                           'u2eu0101t_cr_c0m_center_single_wht.fits']},
                        {'input_file': 'u2eu0101t_flt.fits',
                        'cr_reject_output': ['u2eu0101t_flt.fits', 'u2eu0101t_cr_flt.fits'],
                        'drizzle_output': ['u2eu0101t_wide_single_sci.fits',
                                           'u2eu0101t_center_single_sci.fits',
                                           'u2eu0101t_cr_wide_single_sci.fits',
                                           'u2eu0101t_cr_center_single_sci.fits'],
                        'png_output': ['png/u2eu0101t_wide_single_sci_linear.png',
                                       'png/u2eu0101t_wide_single_sci_linear_1.png',
                                       'png/u2eu0101t_wide_single_sci_linear_2.png',
                                       'png/u2eu0101t_wide_single_sci_linear_3.png',
                                       'png/u2eu0101t_wide_single_sci_linear_4.png',
                                       'png/u2eu0101t_wide_single_sci_linear_5.png',
                                       'png/u2eu0101t_wide_single_sci_linear_6.png',
                                       'png/u2eu0101t_wide_single_sci_linear_7.png',
                                       'png/u2eu0101t_wide_single_sci_linear_8.png',
                                       'png/u2eu0101t_wide_single_sci_linear_9.png',
                                       'png/u2eu0101t_wide_single_sci_linear_10.png',
                                       'png/u2eu0101t_wide_single_sci_linear_11.png',
                                       'png/u2eu0101t_wide_single_sci_linear_12.png',
                                       'png/u2eu0101t_center_single_sci_linear.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_1.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_2.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_3.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_4.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_5.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_6.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_7.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_8.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_9.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_10.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_11.png',
                                       'png/u2eu0101t_cr_wide_single_sci_linear_12.png',
                                       'png/u2eu0101t_cr_center_single_sci_linear.png'],
                        'drizzle_weight': ['u2eu0101t_wide_single_wht.fits',
                                           'u2eu0101t_center_single_wht.fits',
                                           'u2eu0101t_cr_wide_single_wht.fits',
                                           'u2eu0101t_cr_center_single_wht.fits']}
                        ]

def check_output_entry(output_entry,expected_entry):
    """ Checking if the entries in the output dictionary (lists, save
    for the input filename) are identiical to those in the expected,
    manually specified, dictionary.
        
    Parameters:
        input: output_entry
            The entry in the output dictionary accessed by a particular
            key. Either a string or list.
               expected_filename
            The entry in the manually specified, expected dictionary
            for that same key. Either a string or list.
        
    Returns:
        nothing
    
    Output:
        output: string
            "Ok" if test passed.
            Error message if any test failed.
    
    """

    err_message = "\n expected: \n {0} \n got: \n {1}"
    err_message = err_message.format(expected_entry, output_entry)

    assert expected_entry == output_entry, err_message

def check_output_keys(output_keys,expected_keys):
    """ Check if the keys of the output dictionary are identiical to
        those in the expected, manually specified, dictionary.
        
    Parameters:
        input: output_keys (list)
            The keys of the output dictionary.
               expected_keys (list)
            The keys of the dictionary we specify by hand.
            
    Returns:
        nothing
    
    Output:
        output: string
            "Ok" if test passed.
            Error message if any test failed.
    
    """

    err_message = "\n expected keys: \n {0} \n output keys: \n {1} \n \
    If this test fails, others will produce ERRORs."
    err_message = err_message.format(expected_keys, output_keys)
    assert output_keys == expected_keys, err_message

def test_make_output_file_dict():
    """ 
    Iteratively generating tests.
    
    Six tests are generated per dictionary in expected_entry_list.
    Each dictionary represents a particular case, each corresponding
    to a particular input filename.
    
    Parameters:
        nothing
    
    Returns:
        nothing
    
    Output:
        nothing
    
    """
    
    # Go through each test case (different input filenames):
    for expected_output in expected_output_list:
    
        output_dict = make_output_file_dict(
                      expected_output['input_file'])
        expected_keys = expected_output.keys()
        output_keys = output_dict.keys()

        # Test to make sure all the keys are the same.
        yield check_output_keys, output_keys, expected_keys
        
        for key in expected_keys:
            expected_entry = expected_output[key]
            output_entry = output_dict[key]
            
            # Test to make sure the entries for each key are the
            # same.
            yield check_output_entry, output_entry, expected_entry
  

if __name__ == "__main__":
    test_make_output_file_dict()
