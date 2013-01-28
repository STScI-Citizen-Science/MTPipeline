#! /usr/bin/env python

'''
Creates and returns a sqlalchemy session object using the declaarative 
base.
'''

import os
import pyfits

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def loadConnection(connection_string):
    '''
    Create and engine using an engine string. Declare a base and 
    metadata. Load the session and return a session object.
    '''
    engine = create_engine(connection_string, echo=True)
    Base = declarative_base(engine)
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, Base

# Breifly open a database connection to get the arguments needed for 
# autoloading.
session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')
session.close()


class Finders(Base):
    '''
    Class for interacting with the master_images MySQL table. 
    Subclasses the Base class for the SQLAlchemy declarative base.
    '''
    __tablename__ = 'finders'
    __table_args__ = {'autoload':True}


class MasterFinders(Base):
    '''
    Class for interacting with the master_finders MySQL table.
    '''
    __tablename__ = 'master_finders'
    __table_args__ = {'autoload':True}
    

class MasterImages(Base):
    '''
    Class for interacting with the master_images MySQL table. 
    Subclasses the Base class for the SQLAlchemy declarative base.
    '''
    __tablename__ = 'master_images'
    __table_args__ = {'autoload':True}

    def load(self, png_file, fits_file):
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
        png_path, png_name = os.path.split(os.path.abspath(png_file))
        fits_path, fits_name = os.path.split(os.path.abspath(fits_file))

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


