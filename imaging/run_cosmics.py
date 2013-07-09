#! /usr/bin/env python

'''
Wrapper to run cosmics.py
'''

import argparse
import cosmics
import glob
import os
import pyfits

# -----------------------------------------------------------------------------
# Functions (alphabetical)
# -----------------------------------------------------------------------------

def get_file_list(search_string):
    '''
    Generates the file list.
    '''
    file_list = glob.glob(search_string)
    return file_list

# -----------------------------------------------------------------------------

def make_c1m_link(filename):
    '''
    Create a link to a c1m.fits that matches the cosmic ray rejected 
    naming scheme.
    '''
    error = filename + ' does not end in "c0m.fits".'
    assert filename[-8:] == 'c0m.fits', error
    src = filename.replace('_c0m.fits', '_c1m.fits')
    dst = src.replace('_c1m.fits', '_cr_c1m.fits')
    query = os.path.islink(dst)
    if query == True:
        os.remove(dst)
    os.symlink(src, dst)

# -----------------------------------------------------------------------------

def run_cosmics(filename):
    '''
    The main controller.
    '''
    
    output = filename.split('_')[0] + "_cr_" + filename.split('_')[1]

    # Assert the input file exists
    error = filename + ' input for run_cosmics in '
    error += 'run_cosmics.py does not exist.'
    assert os.access(filename, os.F_OK), error
    
    # Define the output name and delete if exists.
    query = os.access(output, os.F_OK)
    if query == True:
        os.remove(output)

        # Find the number of extentions.
    header = pyfits.open(filename)
    header_count = len(header)
    header.close()

    for ext in range(0, header_count):
        print filename + '[' + str(ext) + ']'

        if ext in [0, 5]:
            hdu = pyfits.open(filename)
            array = hdu[ext].data
            header = hdu[ext].header
            pyfits.append(
                output,
                array,
                header)
            hdu.close()
        else:
            # Read the FITS :
            array, header = cosmics.fromfits(filename, hdu = ext)
            # array is a 2D numpy array

            # Build the object
            # WFPC2 PC Chip Settings
            if ext == 1:
                c = cosmics.cosmicsimage(
                        array, 
                        pssl = 0.0, 
                        gain = 1.0, 
                        readnoise = 5.0,
                        sigclip = 3.0, 
                        sigfrac = 0.01, 
                        objlim = 4.0,
                        satlevel = 4095.0,
                        verbose = True)
            # Build the object
            # WFPC2 WF Chip Settings
            elif ext in [2, 3, 4]:
                c = cosmics.cosmicsimage(
                        array, 
                        pssl = 0.0, 
                        gain=1.0, 
                        readnoise=5.0,
                        sigclip = 2.5, 
                        sigfrac = 0.001, 
                        objlim = 5.0,
                        satlevel = 4095.0, 
                        verbose = True)

            # Run the full artillery
            c.run(maxiter = 7)

            # Write the cleaned image into a new FITS file
            # conserving the original header :
            #cosmics.tofits(output, c.cleanarray, header)

            pyfits.append(
                output,
                c.cleanarray.transpose(),
                header,
                ext = 'SCI')

            # If you want the mask, here it is :
            # cosmics.tofits("mask.fits", c.mask, header)
            # (c.mask is a boolean numpy array, that gets 
            # converted here to an integer array)

    assert os.path.isfile(output) == True, 'run_cosmics did not create: ' + output

    # Create a symbolic link to the original c1m files that matches the 
    # Output filename.
    make_c1m_link(os.path.abspath(filename))
                    
# -----------------------------------------------------------------------------
# For Command Line Execution
# -----------------------------------------------------------------------------

def parse_args():
    '''
    Parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Wrapper to run cosmics.py' )
    parser.add_argument(
        '--files', 
        required = True,
        help = 'Search string for the fits files you want to ingest.\
            e.g. "dir/*.fits"')
    args = parser.parse_args() 
    return args

if __name__ == '__main__':
    args = parse_args()
    file_list = get_file_list(args.files)
    for filename in file_list:
        run_cosmics(filename)
