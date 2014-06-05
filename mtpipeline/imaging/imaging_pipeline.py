#! /usr/bin/env python

'''
This is the main module for the Moving Target Pipeline.

Alex C. Viana
viana@stsci.edu
'''

# Standard packages
import argparse
import glob
import logging
import os
import sys
from datetime import datetime
from getpass import getuser
from socket import gethostname
from platform import machine
from platform import platform
from platform import architecture
from stwcs import updatewcs

# Custom Packages
from mtpipeline.imaging.run_cosmics import run_cosmics
from mtpipeline.imaging.run_astrodrizzle import run_astrodrizzle
from mtpipeline.imaging.run_trim import run_trim

LOGFOLDER = "/astro/3/mutchler/mt/logs/"

# ----------------------------------------------------------------------------
# Functions (alphabetical)
# ----------------------------------------------------------------------------

def check_for_outputs(outputs):
    '''
    Returns True if all the outputs are present, else False.
    '''
    assert isinstance(outputs, str) or isinstance(outputs, list), \
        'Expected str or list for outputs. Got ' + type(outputs)
    if isinstance(outputs, str):
        outputs = [outputs]
    for item in outputs:
        if not os.path.exists(item):
            return False
    return True

# ----------------------------------------------------------------------------

def make_output_file_dict(filename):
    '''
    Generate a dictionary with the list of expected inputs for each 
    step. This allows steps to be omitted if the output files already 
    exist.
    '''
    # Check the input.
    error = filename + ' does not end in "c0m.fits".'
    assert filename[-8:] == 'c0m.fits', error

    # Build the dictionary.
    output_file_dict = {}
    output_file_dict['input_file'] = filename
    output_file_dict['cr_reject_output'] = []
    output_file_dict['drizzle_output'] = []
    output_file_dict['png_output'] = []
    output_file_dict['drizzle_weight'] = []
    path, basename = os.path.split(filename)
    basename = basename.split('_')[0]
    
    # CR Rejection outputs.
    for cr in ['_c0m.fits','_cr_c0m.fits']:
        filename = os.path.join(path, basename + cr)
        output_file_dict['cr_reject_output'].append(filename)
            
    # Drizzled outputs.
    for cr in ['_c0m','_cr_c0m']:
        for drz in ['_wide_single_sci.fits', '_center_single_sci.fits']:
            filename = os.path.join(path, basename + cr + drz)
            output_file_dict['drizzle_output'].append(filename)
        for drz in ['_wide_single_wht.fits', '_center_single_wht.fits']:
            filename = os.path.join(path, basename + cr + drz)
            output_file_dict['drizzle_weight'].append(filename)

    # PNG outputs.
    for cr in ['_c0m','_cr_c0m']:
        for drz in ['_wide_single_sci_linear.png', '_center_single_sci_linear.png']:
            filename = os.path.join(path, 'png', basename + cr + drz)
            output_file_dict['png_output'].append(filename)
            if drz == '_wide_single_sci_linear.png':
                for i_image in range(1,13):
                    new_file = filename.replace('_linear', '_linear_{}'.format(i_image))
                    output_file_dict['png_output'].append(new_file)
    
    return output_file_dict

# ----------------------------------------------------------------------------
# The main function.
# ----------------------------------------------------------------------------

def imaging_pipeline(root_filename, output_path = None, cr_reject_switch=True, 
        astrodrizzle_switch=True, png_switch=True, reproc_switch=False):
    '''
    This is the main controller for all the steps in the pipeline.
    '''
    # Generate the output drizzle names 
    filename = os.path.abspath(root_filename) 
    output_file_dict = make_output_file_dict(root_filename)

    # Run CR reject
    if cr_reject_switch:
        output_check = check_for_outputs(output_file_dict['cr_reject_output'][1])
        if reproc_switch == False and output_check == True:
            print 'Not reprocessing cr_reject files.'
            logger.info("Not reprocessing cr_reject files.")
        else:
            logger.info("Running cr_reject")
            print 'Running cr_reject'
            run_cosmics(root_filename, output_file_dict['cr_reject_output'][1], 7)
            print 'Done running cr_reject'
            logger.info("Done running cr_reject")
    else:
        logger.info("Skipping cr_reject ")
        print 'Skipping cr_reject'
    
    # Run astrodrizzle.         
    if astrodrizzle_switch:
        output_check = check_for_outputs(output_file_dict['drizzle_output'])
        if reproc_switch == False and output_check == True:
            logger.info("Not reprocessing astrodrizzle files.")
            print 'Not reprocessing astrodrizzle files.'
        else:
            logger.info("Running Astrodrizzle")
            print 'Running Astrodrizzle'
            for filename in  output_file_dict['cr_reject_output']:
                updatewcs.updatewcs(filename)
                run_astrodrizzle(filename)
            print 'Done running astrodrizzle'
            logger.info("Done running astrodrizzle")
    else:
        print 'Skipping astrodrizzle'
        logger.info("Skipping astrodrizzle")
        
    # Run trim.
    if png_switch:
        output_check = check_for_outputs(output_file_dict['png_output'])
        if reproc_switch == False and output_check == True:
            print 'Not reprocessing png files.'
            logger.info("Not reprocessing png files.")
        else:
            print 'Running png'
            logger.info("Running png")
            for filename, weight_file in zip(output_file_dict['drizzle_output'], \
                    output_file_dict['drizzle_weight']):
                run_trim(filename, weight_file, output_path)
            print 'Done running png'
            logger.info("Done running png")
    else:
        print 'Skipping running png'
        logger.info("Skipping running png")
        
