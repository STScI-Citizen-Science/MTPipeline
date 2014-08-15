#! /usr/bin/env python

""" Wrapper to run lacosmicx.py
"""

import os
import shutil
import inspect
import glob
import yaml

import lacosmicx
from astropy.io import fits


# -----------------------------------------------------------------------------
# Functions (alphabetical)
# -----------------------------------------------------------------------------

def get_file_list(search_string):
    """ Generates a list of files matching the given glob string

    Parameters:
        search_string: string
            glob-formatted search pattern

    Returns:
        file_list: list
            list of files matching pattern

    Outputs: nothing
    """

    file_list = glob.glob(search_string)
    return file_list

# -----------------------------------------------------------------------------

def get_cosmicx_params(header_data):
    """ Accesses the cosmicx configure file and returns the parameters.
    
    Parameters:
        instrument: string
            The intrument for the image. Can be 'WFPC2', 'WFC3', 'ACS'
        header_data: dictionary
                Dictionary containing information from FITS header

    Returns:
        cosmicx_params: dict
            A list of dictionaries, with one dictionary for each FITS 
            extension. Each dictionary has the cosmicx parameters appropriate
            for that extension. If the extension is not a science extension,
            the list has None, instead of a dictionary, for that extension.

    """


    detector_config = { 'WFPC2' : "WFPC2_params.yaml",
                        'HRC' : "HRC_params.yaml",
                        'SBC' : "SBC_params.yaml",
                        'WFC' : "WFC_params.yaml",
                        'UVIS' : "UVIS_params.yaml",
                        'IR' : "IR_params.yaml" }

    detector = header_data["detector"]
    readnoise = header_data["readnoise"]
    gain = header_data["gain"]

    # Load the configuration file for the proper detector:
    config_file = detector_config[detector]

    # os.path.dirname is called three times to move up three directories
    # from this file, to reach to where the cosmicx_cfg directory is located.
    param_path = os.path.dirname(os.path.dirname(os.path.dirname(
                 os.path.abspath(inspect.getfile(inspect.currentframe())))))
    param_path = os.path.join(param_path,'cosmicx_cfg')
    param_path = os.path.join(param_path, config_file)

    cosmicx_params = yaml.load(open(param_path))

    # If we have readnoise and gain from the FITS header, override the 
    # manually specified values from the cfg file:
    if readnoise:
        for extension_key in cosmicx_params:
            cosmicx_params[extension_key]["readnoise"] = readnoise
    if gain:
        for extension_key in cosmicx_params:
            cosmicx_params[extension_key]["gain"] = gain

    return cosmicx_params 

# -----------------------------------------------------------------------------


def run_cosmicx(filename, output, cosmicx_params, detector):
    """ Driver to run lacosmicx on multi-extension FITS files.

    An equivalent to the run_cosmics function in run_cosmiscs.py,
    borrowing much of its code. Performs cosmic-ray rejection on each
    chip of a FITS file.

    Parameters:
        filename: string
            filename of input FITS file
        output: string
            desired filename of output, a cosmic ray rejected FITS file.
        cosmicx_params: dictionary
            a dictionary of dictionaries, with each entry dictionary
            containing the cosmicx settings appropriate for a
            particular FITS science extension.
        detector: string
            the detector used to take the FITS image. If SBC or IR,
            cr rejection is not run.

    Returns: nothing

    Outputs:
        A cosmic ray rejected FITS file with the filename given by
        'output'
        A symbolic link to the original c1m files that matches the
        output filename, for Astrodrizzle.

    """

    # Assert the input file exists
    error = filename + ' input for run_cosmicx in '
    error += 'run_cosmics.py does not exist.'
    assert os.access(filename, os.F_OK), error

    # If the file is taken by SBC or IR, do not cr reject, copy
    # the file with the output name, and return
    if detector == 'SBC' or detector == 'IR':
        shutil.copyfile(filename,output)
        return

    # Define the output name and delete if exists
    query = os.access(output, os.F_OK)
    if query == True:
        os.remove(output)

    with fits.open(filename, mode='readonly') as HDUlist:
        
        for key in cosmicx_params:
            
            params = cosmicx_params[key]

            # It's possible there may not be the same number of SCI extensions
            # in the image as we specify in the cfg files (WFC)
            try: 
                HDU = HDUlist[key]
            except IndexError:
                continue

            # It's possible some of the SCI extensions might not have data,
            # as subsets of the CCD are sometimes used, and these extensions
            # are empty (UVIS)
            try: 
                array = HDU.data
            except AttributeError: 
                continue

            # For a cleaner cr rejection, set all very negative pixels
            # to 0. No significant science data should be lost, as these
            # are already bad pixels
            array[array < -10.0] = 0.0

            cleanarray = lacosmicx.run(array,
                       inmask=params['inmask'],
                       outmaskfile=params['outmaskfile'],
                       pssl=params['pssl'],
                       gain=params['gain'],
                       readnoise=params['readnoise'],
                       sigclip=params['sigclip'],
                       sigfrac=params['sigfrac'],
                       objlim=params['objlim'],
                       satlevel=params['satlevel'],
                       robust=params['robust'],
                       verbose=params['verbose'],
                       niter=params['niter'] )

            HDU.data = cleanarray

        HDUlist.writeto(output)

    # Create the symbolic link
    make_c1m_link(os.path.abspath(filename),
                  os.path.abspath(output))

# -----------------------------------------------------------------------------

def make_c1m_link(filename, output):
    """ Create a link to a c1m.fits that matches the cosmic ray rejected
    naming scheme. This is only done for WFPC2 data (which ends in _c0m.fits)

    Parameters:
        filename: string
            filename of the file to be cleaned.

    Returns: nothing

    Outputs:
        A symbolic link to 'filename'
    """

    if filename[-8:] == 'c0m.fits':
        src = filename.replace('_c0m.fits', '_c1m.fits')
        dst = output.replace('_c0m.fits', '_c1m.fits')
        query = os.path.islink(dst)

        if query == True:
            os.remove(dst)
        os.symlink(src, dst)
