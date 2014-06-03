#! /usr/bin/env python

from mtpipeline.get_settings import SETTINGS
import datetime
import logging
import os
import time

def setup_logging():
    """Set up the logging."""
    module = 'check_file_completeness'
    log_file = os.path.join(SETTINGS['logging_path'], module,
                            module + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.log')
    logging.basicConfig(filename = log_file,
                        format = '%(asctime)s %(levelname)s: %(message)s',
                        datefmt = '%m/%d/%Y %H:%M:%S %p',
                        level = logging.INFO)

if __name__ == "__main__":
    setup_logging()