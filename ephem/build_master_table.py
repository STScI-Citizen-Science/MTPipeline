#! /usr/bin/env python

import argparse
import glob
import os
import pyfits

from database_interface import loadConnection

session, Base = loadConnection('mysql://root@localhost/mtpipeline')

class MasterImages(Base):
    '''
    Class for interacting with the master_images MySQL table. 
    Subclasses the Base class for the SQLAlchemy declarative base.
    '''
    __tablename__ = 'master_images'
    __table_args__ = {'autoload':True}
    def __init__(self, png_file, fits_file):
        '''
        The values for the minimum and maximum ra and dec are given in 
        degrees to match the units of the RA_TARG and DEC_TARG 
        keywords. calculated assuming the the HST pointing information 
        is for pixels (420.0, 424.5). The width and hieght of the image
        in pixels is taken from the NAXIS1 and NAXIS2 header keywords. 
        The conversion used is (3,600 arcsec / 1 deg) * (20 pix / 1 arcsec)
        = (72,000 pix / 1 deg). The pixel resolution is given in units 
        of arcsec / pix.
        '''
        png_path, png_name = os.path.split(png_file)
        fits_path, fits_name = os.path.split(fits_file)

        self.project_id = pyfits.getval(fits_file, 'proposid')
        self.name = png_name
        self.fits_file = fits_name
        self.object_name = pyfits.getval(fits_file, 'targname')
        #self.set_id = 
        #self.set_index =
        self.width = pyfits.getval(fits_file, 'NAXIS1')
        self.height = pyfits.getval(fits_file, 'NAXIS2')
        self.minimum_ra = pyfits.getval(fits_file, 'RA_TARG') - (420.0 / 72000)
        self.minimum_dec = pyfits.getval(fits_file, 'DEC_TARG') - (424.5 / 72000)
        self.maximum_ra = pyfits.getval(fits_file, 'RA_TARG') + ((self.width - 420.0) / 72000) 
        self.maximum_dec = pyfits.getval(fits_file, 'DEC_TARG') + ((self.height - 424.5) / 72000) 
        self.pixel_resolution = 0.05 #arcsec / pix
        self.description = pyfits.getval(fits_file, 'FILTNAM1')
        self.file_location = png_path

#----------------------------------------------------------------------------

def get_fits_file(png_file):
    '''
    Returns the absolute path to the fits file corresponding to a png 
    file. Assumes the at png file is one level above the fits file in 
    directory tree.
    '''    
    png_path, png_name = os.path.split(os.path.abspath(png_file))
    fits_path = os.path.split(png_path)[0]
    fits_name = os.path.splitext(png_name)[0]
    if fits_name[-4:] == '_log':
        fits_name = fits_name[:-4] + '.fits'
    elif fits_name[-7:] == '_median':
        fits_name = fits_name[:-7] + '.fits'
    fits_file = os.path.join(fits_path, fits_name)
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
        print fits_file
        png_path, png_name = os.path. os.path.split(os.path.abspath(png_file))
        if args.rebuild == False:
            query = session.query(MasterImages.name).filter(MasterImages.name == png_name)
            if len(query.all()) == 0:
                record = MasterImages(png_file, fits_file)
                session.add(record)
        elif args.rebuild == True:
            record = MasterImages(png_file, fits_file)
            session.add(record)           

    session.commit()