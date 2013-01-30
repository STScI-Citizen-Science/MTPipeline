#! /usr/bin/env python

import argparse
import glob
import os
import pyfits

from database_interface import loadConnection
from database_interface import MasterImages

session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')

#----------------------------------------------------------------------------

def get_fits_file(png_file):
    '''
    Returns the absolute path to the fits file corresponding to a png 
    file. Assumes the at png file is one level below the fits file in 
    directory tree. Checks to ensure the input file is .png and that 
    the output is .fits.
    '''    
    png_path, png_name = os.path.split(os.path.abspath(png_file))
    assert os.path.splitext(png_name)[1] == '.png', 'png file required'
    fits_path = os.path.split(png_path)[0]
    fits_name = os.path.splitext(png_name)[0]
    if fits_name[-4:] == '_log':
        fits_name = fits_name[:-4] + '.fits'
    elif fits_name[-7:] in ['_median', '_linear']:
        fits_name = fits_name[:-7] + '.fits'
    fits_file = os.path.join(fits_path, fits_name)
    assert os.path.splitext(fits_file)[1] == '.fits', 'unexpected output.'
    return fits_file

#----------------------------------------------------------------------------
# For command line execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Populate the master_images table.')
    parser.add_argument(
        '-filelist',
        required = True,
        help = 'Search string for files. Wildcards accepted.')
    parser.add_argument(
        '-rebuild',
        required = False,
        action='store_true',        
        default = False,
        dest = 'rebuild',
        help = 'Toggle off the scaling step.')
    args = parser.parse_args()
    return args

#----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    file_list = glob.glob(args.filelist)
    for png_file in file_list:
        fits_file = get_fits_file(png_file)
        png_path, png_name = os.path. os.path.split(os.path.abspath(png_file))
        if args.rebuild == False:
            query = session.query(MasterImages.name).filter(MasterImages.name == png_name)
            if query.count() == 0:
                record = MasterImages()
                record.load(png_file, fits_file)
                session.add(record)
        elif args.rebuild == True:
            record = MasterImages()
            records.load(png_file, fits_file)
            session.add(record)           
        session.commit()
    session.close()