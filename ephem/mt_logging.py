"""
This module contains the basic logging setup for the project.
"""

import datetime
import logging
import os

def setup_logging(module):
    """Set up the logging."""
    log_file = os.path.join('/astro/3/mutchler/mt/logs/', module, 
        module + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.log')
    logging.basicConfig(filename = log_file,
        format = '%(asctime)s %(levelname)s: %(message)s',
        datefmt = '%m/%d/%Y %H:%M:%S %p',
        level = logging.INFO)