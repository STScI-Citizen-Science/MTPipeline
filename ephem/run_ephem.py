#! /usr/bin/env python

import argparse
import glob
import pickle

from database_interface import loadConnection
from ephem import *

session, Base = loadConnection('mysql://root@localhost/mtpipeline')

from database_interface import Finders
from database_interface import MasterImages

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

        #session.query(MasterImages).filter()

        moon_dict = main(filename)
        for moon in moon_dict.keys():
            record = Finders()
            record.object_name = moon
            record.x = moon_dict[moon]['delta_x']
            record.y = moon_dict[moon]['delta_y']
            session.add(record)

        for record in session.query(Finders):
            print record.object_name, record.x, record.y

    session.commit()