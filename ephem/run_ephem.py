#! /usr/bin/env python

import argparse
import glob
import os
import pickle

from database_interface import loadConnection
from ephem import ephem_main

from build_master_table import get_fits_file

session, Base = loadConnection('mysql+pymysql://root@localhost/mtpipeline')

from database_interface import Finders
from database_interface import MasterImages
from database_interface import MasterFinders

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
    args = parser.parse_args()
    return args

#----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    file_list = glob.glob(args.filelist)
    for filename in file_list:

        query = session.query(MasterImages).filter(MasterImages.fits_file == os.path.basename(filename)).one()

        moon_dict = ephem_main(filename)
        for moon in moon_dict.keys():

            print moon_dict[moon]

            record = MasterFinders()
            record.object_name = moon
            record.delta_x = float(moon_dict[moon]['delta_x'])
            record.delta_y = float(moon_dict[moon]['delta_y'])
            record.master_images_id = query.id
            session.add(record)

            session.commit()

    session.close()