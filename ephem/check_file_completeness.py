#! /usr/bin/env python

import datetime
import glob
import logging
import os
import time

from database_interface import session
from database_interface import Base
from database_interface import Finders
from database_interface import MasterFinders
from database_interface import MasterImages
from database_interface import SubImages

ARCHIVE_PATH = '/astro/3/mutchler/mt/drizzled'


def setup_logging():
    """Set up the logging."""
    module = 'check_file_completeness'
    log_file = os.path.join('/astro/3/mutchler/mt/logs/', module, 
        module + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.log')
    logging.basicConfig(filename = log_file,
        format = '%(asctime)s %(levelname)s: %(message)s',
        datefmt = '%m/%d/%Y %H:%M:%S %p',
        level = logging.INFO)


def check_file(filename):
    """Check is the file exists, print an error."""
    if not os.path.isfile(filename):
        print 'Missing: {}'.format(filename)


def check_file_completeness_main():
    """The main functin for the check_file_completeness module."""
    file_list = glob.glob(os.path.join(ARCHIVE_PATH, '*_*/*c0m.fits'))
    file_list = [item for item in file_list if len(item) == 59]

    logging.info('Checking in: {}'.format(ARCHIVE_PATH))
    logging.info('Found {} root c0m.fits files'.format(len(file_list)))

    counter = 0
    for c0m in file_list:

        file_dict = {}

        # Create the uncorrected FITS keys.
        file_dict['c0m'] = c0m
        file_dict['c1m'] = c0m.replace('_c0m.fits','_c1m.fits')
        file_dict['c0m_center_single'] = c0m.replace('.fits', '_center_single_sci.fits')
        file_dict['c0m_wide_single'] = c0m.replace('.fits', '_wide_single_sci.fits')

        # Create the corrected FITS keys.
        file_dict['cr_c0m'] = c0m.replace('_c0m.fits', '_cr_c0m.fits')
        file_dict['cr_c1m'] = file_dict['c1m'].replace('_c0m.fits', '_cr_c0m.fits')
        file_dict['cr_c0m_center_single'] = file_dict['c0m_center_single'].replace('_c0m.fits', '_cr_c0m.fits')
        file_dict['cr_c0m_wide_single'] = file_dict['c0m_wide_single'].replace('_c0m.fits', '_cr_c0m.fits')

        # Checking PNG keys.
        key_list = ['c0m_center_single', 'c0m_wide_single',
                    'cr_c0m_center_single', 'cr_c0m_wide_single']
        for key in key_list:
            file_dict[key + '_png'] = os.path.join(os.path.dirname(file_dict[key]), 'png', 
                           os.path.basename(file_dict[key].replace('.fits','_linear.png')))
        key_list = ['c0m_wide_single_png', 'cr_c0m_wide_single_png']
        for key in key_list:
            for i_image in range(1,13):
                file_dict[key + '_{}'.format(i_image)] = file_dict[key].replace('_linear', '_linear_{}'.format(i_image))

        # Check to see if the keys exist
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