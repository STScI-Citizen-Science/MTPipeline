#! /usr/bin/env python

'''
Check to ensure that all the file counts are correct.
'''
import glob
import os

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database_interface import loadConnection
from database_interface import Finders
from database_interface import MasterFinders
from database_interface import MasterImages
from database_interface import SubImages
from database_interface import SetsMasterImages

session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')

#----------------------------------------------------------------------------
# Global Variables
#----------------------------------------------------------------------------

ARCHIVE = '/Users/viana/mtpipeline/archive'
OUTPUT_STRING = '| {:35} | {:8} |'
BORDER_STRING = '+ {:35} + {:8} +'

#----------------------------------------------------------------------------
# Functions
#----------------------------------------------------------------------------

def count_files(search_string):
    file_count = len(glob.glob(search_string))
    search_name = search_string.split('/')[-1]
    print OUTPUT_STRING.format(search_name, file_count)

def count_records():
    pass

if __name__ == '__main__':
    print BORDER_STRING.format(35 * '-', 8 * '-')
    print OUTPUT_STRING.format('FITS Files', 'Count')
    print BORDER_STRING.format(35 * '-', 8 * '-')
    proposal_count = len(glob.glob(os.path.join(ARCHIVE, '*/')))
    print OUTPUT_STRING.format('Proposals', proposal_count)
    c0m_list = glob.glob(os.path.join(ARCHIVE, '*/*c0m.fits'))
    c0m_cr_list = [x for x in c0m_list if x.split('_')[2] == 'cr']
    print OUTPUT_STRING.format('CR Rejected c0m.fits ', len(c0m_cr_list))
    c0m_count = len(c0m_list)
    print OUTPUT_STRING.format('c0m.fits', c0m_count)
    search_list = ['*/*c1m.fits',
        '*/*wide_single_sci.fits',
        '*/*center_single_sci.fits',
        '*/*single_sci.fits']
    for search_string in search_list:
        count_files(os.path.join(ARCHIVE, search_string))
    print BORDER_STRING.format(35 * '-', 8 * '-')
    print '\n'

    print BORDER_STRING.format(35 * '-', 8 * '-')
    print OUTPUT_STRING.format('Master PNG Files', 'Count')
    print BORDER_STRING.format(35 * '-', 8 * '-')
    search_list = ['*/png/*linear.png',
        '*/png/*wide*linear.png',
        '*/png/*center*linear.png']
    for search_string in search_list:
        count_files(os.path.join(ARCHIVE, search_string))
    print BORDER_STRING.format(35 * '-', 8 * '-')
    print '\n'

    print BORDER_STRING.format(35 * '-', 8 * '-')
    print OUTPUT_STRING.format('Subimage PNG Files', 'Count')
    print BORDER_STRING.format(35 * '-', 8 * '-')
    search_list = ['*/png/*linear_*.png',
        '*/png/*wide*linear_*.png',
        '*/png/*center*linear_*.png']
    for search_string in search_list:
        count_files(os.path.join(ARCHIVE, search_string))
    print BORDER_STRING.format(35 * '-', 8 * '-')
    print '\n'

    table_class_list = [Finders, MasterFinders, MasterImages, SubImages, SetsMasterImages]
    for table_class in table_class_list:
        print BORDER_STRING.format(35 * '-', 8 * '-')
        print OUTPUT_STRING.format(table_class.__tablename__, 'Records')
        print BORDER_STRING.format(35 * '-', 8 * '-')
        field_list = table_class.__table__.columns
        for field in field_list:
            print OUTPUT_STRING.format(field, session.query(table_class).filter(field != None).count())
        print BORDER_STRING.format(35 * '-', 8 * '-')
        print '\n'

