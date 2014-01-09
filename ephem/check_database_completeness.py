#! /usr/bin/env python

import datetime
import logging
import os
import socket

from database_interface import session
from database_interface import Base
from database_interface import Finders
from database_interface import MasterFinders
from database_interface import MasterImages
from database_interface import SubImages

from mt_logging import setup_logging

MOONS_PER_PLANET_DICT = {'neptune':14, 
                         'pluto':5, 
                         'jupiter':68, 
                         'uranus':28, 
                         'mars':3, 
                         'saturn':62}

def get_target_name(item):
    """Take a query record, split the name field, and return the 
    target name."""
    return item.file_location.split('/')[-2].split('_')[-1]


def check_database_completeness_main():
    """The main function for the module."""

    # Log the hostname and database record counds.
    logging.info('Host is {}'.format(socket.gethostname()))
    
    # Do the record counts for the master table.
    master_images_query = session.query(MasterImages).all()
    master_images_count = len(master_images_query)
    cr_wide_count = 0
    cr_center_count = 0
    wide_count = 0
    center_count = 0
    unknown_type_count = 0
    for record in master_images_query:
        if len(record.fits_file) == 37:
            cr_wide_count += 1
        elif len(record.fits_file) == 39:
            cr_center_count += 1
        elif len(record.fits_file) == 34:
            wide_count += 1
        elif len(record.fits_file) == 36:
            center_count += 1
        else:
            unknown_type_count += 1
    logging.info('{} records found in master_images'.format(master_images_count))
    logging.info('{} cr wide records found in master_images'.format(cr_wide_count))
    logging.info('{} cr center records found in master_images'.format(cr_center_count))
    logging.info('{} non-cr wide records found in master_images'.format(wide_count))
    logging.info('{} non-cr center records found in master_images'.format(center_count))
    logging.info('{} unknown type records found in master_images'.format(unknown_type_count))


    # Do the record counts for the master_finders records
    logging.info('{} records found in master_finders'.\
        format(session.query(MasterFinders).count()))
    logging.info('{} records found in master_images LEFT JOIN master_finders'.\
        format(session.query(MasterImages, MasterFinders).\
            outerjoin(MasterFinders).count()))
    logging.info('{} records with object_name IS NULL in master_images LEFT JOIN master_finders'.\
        format(session.query(MasterImages, MasterFinders).\
            outerjoin(MasterFinders).\
            filter(MasterFinders.object_name == None).count()))

    # Log the missing master_finders records
    master_finders_query = session.query(MasterImages, MasterFinders).\
            outerjoin(MasterFinders).\
            filter(MasterFinders.object_name == None).all()
    if len(master_finders_query) != 0:
        for record in master_finders_query:
            logging.error('No object_name value for {}'.\
                format(os.path.join(record.MasterImages.file_location,
                    record.MasterImages.name)))

    # Keeping this in case I need it in the future. Sorry for the mess!
    # for record in master_images_query:
    #   target_name = get_target_name(record)
    #   master_finders_count = session.query(MasterFinders).\
    #       filter(MasterFinders.master_images_id == record.id).count()
    #   if master_finders_count != MOONS_PER_PLANET_DICT[target_name]:
    #       logging.error('Expected {} moons for {} got {}'.\
    #           format(MOONS_PER_PLANET_DICT[target_name], 
    #               os.path.join(record.file_location, record.name), 
    #               master_finders_count))

if __name__ == '__main__':
    setup_logging('check_database_completeness')
    check_database_completeness_main()
