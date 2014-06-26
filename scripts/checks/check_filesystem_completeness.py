#! /usr/bin/env python

from mtpipeline.get_settings import SETTINGS
from mtpipeline.setup_logging import setup_logging
from mtpipeline.imaging.imaging_pipeline import make_output_file_dict
from collections import defaultdict
import datetime
import glob
import logging
import os
import time

def check_filesystem_completeness_main():
    """
        The main function for the check_filesystem_completeness module.
        
        Parameters:
            nothing
        
        Returns:
            nothing
        
        Output:
            output: string
                information about files that are missing. Logged in log files.
                Example:
                'INFO: Checking in: /astro/3/mutchler/mt/drizzled/
                INFO: Found 10000 root c0m.fits files
                INFO: Found 500000 files
                INFO: List of missing files:
                11990_comet_hartley2 : cr_reject_output : 108
                11990_comet_hartley2 : drizzle_weight : 432
                11990_comet_hartley2 : drizzle_output : 432
                11990_comet_hartley2 : png_output : 3024
                06497_kbo : png_output : 1960
                11518_kbo_2003el61 : cr_reject_output : 20
                11518_kbo_2003el61 : drizzle_weight : 80
                11518_kbo_2003el61 : drizzle_output : 80
                11518_kbo_2003el61 : png_output : 560
                09585_kbo : png_output : 252
                
                Total: 6948 missing files'
        
    """
    all_files_list = glob.glob(os.path.join(SETTINGS['wfpc2_output_path'], '*_*/*c0m*.fits'))
    c0m_file_list = [filename for filename
                     in all_files_list
                     if len(filename.split('/')[-1]) == 18
                     and filename.split('/')[-1].split('_')[-1] == 'c0m.fits']
    all_files_list += glob.glob(os.path.join(SETTINGS['wfpc2_output_path'], '*_*/png/*c0m*.png'))
    files_set = set(all_files_list)
    
    logging.info('Checking in: {}'.format(SETTINGS['wfpc2_output_path']))
    logging.info('Found {} root c0m.fits files'.format(len(c0m_file_list)))
    logging.info('Found {} files'.format(len(all_files_list)))

    #  creating a dictionary to store the quantities of files that were found
    check_dict = {}
    found = 0
    for filename in c0m_file_list:
        proposal_folder = filename.split('/')[-2]
        if proposal_folder not in check_dict:
            check_dict[proposal_folder] = defaultdict(int)
        check_dict[proposal_folder]['input_file'] += 1
        file_dict = make_output_file_dict(filename)
        for key in file_dict.keys():
            if key != 'input_file':
                for file in file_dict[key]:
                    if file in files_set:
                        check_dict[proposal_folder][key] += 1
                        found += 1

    for mis in check_dict.keys():
        if 'drizzle_weight' not in check_dict[mis]:
            check_dict[mis]['drizzle_weight'] = 0
        if 'drizzle_output' not in check_dict[mis]:
            check_dict[mis]['drizzle_output'] = 0
        if 'cr_reject_output' not in check_dict[mis]:
            check_dict[mis]['cr_reject_output'] = 0
        if 'png_output' not in check_dict[mis]:
            check_dict[mis]['png_output'] = 0

    # creating a dictionary to store the quantities of missing files
    check_missing = {}
    for key1 in check_dict.keys():
        check_missing[key1] = {}
        check_missing[key1]['input_file'] = 0
        for key2 in check_dict[key1].keys():
            if key2 == 'cr_reject_output':
                check_missing[key1][key2] = 2*check_dict[key1]['input_file'] - check_dict[key1][key2]
            elif key2 == 'drizzle_output':
                check_missing[key1][key2] = 4*check_dict[key1]['input_file'] - check_dict[key1][key2]
            elif key2 == 'drizzle_weight':
                    check_missing[key1][key2] = 4*check_dict[key1]['input_file'] - check_dict[key1][key2]
            elif key2 == 'png_output':
                check_missing[key1][key2] = 28*check_dict[key1]['input_file'] - check_dict[key1][key2]

    missing = 0
    missing_list = ''
    for mis in check_missing.keys():
        for key in check_missing[mis].keys():
            if check_missing[mis][key] != 0:
                missing_list += '{} : {} : {}\n'.format(mis, key, check_missing[mis][key])
                missing += check_missing[mis][key]

    if len(missing_list) > 0:
        logging.info('List of missing files:\n{}'.format(missing_list).strip())
    logging.info('Missing: {} files'.format(missing))
    logging.info('Found: {} files'.format(found))

if __name__ == '__main__':
    setup_logging('check_file_completeness')
    t1 = time.time()
    check_filesystem_completeness_main()
    t2 = time.time()
    logging.info('Ran in {} s'.format(int(float(t2 - t1))))