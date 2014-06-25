#! /usr/bin/env python

""" Wrapper to run lacosmicx.py
"""

import os
import glob

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


def run_cosmicx(filename, output, iters):
    """ Driver to run lacosmicx on multi-extension WFPC2 FITS files.

    An equivalent to the run_cosmics function in run_cosmiscs.py,
    borrowing much of its code. Performs cosmic-ray rejection on each
    chip of a FITS file from WFPC2.

    Parameters:
        filename: string
            filename of input FITS file
        output: string
            desired filename of output, a cosmic ray rejected FITS file.
        iters: int
            number of iterations of the LACosmics algorithm to be
            performed.

    Returns: nothing

    Outputs:
        A cosmic ray rejected FITS file with the filename given by
        'output'
        A symbolic link to the original c1m files that matches the
        output filename, for astrodrizzle.

    """

    # Assert the input file exists
    error = filename + ' input for run_cosmics in '
    error += 'run_cosmics.py does not exist.'
    assert os.access(filename, os.F_OK), error

    # Define the output name and delete if exists.
    query = os.access(output, os.F_OK)
    if query == True:
        os.remove(output)

    with fits.open(filename, mode='readonly') as HDUlist:

        # Leave the first HDU untouched, process the remaining chip
        # extensions
        for ext in range(1, len(HDUlist)):

            HDU = HDUlist[ext]
            array = HDU.data

            if ext == 1:
                cleanarray = lacosmicx.run(array,
                        inmask=None,
                        outmaskfile="",
                        pssl=0.0,
                        gain=1.0,
                        readnoise=1.0,
                        sigclip=5.0, #3.0 -> 5.0
                        sigfrac=0.01,
                        objlim=4.0,
                        satlevel=4095.0,
                        robust=False,
                        verbose=True,
                        niter=iters)

            elif ext in [2, 3, 4]:
                cleanarray = lacosmicx.run(array,
                        inmask=None,
                        outmaskfile="",
                        pssl=0.0,
                        gain=1.0,
                        readnoise=1.0,
                        sigclip=5.0, #2.5 -> 5.0
                        sigfrac=0.001,
                        objlim=5.0,
                        satlevel=4095.0,
                        verbose=True,
                        niter=iters)

            HDU.data = cleanarray

        HDUlist.writeto(output)

    # Create the symbolic link
    make_c1m_link(os.path.abspath(filename))

def make_c1m_link(filename):
    """ Create a link to a c1m.fits that matches the cosmic ray rejected
    naming scheme.

    Parameters:
        filename: string
            filename of the file to be cleaned.

    Returns: nothing

    Outputs:
        A symbolic link to 'filename'
    """

    error = filename + ' does not end in "c0m.fits".'
    assert filename[-8:] == 'c0m.fits', error
    src = filename.replace('_c0m.fits', '_c1m.fits')
    dst = src.replace('_c1m.fits', '_cr_c1m.fits')
    query = os.path.islink(dst)
    if query == True:
        os.remove(dst)
    os.symlink(src, dst)
