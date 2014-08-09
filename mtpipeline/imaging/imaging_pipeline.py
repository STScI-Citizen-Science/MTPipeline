

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
#from mtpipeline.ephem.build_masters_finder_table import \
#     get_planet_and_moons_list
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

        if detector == 'WFPC2':
            try:
                filtername = mainHDU.header['filtnam1']
            except: print "Failed to find filter keyword."
        if instrument == 'WFC3':
            try:
                fitername = mainHDU.header['filter']
            except: print "Failed to find filter keyword."
        if instrument == 'ACS':
            try:
                filt1 = mainHDU.header['filter1']
                filt2 = mainHDU.header['filter2']
                if filt1[0] == 'F': filtname = filt1 
                if filt2[0] == 'F': filtname = filt2 
            except: print "Failed to find filter keyword."

        try:
            targname == mainHDU.header['targname']
        except: print "Failed to find targname keyword."

    header_data = {'detector' : detector,
                   'readnoise' : readnoise,
                   'gain' : gain,
                   'targname' : targname,
                   'filtername' : filtername}

    return header_data

# ----------------------------------------------------------------------------

def get_planet_and_moons_list():
    """Return a list of valid JPL HORIZONS targets.

    The JPL HORIZONS interface accepts a strict set of target names. 
    In order to 

    NOTE: This is only here to support get_mtarg below. Once Wally merges
    his branch, uncomment the import from build_masters_finder_table above.

    Parameters: 
        nothing

    Returns: 
        planet_and_moon_list: list
            List of terms that match all the planet and moon targets 
            in the WFPC2 dataset.

    Outputs:
        nothing
    """
    planet_and_moon_list = []
    with open('mtpipeline/ephem/planets_and_moons.txt', 'r') as f:
        planets_and_moons_file = f.readlines()
    for line in planets_and_moons_file:
        line = line.split(' ')
        if len(line) > 3:
            planet_and_moon_list.append(line[1])
    return planet_and_moon_list

def get_mtarg(targname):
    """
    Produce a more regular target name, using the targname keyword and the JPL
    ephemeris bodies. 
    Parameters:
        targname : (string)
            The targname keyword from the image header
    
    Returns:
        mtarg : (string)
            A dash-separated list of JPL ephemeris objects found in the
            targname, accounting for common abbreviations. If no match is
            found, the targname, truncated to 20 characters, is used instead.

    Outputs: nothing
    """
    abbrevs = {'jup' : 'jupiter',
              'gan' : 'ganymede',
              'sat' : 'saturn'}
    
    name_problems = {'pan' : ['pandora'],
                    'anthe' : ['euanthe'],
                    'io' : ['albioriz','bebhionn','iocaste'],
                    'titan' : ['titania']
                    }

    jpl_list = get_planet_and_moons_list()

    targname = targname.lower()
    mtarg_pieces = []
    
    # Look for match in the JPL ephemeris objects.
    for body in jpl_list:
        if str.find(targname,body) == -1:
            continue
        else:
            mtarg_pieces.append(body)
             
    # Look for common abbreviations
    for abbrev in abbrevs:
        body = abbrevs[abbrev]
        if str.find(targname,abbrev) == -1:
            continue
        if body not in mtarg_pieces:
            mtarg_pieces.append(body)
            
    # The names of some moons are substrings of others.
    # Hopefully, Pan and Pandora are never in the same targname,
    # because if Pandora is in the targname, Pan will be
    # removed from mtarg_pieces.
    for subname in name_problems:
        if subname in mtarg_pieces:
            for supername in name_problems[subname]:
                if supername in mtarg_pieces:
                    mtarg_pieces.remove(subname)
                
    if not mtarg_pieces:
        mtarg_pieces.append(targname[:20])
        
    mtarg = '-'.join(mtarg_pieces)
    return mtarg

# ----------------------------------------------------------------------------

def make_output_file_dict(filename,header_data):
    '''
        Generate a dictionary with the list of expected inputs for each
        step. This allows steps to be omitted if the output files already
        exist.
        
        Parameters:
        input: filename
        a path to where the file is located.
        header_data: dictionary
        information extracted from the image header, needed to configure
        the filename.
        
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

    front = 'hlsp_mt_hst'

    instrument = header_data['instrument']
    detector = header_data['detector']

    if instrument == 'WFPC2':
        hardware = instrument.lower()
    else:
        hardware = instrument + '-' + detector

    ipsud = filename.split('_')[0] 

    # Use string parsing to discern the target(s).
    mtarg = get_mtarg(header_data['targname'])

    filtername = header_data['filtername']

    version = 'v' + str(SETTINGS['version'])
    version = version.replace('.','-')

    front = '_'.join([front,hardware,ipsud,mtarg,filtername,version])
    
    # Initialize the dictionary.
    output_file_dict = {}
    output_file_dict['input_file'] = filename
    output_file_dict['cr_reject_output'] = []
    output_file_dict['drizzle_output'] = []
    output_file_dict['png_output'] = []
    output_file_dict['drizzle_weight'] = []
    path, basename = os.path.split(filename)
    

    # CR Rejection outputs.
    # We count the original input file as a cr rejection output.
    output_file_dict['cr_reject_output'].append(filename) 
    # The actual output:
    filename = '_'.join([front,fits_type]) + '.fits'
    output_file_dict['cr_reject_output'].append(filename) 

    # Drizzled outputs.
    # Cr rejected products are sci
    filename = '_'.join([front,'sci']) + '.fits'
    output_file_dict['drizzle_output'].append(filename)
    # Non cr rejected products are img
    filename = '_'.join([front,'img']) + '.fits'
    output_file_dict['drizzle_output'].append(filename)
    # Only a single weight file
    filename = '_'.join([front,'wht']) + '.fits'
    output_file_dict['drizzle_weight'].append(filename)

    # PNG outputs.
    png = 'png/'
    filename = png + '_'.join([front,'sci']) + '-linear.png'
    output_file_dict['png_output'].append(filename)
    filename = png + '_'.join([front,'img']) + '-linear.png'
    output_file_dict['png_output'].append(filename)
    filename = png + '_'.join([front,'sci']) + '-log.png'
    output_file_dict['png_output'].append(filename)
    filename = png + '_'.join([front,'img']) + '-log.png'
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
        
