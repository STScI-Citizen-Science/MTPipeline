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
    def __init__(self, filename):
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
        self.project_id = pyfits.getval(filename, 'proposid')
        #self.name = 
        self.fits_file = basename 
        self.object_name = pyfits.getval(filename, 'targname')
        #self.set_id = 
        #self.set_index =
        self.width = pyfits.getval(filename, 'NAXIS1')
        self.height = pyfits.getval(filename, 'NAXIS2')
        self.minimum_ra = pyfits.getval(filename, 'RA_TARG') - (420.0 / 72000)
        self.minimum_dec = pyfits.getval(filename, 'DEC_TARG') - (424.5 / 72000)
        self.maximum_ra = pyfits.getval(filename, 'RA_TARG') + ((self.width - 420.0) / 72000) 
        self.maximum_dec = pyfits.getval(filename, 'DEC_TARG') + ((self.height - 424.5) / 72000) 
        self.pixel_resolution = 0.05 #arcsec / pix
        self.description = pyfits.getval(filename, 'FILTNAM1')
        self.file_location = path

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
    for filename in file_list:
        path, basename = os.path. os.path.split(os.path.abspath(filename))
        if args.rebuild == False:
            query = session.query(MasterImages.name).filter(MasterImages.name == basename)
            if len(query.all()) == 0:
                record = MasterImages(filename)
                session.add(record)
        elif args.rebuild == True:
            record = MasterImages(filename)
            session.add(record)           

    session.commit()