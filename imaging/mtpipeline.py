#! /usr/bin/env python

'''
This is the main module for the Moving Target Pipeline.

Alex C. Viana
viana@stsci.edu
'''

# Standard packages
import argparse
import glob
import os
from stwcs import updatewcs

# Costum Packages
from run_cosmics import run_cosmics
from run_astrodrizzle import run_astrodrizzle
from run_trim import run_trim

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

    # PNG outputs.
    for cr in ['_c0m','_cr_c0m']:
        for drz in ['_wide', '_center']:
            for png in ['_single_sci_log.png', '_single_sci_median.png']:
                filename = os.path.join(path, basename + cr + drz + png)
                output_file_dict['png_output'].append(filename)
    
    return output_file_dict

# ----------------------------------------------------------------------------
# The main module.
# ----------------------------------------------------------------------------

def run_mtpipeline(root_filename, output_path = None, cr_reject_switch=True, 
        astrodrizzle_switch=True, png_switch=True, reproc_switch=False):
    '''
    This is the main controller for all the steps in the pipeline.
    '''
    # Generate the output drizzle names 
    filename = os.path.abspath(root_filename) 
    output_file_dict = make_output_file_dict(root_filename)

    # Run CR reject.
    if cr_reject_switch:
        output_check = check_for_outputs(output_file_dict['cr_reject_output'][1])
        if reproc_switch == False and output_check == True:
            print 'Not reprocessing cr_reject files.'
        else:
            print 'Running cr_reject'
            run_cosmics(root_filename, output_file_dict['cr_reject_output'][1])
            print 'Done running cr_reject'
    else:
        print 'Skipping cr_reject'
    
    # Run astrodrizzle.         
    if astrodrizzle_switch:
        output_check = check_for_outputs(output_file_dict['drizzle_output'])
        if reproc_switch == False and output_check == True:
            print 'Not reprocessing astrodrizzle files.'
        else:
            print 'Running Astrodrizzle'
            for filename in  output_file_dict['cr_reject_output']:
                updatewcs.updatewcs(filename)
                run_astrodrizzle(filename)
            print 'Done running astrodrizzle'
    else:
        print 'Skipping astrodrizzle'
        
    # Run trim.
    if png_switch:
        output_check = check_for_outputs(output_file_dict['png_output'])
        if reproc_switch == False and output_check == True:
            print 'Not reprocessing png files.'
        else:
            print 'Running png'
            for filename in output_file_dict['drizzle_output']:
                run_trim(filename, output_path, 'median')
            print 'Done running png'
    else:
        print 'Skipping running png'
        
# ----------------------------------------------------------------------------
# For command line execution.
# ----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Run the moving target pipeline.' )
    parser.add_argument(
        '-filelist',
        required = True,
        help = 'Search string for files. Wildcards accepted.')
    parser.add_argument(
        '-output_path',
        required = False,
        help = 'Set the path for the output. Default is the input directory.')
    parser.add_argument(
        '-no_cr_reject',
        required = False,
        action='store_false',
        default = True,
        dest = 'cr_reject',
        help = 'Toggle off the cosmic ray rejection step.')
    parser.add_argument(    
        '-no_astrodrizzle',
        required = False,
        action='store_false',        
        default = True,
        dest = 'astrodrizzle',
        help = 'Toggle off the astrodrizzle step.')
    parser.add_argument(
        '-no_png',
        required = False,
        action = 'store_false',        
        default = True,
        dest = 'png',
        help = 'Toggle off the png step.')
    parser.add_argument(
        '-reproc',
        required = False,
        action = 'store_true',
        default = False,
        dest = 'reproc',
        help = 'Reprocess all files, even if outputs already exist.')
    args = parser.parse_args()
    return args

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    rootfile_list = glob.glob(args.filelist)
    assert rootfile_list != [], 'empty rootfile_list in mtpipeline.py.'
    for filename in rootfile_list:
        run_mtpipeline(filename, 
            output_path =  args.output_path,
            cr_reject_switch = args.cr_reject,
            astrodrizzle_switch = args.astrodrizzle, 
            png_switch = args.png,
            reproc_switch = args.reproc)