#! /usr/bin/env python

"""Populates the master_images table in the MySQL database using 
SQLAlchemy ORM.
"""

import argparse
import glob
import logging
import os

from astropy.io import fits
from mtpipeline.database.database_interface import MasterImages
from mtpipeline.database.database_interface import session
from mtpipeline.setup_logging import setup_logging
from sqlalchemy import distinct
from sqlalchemy.sql import func

#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------

def build_master_images_table_main(png_file_list, reproc, reproc_sets):
    '''
    The main controller.    
    '''
    logging.info('Beginning script')
    logging.info('-filelist setting is {}'.format(png_file_list))
    logging.info('-reproc setting is {}'.format(reproc))
    logging.info('-reproc_sets setting is {}'.format(reproc_sets))
    png_file_list = glob.glob(png_file_list)
    logging.info('filelist returned {} files'.format(len(png_file_list)))

    # Trim the input_png_list according to the reproc settings
    if reproc:
        png_file_list = png_file_list
    elif not reproc:
        logging.info('Removing existing records from filelist')
        existing_png_files = session.query(distinct(MasterImages.name)).all()
        existing_png_files = set([item[0] for item in existing_png_files])
        png_file_list = [item for item in png_file_list
                         if os.path.basename(item) not in existing_png_files]
    logging.info('Processing {} files'.format(len(png_file_list)))

    # Get Existing set information from the DB
    set_info_query = session.query(MasterImages.set_id, 
                                   MasterImages.set_index, 
                                   MasterImages.project_id,
                                   MasterImages.visit,
                                   MasterImages.orbit,
                                   MasterImages.drz_mode,
                                   MasterImages.cr_mode).\
                             filter(MasterImages.visit != None).\
                             filter(MasterImages.orbit != None).\
                             all()
    existing_set_dict = {(record.project_id, 
                          record.visit, 
                          record.orbit,
                          MasterImages.drz_mode,
                          MasterImages.cr_mode): {'set_id':record.set_id, 
                                                  'set_index':record.set_index} 
                         for record in set_info_query}
    
    # Get the max set_id value
    max_set_id = session.query(func.max(MasterImages.set_id)).one()[0]
    if max_set_id == None:
        max_set_id = 0
            
    # Build the new records     
    for png_file in png_file_list:
        logging.info('Processing {}'.format(png_file))
        fits_file = png_file.replace('png/','').replace('_linear.png','.fits')
        with fits.open(fits_file) as hdulist:
            header = hdulist[0].header
        master_images = MasterImages(header, fits_file, png_file)
        existing_set_dict, max_set_id = master_images.set_set_values(existing_set_dict, max_set_id)
        session.add(master_images)
    logging.info('Committing records to database')
    session.commit()
    logging.info('Committing records to database complete')
    logging.info('Script completed')

#----------------------------------------------------------------------------
# For command line execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Populate the master_images table.')
    parser.add_argument(
        '-filelist',
        required = True,
        help = 'Search string for files. Wildcards accepted.')
    parser.add_argument(
        '-reproc',
        required = False,
        action='store_true',        
        default = False,
        dest = 'reproc',
        help = 'Overwrite existing entries except for the set information.')
    parser.add_argument(
        '-reproc_sets',
        required = False,
        action='store_true',        
        default = False,
        dest = 'reproc_sets',
        help = 'Overwrite existing set information.')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    setup_logging('build_master_images_table')
    build_master_images_table_main(args.filelist, args.reproc, args.reproc_sets)