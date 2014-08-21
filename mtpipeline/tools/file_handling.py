#! /usr/bin/env python


"""Module for file-handling and string-parsing functions used throughout 
the pipeline.

This module contains functions used in the various parts (imaging, database,
ephemeris) of the pipeline, such as functions to grab header information from
FITS images, to handle filename conventions for the pipeline outputs,
and to parse target names.

Authors:
    Kevin Hale, kevinfhale@gmail.com, 2014
"""

import os
import inspect
from mtpipeline.get_settings import SETTINGS


# ----------------------------------------------------------------------------
# Functions (alphabetical)
# ----------------------------------------------------------------------------

def get_mtargs(targname):
    """
    Produce a more regular target name, using the targname keyword and the JPL
    ephemeris bodies. 
    Parameters:
        targname : (string)
            The targname keyword from the image header
    
    Returns:
        mtarg : (string)
            A dash-separated list of planets and moons found in the
            targname, accounting for common abbreviations. If no match is
            found, an empty list is returned.

    Outputs: nothing
    """
    abbrevs = {'jup' : 'jupiter',
              'gan' : 'ganymede',
              'sat' : 'saturn'}
    
    name_problems = {'pan' : ['pandora'],
                    'anthe' : ['euanthe'],
                    'io' : ['albioriz','bebhionn','iocaste','dione'],
                    'titan' : ['titania']
                    }

    jpl_list = get_planets_and_moons_list()

    targname = targname.lower()
    mtargs = []
    
    # Look for match in the JPL ephemeris planets and moons.
    for body in jpl_list:
        if str.find(targname,body) == -1:
            continue
        else:
            mtargs.append(body)
             
    # Look for common abbreviations
    for abbrev in abbrevs:
        body = abbrevs[abbrev]
        if str.find(targname,abbrev) == -1:
            continue
        if body not in mtargs:
            mtargs.append(body)
            
    # The names of some moons are substrings of others.
    # Hopefully, Pan and Pandora are never in the same targname,
    # because if Pandora is in the targname, Pan will be
    # removed from mtargs.
    for subname in name_problems:
        if subname in mtargs:
            for supername in name_problems[subname]:
                if supername in mtargs:
                    mtargs.remove(subname)
                
    return mtargs

# ----------------------------------------------------------------------------

def get_planets_and_moons_list():
    """Return a list of valid JPL HORIZONS targets.

    The JPL HORIZONS interface accepts a strict set of target names. 
    In order to 

    XXX

    Parameters: 
        nothing

    Returns: 
        planet_and_moon_list: list
            List of terms that match all the planet and moon targets 
            in the WFPC2 dataset.

    Outputs:
        nothing
    """
    planet_and_moon_list = ['jup-', 'gany-', 'sat-', 'gan-',
                            'io-']

    pm_path = inspect.getfile(inspect.currentframe()) # This file
    pm_path = os.path.abspath(pm_path) # Absolute path to this file
    pm_path = os.path.dirname(pm_path) # This directory 
    pm_path = os.path.join(pm_path,'planets_and_moons.txt')
    
    with open(pm_path, 'r') as f:
        planets_and_moons_file = f.readlines()
    for line in planets_and_moons_file:
        line = line.split(' ')
        if len(line) > 3:
            planet_and_moon_list.append(line[1])
    return planet_and_moon_list


# ----------------------------------------------------------------------------

def make_output_file_dict(filename,header_data):
    '''
        Generate a dictionary with the list of expected inputs for each
        step. This allows steps to be omitted if the output files already
        exist.
        
        Parameters:
        input: filename
        a path to the input file.
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
        hardware = instrument.lower() + '-' + detector.lower()

    path, basename = os.path.split(filename)

    #Get the 9-character alphanumeric identifier for the observation
    ipsud = basename.split('_')[0] 

    # Use string parsing to discern the target(s).
    mtargs = get_mtargs(header_data['targname'])

    # If no planets or moons are found, use the standard targname keyword,
    # truncated to 20 characters.
    if mtargs == []:
        mtargs = header_data['targname'][:20]
    else:
        mtargs = '-'.join(mtargs)

    ipsud_and_mtargs = ipsud + '-' + mtargs

    filtername = header_data['filtername'].lower()

    version = 'v' + str(SETTINGS['version'])
    version = version.replace('.','-')

    front = '_'.join([front,hardware,ipsud_and_mtargs,filtername,version])
    
    # Initialize the dictionary.
    output_file_dict = {}
    output_file_dict['input_file'] = filename
    output_file_dict['cr_reject_output'] = []
    output_file_dict['drizzle_output'] = []
    output_file_dict['png_output'] = []
    output_file_dict['drizzle_weight'] = []
    

    # CR Rejection outputs.
    # We count the original input file as a cr rejection output.
    output_file_dict['cr_reject_output'].append(filename) 
    # The actual output:
    filename = '_'.join([front,fits_type]) + '.fits'
    filename = os.path.join(path,filename)
    output_file_dict['cr_reject_output'].append(filename) 

    # Drizzled outputs.
    # Cr rejected products are sci
    filename = '_'.join([front,'img']) + '.fits'
    filename = os.path.join(path,filename)
    output_file_dict['drizzle_output'].append(filename)
    # Non cr rejected products are img
    filename = '_'.join([front,'sci']) + '.fits'
    filename = os.path.join(path,filename)
    output_file_dict['drizzle_output'].append(filename)
    # Only a single weight file
    filename = '_'.join([front,'wht']) + '.fits'
    filename = os.path.join(path,filename)
    output_file_dict['drizzle_weight'].append(filename)

    # PNG outputs.
    filename = '_'.join([front,'sci']) + '-linscale.png'
    filename = os.path.join(path,filename)
    output_file_dict['png_output'].append(filename)
    filename = '_'.join([front,'img']) + '-linscale.png'
    filename = os.path.join(path,filename)
    output_file_dict['png_output'].append(filename)
    filename = '_'.join([front,'sci']) + '-logscale.png'
    filename = os.path.join(path,filename)
    output_file_dict['png_output'].append(filename)
    filename = '_'.join([front,'img']) + '-logscale.png'
    filename = os.path.join(path,filename)
    output_file_dict['png_output'].append(filename)

    return output_file_dict

# ----------------------------------------------------------------------------

