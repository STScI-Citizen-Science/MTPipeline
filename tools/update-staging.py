#! /usr/bin/env python

'''
Update date the staging folder copies of the pngs.
'''

import argparse
import datetime
import glob
import os
import shutil

PATH_TO_FILES = '/astro/3/mutchler/mt/drizzled/[01]*/png/'
STAGING = '/astro/3/mutchler/mt/staging'

def update_staging_main(reproc=False):
    '''
    The main module.
    '''

    # Build the file lists.
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ': Buidling file list.'
    wide_list = glob.glob(os.path.join(PATH_TO_FILES, '*wide_single_sci_linear_*.png'))
    center_list = glob.glob(os.path.join(PATH_TO_FILES, '*center_single_sci_linear.png'))
    file_list = wide_list + center_list
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ': Checking ' + str(len(file_list)) + ' files.'
    count = 0
    
    # Loop over the file list.
    for filename in file_list:
        output_path = os.path.join(STAGING, filename.split('/')[-3])
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
            os.chmod(output_path, 0775)
        dst = os.path.join(output_path, filename.split('/')[-1])

        # Check for file existence if not reprocessing.
        if os.path.exists(dst):
            if reproc:
                os.remove(dst)
            else:
                continue
        shutil.copy(filename, dst)
        os.chmod(dst, 0664)
        count += 1
        if count % 1000 == 0:
            print datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ': Copied ' + str(count) + ' files'


def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Transfer the pngs to the staging area.')
    parser.add_argument(
        '-reproc',
        required = False,
        action = 'store_true',        
        default = False,
        dest = 'reproc',
        help = 'Overwrite existing files.')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    update_staging_main(args.reproc)