#! /usr/bin/env python

from mtpipeline.get_settings import SETTINGS
import datetime
import logging
import os
import time

def setup_logging(module_name):
    """
        Set up the logging for the mtpipeline scripts.
        
        Parameters:
            module_name : string
        
        Returns:
            nothing
        
        Output:
            nothing
    """
    log_file = (module_name + '_' +
                datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') +
                '.log')
    log_file = os.path.join(SETTINGS['logging_path'], module_name, log_file)
    logging.basicConfig(filename = log_file,
                        format = '%(asctime)s %(levelname)s: %(message)s',
                        datefmt = '%m/%d/%Y %H:%M:%S %p',
                        level = logging.INFO)