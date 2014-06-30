"""Script for executing the imaging_pipeline.
    
    This module is used to execute the mtpipeline.imaging_pipeline code.
    It contains the logic for parsing the command line arguments, logging
    the execution, an email decorator to send out a end of script message,
    and a try/execpt loop to catch exceptions.
    
    Authors:
    Alex Viana, April 2014
"""

from mtpipeline.imaging.imaging_pipeline import imaging_pipeline
from mtpipeline import email_decorator
from mtpipeline.setup_logging import setup_logging

import multiprocessing as mp
import glob
import argparse
import logging
import os
import sys

num_cores = mp.cpu_count() - 1

def parse_args():
    """
        Parse the input arguments using `argparse` module.
        
        Parameters:
        nothing
        
        Returns:
        args : an instance of the class returned by
        `parser.parse_args` with the arguments as instance attributes.
        
        Outputs:
        nothing
    """
    parser = argparse.ArgumentParser(
    description = 'Run the moving target pipeline.' )
    parser.add_argument(
        '-filelist',
        required = True,
        help = 'Search string for files. Wildcards accepted.')
    parser.add_argument(
        '-output_path',
        required = False,
        help = 'Set the path for the output. Default is the input directory.')
    parser.add_argument(
        '-no_cr_reject',
        required = False,
        action='store_false',
        default = True,
        dest = 'cr_reject',
        help = 'Toggle off the cosmic ray rejection step.')
    parser.add_argument(
        '-no_astrodrizzle',
        required = False,
        action='store_false',
        default = True,
        dest = 'astrodrizzle',
        help = 'Toggle off the astrodrizzle step.')
    parser.add_argument(
        '-no_png',
        required = False,
        action = 'store_false',
        default = True,
        dest = 'png',
        help = 'Toggle off the png step.')
    parser.add_argument(
        '-reproc',
        required = False,
        action = 'store_true',
        default = False,
        dest = 'reproc',
        help = 'Reprocess all files, even if outputs already exist.')
    args = parser.parse_args()
    return args


def run_imaging_pipeline(filename):
    """
        The script for executing the imaging_pipeline function.
        
        This function is the wrapper for the `imaging_pipeline` function
        in `mtpipeline`. It adds logging information and parses the
        command line arguments returned by `parse_args`. Completion emails
        are added by the `email_decorator` function.
        
        Parameters:
        nothing
        
        Returns:
        nothing
        
        Outputs:
        The outputs of this are the same as the wrapped
        `imaging_pipeline`.
    """
    logging.info("Current File: " + filename)
    try:
        imaging_pipeline(filename,
                         output_path =  args_list.output_path,
                         cr_reject_switch = args_list.cr_reject,
                         astrodrizzle_switch = args_list.astrodrizzle,
                         png_switch = args_list.png,
                         reproc_switch = args_list.reproc)
        logging.info("Completed: " + filename)
    except Exception as err:
        logging.critical('{0} {1} {2}'.format(
                                              type(err), err.message, sys.exc_traceback.tb_lineno))

@email_decorator.email_decorator
def run():
    """
        """
    logging.info("Command-line arguments used:")
    for arg in args_list.__dict__:
        logging.info(arg + ": " + str(args_list.__dict__[arg]))
    rootfile_list = glob.glob(args_list.filelist)
    rootfile_list = [filename for filename
                     in rootfile_list
                     if len(filename.split('/')[-1]) == 18
                     and filename.split('/')[-1].split('_')[-1] == 'c0m.fits']
    assert rootfile_list != [], 'empty rootfile_list in mtpipeline.py.'
    logging.info("Processing: {} files".format(len(rootfile_list)))
    logging.info("Number of Processes: {}".format(num_cores))
    pool = mp.Pool(processes=num_cores)
    pool.map(run_imaging_pipeline, rootfile_list)
    logging.info("Script completed")

if __name__ == '__main__':
    setup_logging('run_imaging_pipeline')
    args_list = parse_args()
    run()
    organize_logfiles(log_file, num_cores)