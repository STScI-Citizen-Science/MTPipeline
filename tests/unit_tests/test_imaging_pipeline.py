#! /usr/bin/env python

from mtpipeline.imaging.imaging_pipeline import make_output_file_dict

# A list of different input files and the resulting set of expected outputs.
expected_output_list = [
                        {'input_file': 'asdfghjkl_c0m.fits',
                        'cr_reject_output': ['asdfghjkl_c0m.fits', 
                                             'hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_c0m.fits'],

                        'drizzle_output': [ 'hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_img.fits',
                                            'hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_sci.fits'],

                        'png_output': ['png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_sci-linscale.png',
                                       'png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_img-linscale.png',
                                       'png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_sci-logscale.png',
                                       'png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_img-logscale.png'],
                        
                        'drizzle_weight': ['hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_wht.fits']

                        },

                        {'input_file': 'asdfghjkl_flt.fits',
                        'cr_reject_output': ['asdfghjkl_flt.fits', 
                                             'hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_flt.fits'],

                        'drizzle_output': [ 'hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_img.fits',
                                            'hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_sci.fits'],

                        'png_output': ['png/hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_sci-linscale.png',
                                       'png/hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_img-linscale.png',
                                       'png/hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_sci-logscale.png',
                                       'png/hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_img-logscale.png'],
                        
                        'drizzle_weight': ['hlsp_mt_hst_wfc3-uvis_asdfghjkl-mars_f606w_v1-0_wht.fits']

                        },

                        {'input_file': 'dir/asdfghjkl_c0m.fits',
                        'cr_reject_output': ['dir/asdfghjkl_c0m.fits', 
                                             'dir/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_c0m.fits'],

                        'drizzle_output': [ 'dir/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_img.fits',
                                            'dir/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_sci.fits'],

                        'png_output': ['dir/png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_sci-linscale.png',
                                       'dir/png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_img-linscale.png',
                                       'dir/png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_sci-logscale.png',
                                       'dir/png/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_img-logscale.png'],
                        
                        'drizzle_weight': ['dir/hlsp_mt_hst_wfpc2_asdfghjkl-mars_f606w_v1-0_wht.fits']

                        },
                       ]

# A list of dictionaries of metadata for each fake test file
metadata_list = [
                    {'instrument': 'WFPC2',
                     'detector' : 'WFPC2',
                     'readnoise' : None,
                     'gain' : None,
                     'targname' : 'mars',
                     'filtername': 'F606W'},

                    {'instrument': 'WFC3',
                     'detector' : 'UVIS',
                     'readnoise' : None,
                     'gain' : None,
                     'targname' : 'mars',
                     'filtername': 'F606W'},

                    {'instrument': 'WFPC2',
                     'detector' : 'WFPC2',
                     'readnoise' : None,
                     'gain' : None,
                     'targname' : 'mars',
                     'filtername': 'F606W'},
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
    for expected_output, metadata in zip(expected_output_list, metadata_list):
    
        output_dict = make_output_file_dict(
                      expected_output['input_file'],metadata)
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
