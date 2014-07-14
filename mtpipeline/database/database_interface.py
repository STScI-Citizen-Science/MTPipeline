#! /usr/bin/env python

"""Defines the ORMs for the MySQL ephemerides database.

Note that the loadConnection function is called directly in this 
module so that the objects it returns can be directly imported 
without having to import and run the function again.

Authors:
    Alex Viana, 2013 
"""

import os
import pyfits

from mtpipeline.get_settings import SETTINGS
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

def loadConnection(connection_string, echo=False):
    """Establishes the database connection.

    This function establishes the connection to the database. It 
    returns a session object, the declarative base class, and an 
    engine object. 

    Parameters: 
        connection_string : str
            A SQLAlchemy style connection string. This value should 
            never be hard-coded into a function call and should 
            instead be read in from an external yaml configuration 
            file. The exception to this is unit tests which are always 
            performed using a temporary sqlte3 in-memory database. 
        echo : Bool
            A Boolean toggling the echo parameter of the 
            `create_engine` function. Setting this to True will 
            trigger both command line and logging outputs.

    Returns:
        session : Class instance
            An instance of the SQLAlchemy Session class. Used to issue 
            all the database commands.
        Base : Class
            The declarative base Base class. Used as a parent class 
            for all the ORM definitions.
        engine : Class instance
            The engine object.

    Outputs:
        nothing
    """
    engine = create_engine(connection_string, echo=echo)
    Base = declarative_base(engine)
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, Base, engine

#----------------------------------------------------------------------------
# Define all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

session, Base, engine = loadConnection(SETTINGS['db_connection'], 
                                       SETTINGS['db_echo'])

class Finders(Base):
    '''
    Class for interacting with the master_images MySQL table. 
    Subclasses the Base class for the SQLAlchemy declarative base.
    '''
    __tablename__ = 'finders'
    id = Column(Integer, primary_key=True)
    sub_images_id = Column(Integer, 
        ForeignKey('sub_images.id'),
        nullable=False)
    master_finders_id = Column(Integer,
        ForeignKey('master_finders.id'),
        nullable=False)
    x = Column(Float)
    y = Column(Float)
    diameter = Column(Float)
    object_name = Column(String(50))
    description = Column(String(50))
    mysql_engine = 'InnoDB'
    sub_images_rel = relationship('SubImages', 
        backref=backref('sub_images', order_by=id))
    master_finders_rel = relationship('MasterFinders', 
        backref=backref('master_finders', order_by=id))


class MasterFinders(Base):
    '''
    Class for interacting with the master_finders MySQL table.
    '''
    __tablename__ = 'master_finders'
    id = Column(Integer, primary_key=True)
    object_name = Column(String(45))
    master_images_id = Column(Integer, 
        ForeignKey('master_images.id'),
        nullable=False)
    ephem_x = Column(Integer)
    ephem_y = Column(Integer)
    version = Column(Integer)
    jpl_ra = Column(String(15))
    jpl_dec = Column(String(15))
    magnitude = Column(Float)
    diameter = Column(Float)
    mysql_engine = 'InnoDB'
    master_images_rel = relationship("MasterImages", 
        backref=backref('master_finders', order_by=id))


