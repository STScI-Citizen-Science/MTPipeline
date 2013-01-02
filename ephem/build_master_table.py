#! /usr/bin/env python

import argparse
import glob
import os
import pyfits

from database_interface import loadConnection


session, Base = loadConnection('mysql://root@localhost/mtpipeline')

class MasterImages(Base):
    '''
    '''
    __tablename__ = 'master_images'
    __table_args__ = {'autoload':True}

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
        '-rebuild',
        required = False,
        action='store_true',        
        default = False,
        dest = 'rebuild',
        help = 'Toggle off the scaling step.')
    args = parser.parse_args()
    return args

#----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    file_list = glob.glob(args.filelist)
    for filename in file_list:
        if args.rebuild == False:
            path, basename = os.path. os.path.split(os.path.abspath(filename))
            query = session.query(MasterImages.name).filter(MasterImages.name == basename)
            if len(query.all()) == 0:
                record = MasterImages()
                record.project_id = pyfits.getval(filename, 'proposid')
                record.name = basename 
                record.object_name = pyfits.getval(filename, 'targname')
                #record.set_id =
                #record.set_index =
                #record.width = 
                #record.height = 
                #record.minimum_ra = 
                #record.minimum_dec =
                #record.maximum_ra = 
                #record.maximum_dec =
                #record.pixel_resolution = 
                #record.priority = 
                #record.description =
                record.file_location = path
                session.add(record)

        #for moon in moon_dict.keys():
        #    record = Finders()
        #    record.object_name = moon
        #    record.x = moon_dict[moon]['delta_x']
        #    record.y = moon_dict[moon]['delta_y']
        #    session.add(record)

        #for record in session.query(Finders):
        #    print record.object_name, record.x, record.y

    session.commit()