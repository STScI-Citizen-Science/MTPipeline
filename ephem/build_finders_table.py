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
from database_interface import insert_record
from database_interface import Finders
from database_interface import MasterFinders
from database_interface import MasterImages
from database_interface import SubImages

#----------------------------------------------------------------------------

def get_ephem_region(record):
    '''
    Figure out which region the ephemeris is in.
    '''
    ephem_region = (((record.MasterFinders.ephem_x // 425) + 1) * 3) \
        - (record.MasterFinders.ephem_y // 425)
    return ephem_region

def get_region_list(record):
    '''
    Calculate which regions the ephemeris coordinate lays in.
    '''
    region_list = []
    region_list.append(get_ephem_region(record))
    # Overlap in X
    if record.MasterFinders.ephem_x % 425 <= 25 and record.MasterFinders.ephem_x >= 25:
        region_list.append(get_ephem_region(record) - 3)
    # Overlap in Y
    if record.MasterFinders.ephem_y % 425 <= 25 and record.MasterFinders.ephem_y >= 25:
        region_list.append(get_ephem_region(record) + 1)
    # Overlap in X and Y
    if record.MasterFinders.ephem_x % 425 <= 25 \
        and record.MasterFinders.ephem_x >= 25 \
        and record.MasterFinders.ephem_y % 425 <= 25 \
        and record.MasterFinders.ephem_y >= 25:
            region_list.append(get_ephem_region(record) - 2)
    return region_list

def make_record_dict(record):
    '''
    Make a dictionary of all the data for a record.
    '''
    record_dict = {}
    record_dict['sub_image_id'] = int(record.SubImages.id)
    record_dict['object_name'] = record.MasterFinders.object_name
    record_dict['x'] = record.ephem_x - ((record.ephem_x // 425) * 425)
    record_dict['y'] = record.ephem_y - ((record.ephem_y // 425) * 425)
    check_type(record_dict, dict)
    return record_dict


#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------


def build_finders_table_main(reproc):
    '''
    Calculate the ephemeris information for the subimages.
    '''
    query = session.query(MasterFinders).count()
    print str(query) + ' total ephemerides'
    query = session.query(MasterFinders, MasterImages)\
        .join(MasterImages, MasterImages.id == MasterFinders.master_images_id)\
        .filter(MasterFinders.ephem_x >= 0)\
        .filter(MasterFinders.ephem_y >= 0)\
        .filter(MasterFinders.ephem_x <= 1725)\
        .filter(MasterFinders.ephem_x <= 1300)\
        .filter(MasterImages.drz_mode == 'center').all()
    print str(len(query)) + ' ephemerides in image FOVs'
    for record in query:
        region_list = get_region_list(record)
        for region in region_list:
            print record.MasterFinders.master_images_id
            print region
            subimage_query = session.query(SubImages)\
                .filter(SubImages.master_image_id == record.MasterFinders.master_images_id)\
                .filter(SubImages.region == region).one()
            return

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