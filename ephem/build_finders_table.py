#! /usr/bin/env python

'''
Populates the finders table in the MySQL database using SQLAlchemy 
ORM.
'''

import argparse
import os
import string

from database_interface import counter
from database_interface import check_type
#from database_interface import insert_record
from database_interface import update_record

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database_interface import session
from database_interface import Finders
from database_interface import MasterFinders
from database_interface import MasterImages
from database_interface import SubImages

#----------------------------------------------------------------------------

def get_ephem_region(record):
    '''
    Figure out which region the ephemeris is in.
    '''
    ephem_region = str(((record.MasterFinders.ephem_x // 450) * 3) + \
                (record.MasterFinders.ephem_y // 450) + 1)
    return ephem_region

def make_record_dict(record):
    '''
    Make a dictionary of all the data for a record.
    '''
    record_dict = {}
    record_dict['sub_image_id'] = int(record.SubImages.id)
    record_dict['object_name'] = record.MasterFinders.object_name
    record_dict['x'] = int(record.MasterFinders.ephem_x - \
        ((record.MasterFinders.ephem_x // 450) * 450))
    record_dict['y'] = int(record.MasterFinders.ephem_y - \
        ((record.MasterFinders.ephem_y // 450) * 450))
    check_type(record_dict, dict)
    return record_dict

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

#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------

def build_finders_table_main(reproc):
    '''
    '''
    count = 0
    print 'Querying database ...'
    query = session.query(SubImages, MasterFinders, MasterImages)\
        .join(MasterFinders, SubImages.master_image_id == MasterFinders.master_images_id)\
        .join(MasterImages, SubImages.master_image_id == MasterImages.id)\
        .filter(MasterFinders.ephem_x != None)\
        .filter(MasterFinders.ephem_y != None).all()
    print 'Processing ' + str(len(query)) + ' records.'
    for record in query:
        subimage_region = os.path.splitext(record.SubImages.name)[0][-1]
        if subimage_region in string.digits:
            ephem_region = get_ephem_region(record)
            if subimage_region == ephem_region:
                record_dict = make_record_dict(record)
            else:
                continue
        else:
            if record.MasterFinders.ephem_x <= 450 and record.MasterFinders.ephem_y <= 450:
                record_dict = make_record_dict(record)
            else:
                continue
        duplicate_query = session.query(Finders)\
            .filter(Finders.object_name == record.MasterFinders.object_name)\
            .filter(Finders.sub_image_id == record.SubImages.id)
        assert duplicate_query.count() in [0,1], 'Found duplicate records.'
        if duplicate_query.count() == 0:
            finders = Finders()
            insert_record(record_dict, finders)
        elif duplicate_query.count() == 1:
            update_record(record_dict, duplicate_query)
        count = counter(count)

#----------------------------------------------------------------------------
# For command line execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Populate the finders table.')
    parser.add_argument(
        '-reproc',
        required = False,
        action='store_true',        
        default = False,
        dest = 'reproc',
        help = 'Overwrite existing entries except for the set information.')
    args = parser.parse_args()
    return args

#----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    build_finders_table_main(args.reproc)