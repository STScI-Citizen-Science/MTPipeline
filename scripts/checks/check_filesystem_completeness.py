#! /usr/bin/env python

from mtpipeline.get_settings import SETTINGS
from mtpipeline.setup_logging import setup_logging
from mtpipeline.imaging.imaging_pipeline import make_output_file_dict
import datetime
import glob
import logging
import os
import time

def check_filesystem_completeness_main():
    """The main functin for the check_filesystem_completeness module."""
    all_fits_file_list = glob.glob(os.path.join(SETTINGS['wfpc2_output_path'], '*_*/*.fits'))
    c0m_file_list = [filename for filename in all_fits_file_list if filename.split('/')[-1].split('_')[-1] == 'c0m.fits']
    all_fits_file_list += glob.glob(os.path.join(SETTINGS['wfpc2_output_path'], '*_*/png/*.png'))
    fits_set = set(all_fits_file_list)
    
    logging.info('Checking in: {}'.format(SETTINGS['wfpc2_output_path']))
    logging.info('Found {} root c0m.fits files'.format(len(all_fits_file_list)))
    
    counter = 0
    for filename in c0m_file_list:
        file_dict = make_output_file_dict(filename)
        for file in file_dict.itervalues():
            if type(file) == 'str':
                if file in fits_set:
                    counter += 1
            else:
                for item in file:
                    if item in fits_set:
                        counter += 1

    logging.info('Checked {} files'.format(counter))

if __name__ == '__main__':
    setup_logging()
    t1 = time.time()
    check_filesystem_completeness_main()
    t2 = time.time()
    logging.info('Ran in {} s'.format(int(float(t2 - t1))))