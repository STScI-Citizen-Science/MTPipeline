#! /usr/bin/env python

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

import sys
if sys.platform == 'win32':
	engine = create_engine('sqlite:///C:\\Users\\ACV\\Documents\\My Dropbox\\Work\\MTPipeline\\Code\\database\\test.db')
else:
	engine = create_engine('sqlite:///:memory:', echo=True)

def create_tables():
Base = declarative_base()
	class Neptune(Base):
	    __tablename__ = 'neptune'

	    id = Column(Integer, primary_key=True)
	    triton = Column(String)         
	    nereid = Column(String)                 
	    naiad = Column(String)                  
	    thalassa = Column(String)               
	    despina = Column(String)               
	    galatea = Column(String)                
	    larissa = Column(String)                
	    proteus = Column(String)                
	    halimede = Column(String)               
	    psamathe = Column(String)               
	    sao = Column(String)                    
	    laomedeia = Column(String)              
	    neso = Column(String)

	Base.metadata.create_all(engine)

