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
    engine = create_engine(connection_string, echo=False)
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


class SubImages(Base):
    '''
    Class for interacting with the sub_images MySQL table.
    '''
    __tablename__ = 'sub_images'
    __table_args__ = {'autoload':True}


class SetsMasterImages(Base):
    '''
    Class for interacting with the sets_master_images MySQL table.
    '''
    __tablename__ = 'sets_master_images'
    __table_args__ = {'autoload':True}


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


