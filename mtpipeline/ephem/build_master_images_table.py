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

def build_master_images_table_main(fits_file_list, reproc, reproc_sets):
    '''
    The main controller.    
    '''
    logging.info('Beginning script')
    logging.info('-filelist setting is {}'.format(fits_file_list))
    logging.info('-reproc setting is {}'.format(reproc))
    logging.info('-reproc_sets setting is {}'.format(reproc_sets))
    fits_file_list = glob.glob(fits_file_list)
    logging.info('filelist returned {} files'.format(len(fits_file_list)))

    # Trim the input_png_list according to the reproc settings
    if reproc:
        fits_file_list = fits_file_list
    elif not reproc:
        logging.info('Removing existing records from filelist')
        existing_fits_files = session.query(distinct(MasterImages.name)).all()
        existing_fits_files = set([item[0] for item in existing_fits_files])
        fits_file_list = [item for item in fits_file_list
                         if os.path.basename(item) not in existing_fits_files]
    logging.info('Processing {} files'.format(len(fits_file_list)))
            
    # Build the new records     
    for fits_file in fits_file_list:
        logging.info('Processing {}'.format(fits_file))
        with fits.open(fits_file) as hdulist:
            header = hdulist[0].header
        master_images = MasterImages(header, fits_file)
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