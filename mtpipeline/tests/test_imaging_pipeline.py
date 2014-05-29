#! /usr/bin/env python

from mtpipeline.imaging.imaging_pipeline import make_output_file_dict

expected_output_list = [
                            {
                            'input_file': 'u2eu0101t_c0m.fits',
                        
                            'cr_reject_output': ['u2eu0101t_c0m.fits', 'u2eu0101t_cr_c0m.fits'],
                        
                            'drizzle_output': ['u2eu0101t_c0m_wide_single_sci.fits', 'u2eu0101t_c0m_center_single_sci.fits', 'u2eu0101t_cr_c0m_wide_single_sci.fits', 'u2eu0101t_cr_c0m_center_single_sci.fits'],
                        
                            'png_output': ['u2eu0101t_c0m_wide_single_sci_log.png', 'u2eu0101t_c0m_wide_single_sci_median.png', 'u2eu0101t_c0m_center_single_sci_log.png', 'u2eu0101t_c0m_center_single_sci_median.png', 'u2eu0101t_cr_c0m_wide_single_sci_log.png', 'u2eu0101t_cr_c0m_wide_single_sci_median.png', 'u2eu0101t_cr_c0m_center_single_sci_log.png', 'u2eu0101t_cr_c0m_center_single_sci_median.png'],
                        
                            'drizzle_weight': ['u2eu0101t_c0m_wide_single_wht.fits', 'u2eu0101t_c0m_center_single_wht.fits', 'u2eu0101t_cr_c0m_wide_single_wht.fits', 'u2eu0101t_cr_c0m_center_single_wht.fits']
                            },
                            {
                            'input_file': 'u2eu0102t_c0m.fits',
                        
                            'cr_reject_output': ['u2eu0102t_c0m.fits', 'u2eu0102t_cr_c0m.fits'],
                        
                            'drizzle_output': ['u2eu0102t_c0m_wide_single_sci.fits', 'u2eu0102t_c0m_center_single_sci.fits', 'u2eu0102t_cr_c0m_wide_single_sci.fits', 'u2eu0102t_cr_c0m_center_single_sci.fits'],
                        
                            'png_output': ['u2eu0102t_c0m_wide_single_sci_log.png', 'u2eu0102t_c0m_wide_single_sci_median.png', 'u2eu0102t_c0m_center_single_sci_log.png', 'u2eu0102t_c0m_center_single_sci_median.png', 'u2eu0102t_cr_c0m_wide_single_sci_log.png', 'u2eu0102t_cr_c0m_wide_single_sci_median.png', 'u2eu0102t_cr_c0m_center_single_sci_log.png', 'u2eu0102t_cr_c0m_center_single_sci_median.png'],
                        
                            'drizzle_weight': ['u2eu0102t_c0m_wide_single_wht.fits', 'u2eu0102t_c0m_center_single_wht.fits', 'u2eu0102t_cr_c0m_wide_single_wht.fits', 'u2eu0102t_cr_c0m_center_single_wht.fits']
                            }
                        ]

def check_make_output_file_dict(expected_make_output_dict):
    
    assert make_output_file_dict(expected_make_output_dict['input_file']) == expected_make_output_dict, "expected {0} got {1}".format(expected_make_output_dict, make_output_file_dict(expected_make_output_dict['input_file']))

def test_make_output_file_dict():
    for expected_output in expected_output_list:
        yield check_make_output_file_dict, expected_output
