#! /usr/bin/env python

import argparse
import glob
import os
import pickle

from build_master_table import get_fits_file
from database_interface import loadConnection
from ephem import ephem_main

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')

from database_interface import Finders
from database_interface import MasterImages
from database_interface import MasterFinders

#----------------------------------------------------------------------------
# The main controller for the module
#----------------------------------------------------------------------------

def run_ephem_main(filelist, reproc=False):
    '''
    The main controller for the module. It executes the code in ephem_main 
    and writes the output to the database.
    '''
    file_list = glob.glob(filelist)
    for filename in file_list:

        # Get the unique record from the master_images table.
        master_images_query = session.query(MasterImages).filter(\
            MasterImages.fits_file == os.path.basename(filename)).one()

        # Count the number of records in the master_finders table that 
        # match the id field of the master_images_query.
        master_finder_query = session.query(MasterFinders).filter(\
            MasterFinders.master_images_id == master_images_query.id).count()

        if master_finder_query == 0 or reproc == True:
            moon_dict = ephem_main(filename)
            for moon in moon_dict.keys():
                if reproc:
                    update_dict = {}
                    update_dict['object_name'] = moon
                    update_dict['delta_x'] = float(moon_dict[moon]['delta_x'])
                    update_dict['delta_y'] = float(moon_dict[moon]['delta_y'])
                    update_dict['ephem_x'] = int(moon_dict[moon]['ephem_x'])
                    update_dict['ephem_y'] = int(moon_dict[moon]['ephem_y'])
                    update_dict['master_images_id'] = master_images_query.id
                    print update_dict
                    session.query(MasterFinders).filter(\
                        MasterFinders.master_images_id == master_images_query.id, 
                        MasterFinders.object_name == moon).update(update_dict)
                else:
                    record = MasterFinders()
                    record.object_name = moon
                    record.delta_x = float(moon_dict[moon]['delta_x'])
                    record.delta_y = float(moon_dict[moon]['delta_y'])
                    record.ephem_x = int(moon_dict[moon]['ephem_x'])
                    record.ephem_y = int(moon_dict[moon]['ephem_y'])
                    record.master_images_id = master_images_query.id
                    session.add(record)
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
        description = 'Generate the ephemeride data.')
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
    run_ephem_main(args.filelist, args.reproc)
