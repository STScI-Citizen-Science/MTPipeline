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
    '''
    file_list = glob.glob(search_string)
    return file_list

# -----------------------------------------------------------------------------

def run_cosmics(filename):
    '''
    The main controller.
    '''
    # Define the output name and delete if exists.
    output = os.path.splitext(filename)[0] + '_cr.fits'
    query = os.access(output,os.F_OK)
    if query == True:
        os.remove(output)

    for ext in range(0,5):
        print filename + '[' + str(ext) + ']'

        if ext == 0:
            hdu = pyfits.open(filename)
            array = hdu[0].data
            header = hdu[0].header
            pyfits.writeto(
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
            elif ext in [2,3,4]:
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
            
    #return output
        
# -----------------------------------------------------------------------------
# For Command Line Execution
# -----------------------------------------------------------------------------

def prase_args():
    '''
    Prase the command line arguemnts.
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

# -----------------------------------------------------------------------------

if __name__ == '__main__':
    args = prase_args()
    run_cosmics(filename)