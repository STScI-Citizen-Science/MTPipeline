

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
from mtpipeline.imaging.run_cosmicx import run_cosmicx
from mtpipeline.imaging.run_cosmicx import get_cosmicx_params
from mtpipeline.imaging.run_astrodrizzle import run_astrodrizzle
from mtpipeline.imaging.run_trim import run_trim

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
            Has keys , 'detector','readnoise', and 'gain'
            Possible 'instrument' values: 'WFPC2', 'WFC3', 'ACS' 
            Possible 'detectors' values: 
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

    header_data = {'detector' : detector,
                   'readnoise' : readnoise,
                   'gain' : gain }

    return header_data

# ----------------------------------------------------------------------------

def make_output_file_dict(filename):
    '''
        Generate a dictionary with the list of expected inputs for each
        step. This allows steps to be omitted if the output files already
        exist.
        
        Parameters:
        input: filename
        a path to where the file is located.
        
        Returns:
        output: output_file_dict
        a dictionary with all the expected created files.
        
        Output:
        nothing
    '''
    # Check the input.
    error = filename + ' does not end in "c0m.fits" or "flt.fits".'
    assert (filename[-8:] == 'c0m.fits' or filename[-8:] == 'flt.fits'), error
    
    fits_type = filename[-8:-5]
    
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
    for cr in ['_','_cr_']:
        filename = os.path.join(path, basename + cr + fits_type + '.fits')
        output_file_dict['cr_reject_output'].append(filename)
    
    # Drizzled outputs.
    # AstroDrizzle strips _flt from the filename when writing outputs,
    # but keeps _c0m. 
    if fits_type == 'flt':
        fits_type = ''
    else:
        fits_type = 'c0m_'

    for cr in ['_','_cr_']:
        drz = 'wide_single_sci.fits'
        filename = os.path.join(path, basename + cr + fits_type + drz)
        output_file_dict['drizzle_output'].append(filename)

        drz = 'wide_single_wht.fits'
        filename = os.path.join(path, basename + cr + fits_type + drz)
        output_file_dict['drizzle_weight'].append(filename)
    
    # PNG outputs.
    for cr in ['_','_cr_']:
        drz = 'wide_single_sci_linear.png'
        filename = os.path.join(path, 'png', basename + cr + fits_type + drz)
        output_file_dict['png_output'].append(filename)
    
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

    # Get the detector, readnoise, and gain from the header
    header_data = get_metadata(root_filename)
    detector = header_data['detector']

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
            run_cosmicx(root_filename, output_filename,cosmicx_params,detector)
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
            for filename in  output_file_dict['cr_reject_output']:
                updatewcs.updatewcs(filename)
                run_astrodrizzle(filename, detector)
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
            for filename, weight_file in zip(output_file_dict['drizzle_output'], \
                    output_file_dict['drizzle_weight']):
                run_trim(filename, weight_file, output_path,log_switch=True)
            print 'Done running png'
            logging.info("Done running png")
    else:
        print 'Skipping running png'
        logging.info("Skipping running png")
        
