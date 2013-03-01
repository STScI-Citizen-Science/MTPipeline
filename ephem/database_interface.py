#! /usr/bin/env python

'''
Creates and returns a sqlalchemy session object using the declaarative 
base.
'''

import os
import pyfits

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

def loadConnection(connection_string):
    '''
    Create and engine using an engine string. Declare a base and 
    metadata. Load the session and return a session object.
    '''
    engine = create_engine(connection_string, echo=False)
    Base = declarative_base(engine)
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, Base

#----------------------------------------------------------------------------
# Define all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')

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

class SubImages(Base):
    '''
    Class for interacting with the sub_images MySQL table.
    '''
    __tablename__ = 'sub_images'
    __table_args__ = {'autoload':True}

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
        str(type(record_dict)) + ' instead.'


def insert_record(record_dict, tableclass_instance):
    '''
    Insert the value into the database using SQLAlchemy.
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
    query.update(record_dict)
    session.commit()
