

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
from platform import architecture
from stwcs import updatewcs
from astropy.io import fits

# Custom Packages
from mtpipeline.tools.file_handling import make_output_file_dict
from mtpipeline.tools.file_handling import get_mtargs
from mtpipeline.imaging.run_cosmicx import run_cosmicx
from mtpipeline.imaging.run_cosmicx import get_cosmicx_params
from mtpipeline.imaging.run_astrodrizzle import run_astrodrizzle
from mtpipeline.imaging.run_trim import run_trim
from mtpipeline.get_settings import SETTINGS

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

def get_metadata(filename):
    """Retrieves the image's detector, as well as the gain and 
       readnoise, from a FITS image's header.
    
    Parameters:
        filename: str
            The path to and the filename of a FITS image.
        
    Returns:
        header_data: dict 
            Has keys , 'detector','readnoise', and 'gain', 'targname'
                and , 'filtername'
            Possible 'instrument' values: 'WFPC2', 'WFC3', 'ACS' 
            Possible 'detector' values: 
                'WFPC2' for WFPC2 (not technically correct, as WFPC2 FITS
                images have no detector keyword, but accurate enough).
                'UVIS', 'IR' for WFC3
                'SBC', 'HRC', 'WFC' for ACS

    Outputs: nothing 

    """

    with fits.open(filename, mode='readonly') as HDUlist:

        mainHDU = HDUlist[0]
        instrument = mainHDU.header['instrume']
        
        # Because WFPC2 has no 'detector' keyword:
        try:
            detector = mainHDU.header['detector']
        except KeyError:
            detector = instrument

        gain = None
        readnoise = None
        filtername = "none"
        targname = "none"
        
        # For WFPC2, there is no readnoise information in the header.
	    # There is gain information, but it leads to bad CR rejection.
        # For ACS / SBC, there is no readnoise or gain information.
	    # If None, we use the settings provided in the cfg files.
        
        if detector != 'SBC' and instrument != 'WFPC2':
      	    gain = mainHDU.header['ccdgain']
            readnoise_a = mainHDU.header['readnsea']
            readnoise_b = mainHDU.header['readnseb']
            readnoise_c = mainHDU.header['readnsec']
            readnoise_d = mainHDU.header['readnsed']
            readnoise = max(readnoise_a, readnoise_b,readnoise_c,readnoise_d)

        if instrument == 'WFPC2':
            try:
                filtername = mainHDU.header['filtnam1']
            except: print "Failed to find filter keyword."
        if instrument == 'WFC3':
            try:
                filtername = mainHDU.header['filter']
            except: print "Failed to find filter keyword."
        if instrument == 'ACS':
            try:
                filt1 = mainHDU.header['filter1']
                filt2 = mainHDU.header['filter2']
                if filt1[0] == 'F': filtername = filt1 
                if filt2[0] == 'F': filtername = filt2 
            except: print "Failed to find filter keyword."

        try:
            targname = mainHDU.header['targname']
        except: print "Failed to find targname keyword."

    header_data = {'instrument' : instrument,
                   'detector' : detector,
                   'readnoise' : readnoise,
                   'gain' : gain,
                   'targname' : targname,
                   'filtername' : filtername}

    return header_data

# ----------------------------------------------------------------------------
# The main function.
# ----------------------------------------------------------------------------

def imaging_pipeline(root_filename, output_path = None, cr_reject_switch=True, 
        astrodrizzle_switch=True, png_switch=True, reproc_switch=False):
    '''
    This is the main controller for all the steps in the pipeline.
    '''
    # Get information from the header
    header_data = get_metadata(root_filename)
    detector = header_data['detector']

    # Generate the output filenames 
    filename = os.path.abspath(root_filename) 
    output_file_dict = make_output_file_dict(root_filename,header_data)

    # Run CR reject
    if cr_reject_switch:
        output_check = check_for_outputs(output_file_dict['cr_reject_output'][1])
        if reproc_switch == False and output_check == True:
            print 'Not reprocessing cr_reject files.'
            logging.info("Not reprocessing cr_reject files.")
        else:
            logging.info("Running cr_reject")
            print 'Running cr_reject'

            cosmicx_params = get_cosmicx_params(header_data) 
            logging.info(cosmicx_params)

            output_filename = output_file_dict['cr_reject_output'][1]
            run_cosmicx(root_filename, 
                        output_filename,
                        cosmicx_params,
                        detector)
            print 'Done running cr_reject'
            logging.info("Done running cr_reject")
    else:
        logging.info("Skipping cr_reject ")
        print 'Skipping cr_reject'
    
    # Run astrodrizzle.         
    if astrodrizzle_switch:
        output_check = check_for_outputs(output_file_dict['drizzle_output'])
        if reproc_switch == False and output_check == True:
            logging.info("Not reprocessing astrodrizzle files.")
            print 'Not reprocessing astrodrizzle files.'
        else:
            logging.info("Running Astrodrizzle")
            print 'Running Astrodrizzle'
            for filename, output in zip(output_file_dict['cr_reject_output'],
                                        output_file_dict['drizzle_output']):
                updatewcs.updatewcs(filename)
                run_astrodrizzle(filename, output, detector)
            print 'Done running astrodrizzle'
            logging.info("Done running astrodrizzle")
    else:
        print 'Skipping astrodrizzle'
        logging.info("Skipping astrodrizzle")
        
    # Run trim.
    if png_switch:
        output_check = check_for_outputs(output_file_dict['png_output'])
        if reproc_switch == False and output_check == True:
            print 'Not reprocessing png files.'
            logging.info("Not reprocessing png files.")
        else:
            print 'Running png'
            logging.info("Running png")
            for filename in output_file_dict['drizzle_output']:
                run_trim(filename, output_path,log_switch=True)
            print 'Done running png'
            logging.info("Done running png")
    else:
        print 'Skipping running png'
        logging.info("Skipping running png")
        