class MasterImages(Base):
    """ORM for the master_images MySQL table. """
    __tablename__ = 'master_images'
    id  = Column(Integer, primary_key=True)
    project_id  = Column(Integer)
    name = Column(String(50), unique=True)
    fits_file = Column(String(50), unique=True)
    object_name = Column(String(50))
    set_id = Column(Integer)
    set_index = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    minimum_ra = Column(Float(30))
    minimum_dec = Column(Float(30))
    maximum_ra = Column(Float(30))
    maximum_dec = Column(Float(30))
    pixel_resolution = Column(Float(10))
    priority = Column(Integer, default=1)
    description = Column(String(50))
    file_location = Column(String(100))
    visit = Column(String(11))
    orbit = Column(Integer)
    drz_mode  = Column(String(6))
    cr_mode = Column(String(6))
    mysql_engine = 'InnoDB'

    def __init__(self, header, fits_file, png_file):
        """Populates the class attributes of the MasterImages instance.

        Note that the `__init__` method does not populate the set 
        information, that is done by the `set_set_values` method and
        a MasterImages instance's attribute data which is ingested 
        into the database isn't complete until that method is run.

        The values for the minimum and maximum ra and dec are given in 
        degrees to match the units of the RA_TARG and DEC_TARG 
        keywords. calculated assuming the the HST pointing information 
        is for pixels (420.0, 424.5). The width and hieght of the image
        in pixels is taken from the NAXIS1 and NAXIS2 header keywords. 
        The conversion used is (3,600 arcsec / 1 deg) * 
        (20 pix / 1 arcsec) = (72,000 pix / 1 deg). The pixel 
        resolution is given in units of arcsec / pix.

        Parameters:
            input1 : int
                Description of input1.
            input2 : list of strings
                Description of input2.
        """
        fits_path, fits_name = os.path.split(os.path.abspath(fits_file))
        png_path, png_name = os.path.split(os.path.abspath(png_file))
        self.project_id = header['proposid']
        self.name = png_name
        self.fits_file = fits_name
        self.object_name = header['targname']
        self.width = header['NAXIS1']
        self.height = header['NAXIS2']
        self.minimum_ra = header['RA_TARG'] - (420.0 / 72000)
        self.minimum_dec = header['DEC_TARG'] - (424.5 / 72000)
        self.maximum_ra = header['RA_TARG'] + ((self.width - 420.0) / 72000)
        self.maximum_dec = header['DEC_TARG'] + ((self.height - 424.5) / 72000)
        self.pixel_resolution = 0.05 #arcsec / pix
        self.description = header['FILTNAM1']
        self.file_location = png_path
        linenum = header['LINENUM']
        self.visit = linenum.split('.')[0]
        self.orbit = linenum.split('.')[1]
        self.drz_mode = fits_name.split('_')[-3]
        cr_mode = fits_name.split('_')[1]
        if cr_mode == 'c0m':
            cr_mode = 'no_cr'
        assert cr_mode in ['no_cr', 'cr'], 'Unexpected CR mode.'
        self.cr_mode = cr_mode

    def set_set_values(self, existing_set_dict, max_set_id):
        """Set set_id and set_index attributes.

        The `set_id` keyword identifies a unique combination of the 
        `proposid`, `linenum` (split into orbit and visit in the 
        database), `drz_mode`, and `cr_mode` keywords. Images that 
        share a `set_id` value are enumerated in by the `set_index` 
        variable in the order they are ingested. Observation order
        is not automatically preserved by the `set_index` keyword. 
        However, it may end up being preserved due to the alphabetical 
        naming convention for FITS files which corresponds with 
        exposure order. 

        The set_id and set_index attributes require information about 
        the state of the database and any INSERT statements in the 
        current session. This information comes from the 
        existing_set_dict and max_set_id variables which this method 
        takes as an input, sometimes modifies, and then returns.

        Parameters:
            existing_set_dict : dict
                A dictionary where the keys are tuples of project_id, 
                visit, orbit, drz_mode, and cr_mode and each value is 
                the `set_id` associated with that key. 
            max_set_id : int
                The largest set_id value, used to generate new 
                set_id's records.

        Returns: 
            existing_set_dict : dict
                A modified version of the existing_set_dict variable 
                updated with the information from the method call. 
            max_set_id : int
                A modified version of the max_set_id variable updated 
                with the information from the method call. 
        """
        key = (self.project_id, self.visit, self.orbit, self.drz_mode, 
               self.cr_mode)
        if key in existing_set_dict:
            existing_set_dict[key]['set_index'] += 1
        else:
            max_set_id += 1
            existing_set_dict[key] = {'set_id':max_set_id, 'set_index':1}
        self.set_id = existing_set_dict[key]['set_id']
        self.set_index = existing_set_dict[key]['set_index'] 
        return existing_set_dict, max_set_id        


class SubImages(Base):
    '''
    Class for interacting with the sub_images MySQL table.
    '''
    __tablename__ = 'sub_images'
    id  = Column(Integer, primary_key=True)
    project_id = Column(Integer)
    master_images_id = Column(Integer, 
        ForeignKey('master_images.id'),
        nullable=False)
    master_images_name = Column(String(50), 
        ForeignKey('master_images.name'),
        nullable=False)
    name = Column(String(50))
    x = Column(Integer)
    y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    image_width = Column(Integer)
    image_height = Column(Integer)
    scale_level = Column(Integer)
    file_location = Column(String(100))
    thumbnail_location = Column(String(100))
    active = Column(Integer)
    confirmed = Column(Integer)
    description = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    priority = Column(Float)
    done = Column(Integer)
    view_count = Column(Integer)
    region = Column(Integer)
    mysql_engine = 'InnoDB'
    master_images_id_rel = relationship(MasterImages,
        primaryjoin=(master_images_id==MasterImages.id),
        backref=backref('master_images_id_ref', order_by=id))
    master_images_name_rel = relationship(MasterImages,
        primaryjoin=(master_images_name==MasterImages.name), 
        backref=backref('master_images_name_ref', order_by=id))
 
