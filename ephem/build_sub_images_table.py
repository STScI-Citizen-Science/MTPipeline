#! /usr/bin/env python

'''
Populates the sub_images table in the MySQL database using SQLAlchemy 
ORM.
'''

import argparse
import glob
import os
import string

from database_interface import counter
from database_interface import check_type
from database_interface import insert_record
from database_interface import update_record

from PIL import Image

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database_interface import MasterImages
from database_interface import SubImages
from database_interface import session

#----------------------------------------------------------------------------
# Low-Level Functions
#----------------------------------------------------------------------------


def get_image_size(filename):
    """Use the PIL to get the images size."""
    assert isinstance(filename, str), \
        'Expected str for filename, got ' + str(type(filename))
    im = Image.open(filename)
    return im.size[0], im.size[1] 


def get_master_filename(basename):
    """Builds the master_filename."""
    check_type(basename, str)
    if basename.split('_')[1] == 'cr':
        drizzle_type = basename.split('_')[3]
    else:
        drizzle_type = basename.split('_')[2]
    assert drizzle_type in ['wide', 'center'], \
        'Unexpected image type ' + drizzle_type + ' for ' + filename
    master_filename = basename.split('linear')[0] + 'linear.png'
    return master_filename

def get_region(filename):
    """Figures out the subimage region from the filename."""
    check_type(filename, str)
    basename = os.path.basename(filename)
    if basename.split('_')[1] == 'cr':
        drizzle_type = basename.split('_')[3]
    else:
        drizzle_type = basename.split('_')[2]
    assert drizzle_type in ['wide', 'center'], \
        'Unexpected image type ' + drizzle_type + ' for ' + filename
    if drizzle_type == 'wide':
        filename = os.path.splitext(filename)[0]
        region = filename.split('/')[-1].split('_')[-1]
    elif drizzle_type == 'center':
        region = '1'
    for digit in region:
        assert digit in string.digits, \
            'Region {} is not a number for {}'.format(region, filename)
    return region


#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------


def build_sub_images_table_main(filename, reproc):
    """The main controller."""

    # Check for PNG images and skip "ephem" or "lb" images.
    assert os.path.splitext(filename)[1] == '.png', \
        'Expected .png got ' + filename

    # Generate some variables and run basic queries.
    path = os.path.split(filename)[0] 
    basename = os.path.basename(filename)
    master_filename = get_master_filename(basename)
    master_images_query = session.query(MasterImages).\
        filter(MasterImages.name == master_filename).one()
    sub_images_query = session.query(SubImages).\
        filter(SubImages.name == basename).count()

    # Skip, insert, or update depending on the query results and the 
    # reproc parameter.
    assert sub_images_query in [0, 1], \
        'Unexpected number of records: {} for {}'.\
        format(sub_images_query, filename)
    if sub_images_query == 1 and reproc == False:
        return
    else:
        image_width, image_height = get_image_size(filename)
        record_dict = {}
        record_dict['master_images_id'] = master_images_query.id
        record_dict['master_images_name'] = master_images_query.name
        record_dict['name'] = basename
        record_dict['file_location'] = path
        record_dict['image_width'] = image_width 
        record_dict['image_height'] = image_height
        record_dict['region'] = get_region(filename)

        if sub_images_query == 1 and reproc:
            sub_images_query = session.query(SubImages).filter(\
                SubImages.name == basename).update(record_dict)
        elif sub_images_query == 0:
            record = SubImages()
            insert_record(record_dict, record)
        else:
            raise Exception('Something Unexpected happed in line 103') 


#----------------------------------------------------------------------------
# For Command Line Execution
#----------------------------------------------------------------------------


def parse_args():
    '''
    parse the command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description = 'Populates the sub_images table from a PNG file list.')
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


if __name__ == '__main__':
    args = parse_args()
    filelist = glob.glob(args.filelist)
    print 'Selected ' + str(len(filelist)) + ' files from input.'
    filelist = [filename for filename in filelist if \
                os.path.basename(filename).split('_')[-1] \
                not in ['ephem.png', 'lb.png']]
    print str(len(filelist)) + ' files after removing emphem and lb.'   
    filelist = [filename for filename in filelist if \
                os.path.basename(filename).split('_')[-4] != 'wide' or \
                os.path.basename(filename).split('_')[-1] != 'linear.png']
    print 'Processing ' + str(len(filelist)) + ' files.'
    print filelist[0]
    assert isinstance(filelist, list), \
        'Expected list for filelist, got ' + str(type(filelist))
    count = 0
    for filename in filelist:
        count = counter(count)
        build_sub_images_table_main(filename, args.reproc)
        if count % 100 == 0:
            session.commit()
    session.close()

