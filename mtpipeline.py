#! /usr/bin/env python

'''
This is the main module for the Moving Target Pipeline.

Alex C. Viana
viana@stsci.edu
'''

import argparse
import glob
import os
from run_cosmics import run_cosmics
from run_astrodrizzle import run_astrodrizzle
from run_trim import run_trim
from stwcs import updatewcs
import sys

# ----------------------------------------------------------------------------
# Functions (alphabetical)
# ----------------------------------------------------------------------------

def make_output_file_dict(filename):
	'''
	Generate a dictionary with the list of expected inputs for each 
	step. This allows steps to be omitted if the output files already 
	exist.
	'''
	# Generate the output drizzle names.
	output_file_dict = {}
	output_file_dict['drizzle_output']
	basename = os.path.splitext(filename)[0]
	
	# CR Rejection outputs.
	for cr in ['','_cr']:
		drz = basename + cr + '.fits'
		output_file_dict['cr_reject_output'].append(drz)
			
	# Drizzled outputs.
	for cr in ['','_cr']:
		for drz in ['_slice']: #['_slice', '_wide', '_zoom']:
			drz = basename + cr + drz + '_single_sci.fits'
			output_file_dict['drizzle_output'].append(drz)
	
	return output_file_dict

# ----------------------------------------------------------------------------

def get_files():
    '''
    This gets the list of files to run.
    '''
    
    if 0 == 1:
        file_list = ['/astro/3/mutchler/mt/drizzled/neptune/u40n0101m_c0m.fits']
    
    if 0 == 1: 
        file_list = [
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0101m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n010bm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0208m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0305m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0102m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n010cm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0209m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0306m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0103m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n010dm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n020am_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0307m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0104m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0201m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n020bm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0308m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0105m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0202m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n020cm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0309m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0106m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0203m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n020dm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n030am_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0107m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0204m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0301m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n030bm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0108m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0205m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0302m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n030cm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0109m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0206m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0303m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n030dm_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n010am_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0207m_c0m.fits',
            '/astro/3/mutchler/mt/drizzled/neptune/u40n0304m_c0m.fits']
    
    file_list = glob.glob('/astro/3/mutchler/mt/drizzled/neptune/*c0m.fits')
    file_list = [item for item in file_list if len(item) == 56]
    
    return file_list

# ----------------------------------------------------------------------------
# The main module.
# ----------------------------------------------------------------------------

def run_mtpipeline(root_filename, cr_reject_switch=False, 
        astrodrizzle_switch=False, trim_switch=True):
    '''
    This is the main controller for all the steps in the pipeline.
    ''' 
	# Generate the output drizzle names	
	output_file_dict = make_output_file_dict(root_filename)
	
	# Run CR reject.
	if cr_reject_switch == True:
		run_cosmics(root_filename)
	
	# Run astrodrizzle.			
	if astrodrizzle_switch == True:
		for filename in  output_file_dict['cr_reject_output']:
			updatewcs.updatewcs(filename)
            run_astrodrizzle(filename)
	
	# Run trim.
	if trim_switch == True:
		for filename in output_file_dict['drizzle_output']:
			run_trim(drz)

# ----------------------------------------------------------------------------
# For command line execution.
# ----------------------------------------------------------------------------

def prase_args():
    '''
    Prase the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Run the moving target pipeline.' )
    parser.add_argument(
        '--filelist',
        required = False,
        default = False,
        help = 'search string for files. Wildcards accepted.')
    args = parser.parse_args()
       
    return args

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    args = prase_args()
    rootfile_list = glob.glob(args.filelist)
    for filename in rootfile_list:
        print filename
        error = filename + ' does not end in "c0m.fits".'
        assert filename[-8:] == 'c0m.fits', error
        run_mtpipeline(filename)