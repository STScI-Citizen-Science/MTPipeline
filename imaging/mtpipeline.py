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
    basename = os.path.splitext(filename)[0]
    
    # CR Rejection outputs.
    for cr in ['','_cr']:
        drz = basename + cr + '.fits'
        output_file_dict['cr_reject_output'].append(drz)
            
    # Drizzled outputs.
    for cr in ['','_cr']:
        for drz in ['_wide', '_center']:
            drz = basename + cr + drz + '_single_sci.fits'
            output_file_dict['drizzle_output'].append(drz)
    
    return output_file_dict

# ----------------------------------------------------------------------------
# The main module.
# ----------------------------------------------------------------------------

def run_mtpipeline(root_filename, output_path = None, cr_reject_switch=True, 
        astrodrizzle_switch=True, trim_switch=True):
    '''
    This is the main controller for all the steps in the pipeline.
    '''
    # Generate the output drizzle names 
    filename = os.path.abspath(filename) 
    output_file_dict = make_output_file_dict(root_filename)
    
    # Run CR reject.
    if cr_reject_switch == True:
        print 'Running cr_reject'
        run_cosmics(root_filename)
        print 'Done running cr_reject'
    else:
        print 'Skipping cr_reject'
    
    # Run astrodrizzle.         
    if astrodrizzle_switch == True:
        print 'Running Astrodrizzle'
        for filename in  output_file_dict['cr_reject_output']:
            updatewcs.updatewcs(filename)
            run_astrodrizzle(filename)
        print 'Done running astrodrizzle'
    else:
        print 'Skipping astrodrizzle'
        
    # Run trim.
    if trim_switch == True:
        print 'Running scaling'
        for filename in output_file_dict['drizzle_output']:
            print filename
            run_trim(filename, output_path, 'median')
        print 'Done running scaling'
    else:
        print 'Skipping running scaling'
        
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
        '-no_trim',
        required = False,
        action='store_false',        
        default = True,
        dest = 'trim',
        help = 'Toggle off the scaling step.')
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
            trim_switch = args.trim)