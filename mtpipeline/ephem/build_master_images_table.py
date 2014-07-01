#! /usr/bin/env python

'''
Populates the master_images table in the MySQL database using SQLAlchemy 
ORM.
'''

import argparse
import datetime
import glob
import logging
import os
import pyfits

from astropy.io.fits import getheader
from mtpipeline.database.database_tools import counter
from mtpipeline.database.database_tools import check_type
from mtpipeline.database.database_tools import insert_record
from mtpipeline.database.database_tools import update_record
from mtpipeline.setup_logging import setup_logging
from sqlalchemy import desc
from sqlalchemy import distinct
from sqlalchemy.sql import func

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from mtpipeline.database.database_interface import MasterImages
from mtpipeline.database.database_interface import session

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------

def get_fits_file(png_file):
    """Returns the absolute path to the fits file corresponding to a 
    png file. Assumes the at png file is one level below the fits file 
    in directory tree. Checks to ensure the input file is .png and 
    that the output is .fits.
    """  
    assert os.path.splitext(png_file)[-1] == '.png', 'png file required'
    fits_file = png_file.replace('png/','').replace('_linear.png','.fits')
    return fits_file


def make_record_dict(png_file, fits_file):
    '''
    Make a dictionary of all the data for a record.

    The values for the minimum and maximum ra and dec are given in 
    degrees to match the units of the RA_TARG and DEC_TARG 
    keywords. calculated assuming the the HST pointing information 
    is for pixels (420.0, 424.5). The width and hieght of the image
    in pixels is taken from the NAXIS1 and NAXIS2 header keywords. 
    The conversion used is (3,600 arcsec / 1 deg) * (20 pix / 1 arcsec)
    = (72,000 pix / 1 deg). The pixel resolution is given in units 
    of arcsec / pix.
    '''
    png_path, png_name = os.path.split(os.path.abspath(png_file))
    fits_path, fits_name = os.path.split(os.path.abspath(fits_file))
    header_dict = getheader(fits_file)
    record_dict = {}
    record_dict['project_id'] = header_dict['proposid']
    record_dict['name'] = png_name
    record_dict['fits_file'] = fits_name
    record_dict['object_name'] = header_dict['targname']
    record_dict['width'] = header_dict['NAXIS1']
    record_dict['height'] = header_dict['NAXIS2']
    record_dict['minimum_ra'] = header_dict['RA_TARG'] - \
        (420.0 / 72000)
    record_dict['minimum_dec'] = header_dict['DEC_TARG'] - \
        (424.5 / 72000)
    record_dict['maximum_ra'] = header_dict['RA_TARG'] + \
        ((record_dict['width'] - 420.0) / 72000) 
    record_dict['maximum_dec'] = header_dict['DEC_TARG'] + \
        ((record_dict['height'] - 424.5) / 72000) 
    record_dict['pixel_resolution'] = 0.05 #arcsec / pix
    record_dict['description'] = header_dict['FILTNAM1']
    record_dict['file_location'] = png_path
    linenum = header_dict['LINENUM']
    record_dict['visit'] = linenum.split('.')[0]
    record_dict['orbit'] = linenum.split('.')[1]
    record_dict['drz_mode'] = fits_name.split('_')[-3]
    cr_mode = fits_name.split('_')[1]
    if cr_mode == 'c0m':
        cr_mode = 'no_cr'
    assert cr_mode in ['no_cr', 'cr'], 'Unexpected CR mode.'
    record_dict['cr_mode'] = cr_mode        
    record_dict = make_set_info(record_dict)
    return record_dict


def make_set_info(record_dict):
    '''
    Use the existing dictionary information and the database to 
    construct the set information and add it to the dictionary.
    '''
    check_type(record_dict, dict)

    # If the set_index already exists keep the existing value. To 
    # reprocess all set_id and set_index values they have to be set to 
    # Null. Assumes a set_id exists if the set_index exists.
    master_images_query = session.query(MasterImages).filter(\
        MasterImages.name == record_dict['name']).filter(\
        MasterImages.set_index != None)
    assert master_images_query.count() <= 1, 'Got too many results.'
    if master_images_query.count() == 1:
        master_images_query = master_images_query.one()
        record_dict['set_id'] = master_images_query.set_id
        record_dict['set_index'] = master_images_query.set_index
        return record_dict
    
    # If there isn't already a set_index, get all the records that 
    # match the proposid, visit, and orbit, ignoring the records with 
    # Null values.
    set_matches = session.query(MasterImages).filter(\
        MasterImages.project_id == record_dict['project_id']).filter(\
        MasterImages.visit != None).filter(\
        MasterImages.orbit != None).filter(\
        MasterImages.visit == record_dict['visit']).filter(\
        MasterImages.orbit == record_dict['orbit'])

    # If all the set_id values are None.
    if set_matches.filter(MasterImages.set_id != None).count() == 0:
        max_set_id = session.query(func.max(MasterImages.set_id)).one()[0]
        if max_set_id == None:
            record_dict['set_id'] = 1
            record_dict['set_index'] = 1
        else:
            record_dict['set_id'] = max_set_id + 1
            record_dict['set_index'] = 1

    # If the set_id already exists
    else:
        set_id = set_matches.filter(\
            MasterImages.set_id != None).group_by(\
            MasterImages.set_id).one()
        record_dict['set_id'] = set_id.set_id
        max_set_index = set_matches.filter(\
            MasterImages.set_index != None).order_by(\
            desc(MasterImages.set_index)).first()
        record_dict['set_index'] = max_set_index.set_index + 1
    return record_dict

#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------

def build_master_images_table_main(file_list, reproc, reproc_sets):
    '''
    The main controller.    
    '''
    logging.info('Beginning Processing')
    logging.info('-reproc setting is {}'.format(reproc))
    logging.info('-reproc_sets setting is {}'.format(reproc_sets))

    # If the set information is being reprocessed set it to NULL and 
    # let the regular set processing handle it.
    if reproc == True and reproc_sets == False:
        print 'REMINDER: You are reprocessing everything BUT the set information.'
    if reproc_sets:
        reproc = True
        update_dict = {'set_id':None, 'set_index':None}
        logging.info('Updating all set_index and set_id information to NULL.')
        session.query(MasterImages).filter(\
            MasterImages.set_index != None).update(update_dict)
        session.commit()
        logging.info('Update complete')


    file_list = glob.glob(file_list)
    logging.info('Processing {} files'.format(len(file_list)))
    count = 0
    for png_file in file_list:
        fits_file = get_fits_file(png_file)
        png_path, png_name = os.path.split(os.path.abspath(png_file))
        master_images_query = session.query(MasterImages).filter(\
            MasterImages.name == png_name)
        assert master_images_query.count() in [0, 1], \
            'Multiple matches for ' + png_name
        if master_images_query.count() == 0:
            record_dict = make_record_dict(png_file, fits_file)
            insert_record(record_dict, MasterImages())
        elif master_images_query.count() == 1 and reproc == True:
            record_dict = make_record_dict(png_file, fits_file)
            update_record(record_dict, master_images_query)
        count = counter(count)
    session.close()
    logging.info('Processing Completed')

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

#----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    setup_logging('build_master_images_table')
    build_master_images_table_main(args.filelist, args.reproc, args.reproc_sets)