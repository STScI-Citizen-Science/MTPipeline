#! /usr/bin/env python

'''
Creates and returns a sqlalchemy session object using the declaarative 
base.
'''

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
    '''
    Create and engine using an engine string. Declare a base and 
    metadata. Load the session and return a session object.
    '''
    engine = create_engine(connection_string, echo=echo)
    Base = declarative_base(engine)
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, Base

#----------------------------------------------------------------------------
# Define all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

session, Base = loadConnection(SETTINGS['db_connection'], SETTINGS['db_echo'])

class Foo(Base):
    __tablename__ = 'foo'
    id = Column(Integer, primary_key=True)

class Finders(Base):
    '''
    Class for interacting with the master_images MySQL table. 
    Subclasses the Base class for the SQLAlchemy declarative base.
    '''
    #def __init__(self, **kwargs):
    #    for k, v in kwargs.iteritems():
    #        setattr(self, k, v)

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
    '''
    Class for interacting with the master_images MySQL table. 
    Subclasses the Base class for the SQLAlchemy declarative base.
    '''
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
 

#----------------------------------------------------------------------------
# General Utility Functions
#----------------------------------------------------------------------------

import datetime

def counter(count, update=100):
    '''
    Advance the count and print a status message every 100th item.
    '''
    check_type(count, int)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if count == 0:
        print now + ': Starting processing'
    count += 1
    if count % update == 0:
        print now + ': Completed ' + str(count)
    check_type(count, int)
    return count


def check_type(instance, expected_type):
    '''
    A wrapper around my standard assert isinstance pattern.
    '''
    assert isinstance(instance, expected_type), \
        'Expected ' + str(expected_type) + ' got ' +  \
        str(type(instance)) + ' instead.'


def insert_record(record_dict, tableclass_instance):
    '''
    Insert the value into the database using SQLAlchemy.

    This is being phased out in favor of a proper __init__ method for 
    the mapped classes.
    '''
    record = tableclass_instance
    check_type(record_dict, dict)
    for key in record_dict.keys():
        setattr(record, key, record_dict[key])
    session.add(record)
    session.commit()


def update_record(record_dict, query):
    '''
    Update a record in the database using SQLAlchemy. See 
    insert_record for details.
    '''
    check_type(record_dict, dict)
    count = query.update(record_dict)
    session.commit()
