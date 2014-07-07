#! /usr/bin/env python

'''
Populates the finders table in the MySQL database using SQLAlchemy 
ORM.
'''

import argparse
import os
import string

from mtpipeline.database.database_interface import counter
from mtpipeline.database.database_interface import check_type
#from mtpipeline.database.database_interface import insert_record
from mtpipeline.database.database_interface import update_record

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from mtpipeline.database.database_interface import session
from mtpipeline.database.database_interface import Finders
from mtpipeline.database.database_interface import MasterFinders
from mtpipeline.database.database_interface import MasterImages
from mtpipeline.database.database_interface import SubImages

#----------------------------------------------------------------------------

def get_ephem_region(ephem_x, ephem_y):
    '''
    Figure out which region the ephemeris is in.
    '''
    ephem_region = ((min(ephem_x // 425, 3) + 1) * 3) \
        - min(ephem_y // 425, 2)
    assert ephem_region in range(1,13),\
        'Region ' + str(ephem_region) + ' is not in [1,12]'
    return ephem_region


def get_region_list(ephem_x, ephem_y):
    '''
    Calculate which regions the ephemeris coordinate lays in.
    '''
    region_list = []
    region_list.append(get_ephem_region(ephem_x, ephem_y))
    
    # Overlap in X
    if ephem_x % 425 <= 25 and ephem_x >= 425 and ephem_x <= 1300:
            region_list.append(get_ephem_region(ephem_x, ephem_y) - 3)
    
    # Overlap in Y
    if ephem_y % 425 <= 25 and ephem_y >= 425 and ephem_y <= 875:
            region_list.append(get_ephem_region(ephem_x, ephem_y) + 1)
    
    # Overlap in X and Y
    if ephem_x % 425 <= 25 and ephem_x >= 425 and ephem_x <= 1300\
        and ephem_y % 425 <= 25 and ephem_y >= 425 and ephem_y <= 875:
            region_list.append(get_ephem_region(ephem_x, ephem_y) - 2)
    
    # Check and return
    assert len(region_list) in [1, 2, 4], \
        'Unexpected number of regions in list: {}'.format(len(region_list))
    for region in region_list:
        assert region in range(1,13), \
            'Region {} is not in [1,12]: coords: {}, {}'.\
            format(region, ephem_x, ephem_y)
    return region_list


def add_new_record(record, region):
    '''
    Make a dictionary of all the data for a record.
    '''
    finders = Finders()
    finders.sub_images_id = session.query(SubImages.id)\
                .filter(SubImages.master_images_id == record.MasterFinders.master_images_id)\
                .filter(SubImages.region == region)\
                .one().id
    finders.master_finders_id = record.MasterFinders.id
    finders.object_name = record.MasterFinders.object_name
    finders.x = record.MasterFinders.ephem_x - ((record.MasterFinders.ephem_x // 425) * 425)
    finders.y = record.MasterFinders.ephem_y - ((record.MasterFinders.ephem_y // 425) * 425)
    session.add(finders)


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
        .filter(MasterFinders.ephem_y <= 1300)\
        .filter(MasterImages.drz_mode == 'wide')\
        .all()
    print str(len(query)) + ' ephemerides in wide mode image FOVs'

    count = 0
    for record in query:
        count = counter(count)
        region_list = get_region_list(record.MasterFinders.ephem_x, record.MasterFinders.ephem_y)
        for region in region_list:
            add_new_record(record, region)
    session.commit()
    session.close()


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
