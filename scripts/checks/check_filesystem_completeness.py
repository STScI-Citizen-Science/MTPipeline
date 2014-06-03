#! /usr/bin/env python

from mtpipeline.get_settings import SETTINGS
from mtpipeline.setup_logging import setup_logging
from mtpipeline.imaging.imaging_pipeline import make_output_file_dict
import datetime
import glob
import logging
import os
import time

def check_file(filename):
    """Check is the file exists, print an error."""
    if not os.path.isfile(filename):
        print 'Missing: {}'.format(filename)


def check_file_completeness_main():
    """The main functin for the check_file_completeness module."""
    file_list = glob.glob(os.path.join(SETTINGS['wfpc2_output_path'], '*_*/*c0m.fits'))
    file_list = [item for item in file_list if len(item) == 59]
    
    logging.info('Checking in: {}'.format(SETTINGS['wfpc2_output_path']))
    logging.info('Found {} root c0m.fits files'.format(len(file_list)))
    
    counter = 0
    for c0m in file_list:
        file_dict = make_output_file_dict(c0m)
                    
        # Check to see if the files exist
        for value in file_dict.itervalues():
            check_file(value)
            counter += 1
    
    logging.info('Checked {} files'.format(counter))

if __name__ == '__main__':
    setup_logging()
    t1 = time.time()
    check_file_completeness_main()
    t2 = time.time()
    logging.info('Ran in {} s'.format(int(float(t2 - t1))))