#! /usr/bin/env python

'''
Populates the sub_images table in the MySQL database using SQLAlchemy 
ORM.
'''

import argparse
import glob
import os

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database_interface import loadConnection
from database_interface import MasterImages
from database_interface import SubImages

session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')

#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------

def build_sub_images_table_main(filename, reproc):
    '''
    The main controller.
    '''
    assert os.path.splitext(filename)[1] == '.png', \
        'Expected .png got ' + filename
    path = os.path.split(filename)[0] 
    basename = os.path.basename(filename)
    if basename.split('_')[1] == 'cr':
        drizzle_type = basename.split('_')[3]
    else:
        drizzle_type = basename.split('_')[2]
    assert drizzle_type in ['wide', 'center'], \
        'Unexpected image type ' + drizzle_type + ' for ' + filename
    if drizzle_type == 'wide':
        if len(basename) in [42, 45]:
            master_filename = basename[:-6] + '.png'
        elif len(basename) in [43, 46]:
            master_filename = basename[:-7] + '.png'
        else:
            print basename
            print len(basename)
    elif drizzle_type == 'center':
        if len(basename) in [44, 47]:
            master_filename = basename[:-6] + '.png'
        elif len(basename) in [45, 48]:
            master_filename = basename[:-7] + '.png'
        else:
            print basename
            print len(basename)
    
    master_images_query = session.query(MasterImages).filter(\
        MasterImages.name == master_filename).one()

    sub_images_query = session.query(SubImages).filter(\
        SubImages.name == basename).count()

    if sub_images_query == 0:
        record = SubImages()
        record.master_image_id = master_images_query.id
        record.master_image_name = master_images_query.name
        record.name = basename
        record.file_location = path
        session.add(record)
        session.commit()

    elif sub_images_query == 1:
        update_dict = {}
        update_dict['master_image_id'] = master_images_query.id
        update_dict['master_image_name'] = master_images_query.name
        update_dict['name'] = basename
        update_dict['file_location'] = path
        sub_images_query = session.query(SubImages).filter(\
            SubImages.name == basename).update(update_dict)
        session.commit()
    else:
        pass

    session.close()

#----------------------------------------------------------------------------
# For Command Line Execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description = 'Populates the sub_images table.')
    parser.add_argument(
        '-filelist',
        required = True,
        help = 'Search string for files. Wildcards accepted.')
    parser.add_argument(
        '-reproc',
        required = False,
        action = 'store_true',        
        default = False,
        dest = 'reproc',
        help = 'Overwrite existing entries.')
    args = parser.parse_args()
    return args

#----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    filelist = glob.glob(args.filelist)
    assert isinstance(filelist, list), \
        'Expected list for filelist, got ' + str(type(filelist))
    for filename in filelist:
        build_sub_images_table_main(filename, args.reproc)