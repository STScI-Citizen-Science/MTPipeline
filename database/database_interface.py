#! /usr/bin/env python

'''
Creates and returns a sqlalchemy session object.
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
 
import sys
if sys.platform == 'win32':
	engine = create_engine('sqlite:///C:\\Users\\ACV\\Documents\\My Dropbox\\Work\\MTPipeline\\Code\\database\\test.db')
else:
	engine = create_engine('sqlite:///:memory:', echo=True)

Base = declarative_base(engine)

class Neptune(Base):
    """"""
    __tablename__ = 'Neptune'
    __table_args__ = {'autoload':True}
 
def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session