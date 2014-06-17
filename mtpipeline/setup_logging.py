#! /usr/bin/env python

from mtpipeline.get_settings import SETTINGS

import datetime
import logging
import os
import time

from astropy import __version__ as astro_version
from numpy import __version__ as numpy_version
from slqalchemy import __version__ as sql_version
from PIL import VERSION as PIL_version
from getpass import getuser
from socket import gethostname
from platform import machine
from platform import platform
from platform import python_version
from multiprocessing import cpu_count
from psutil import virtual_memory

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
    logging.info('User: {0}'.format(getuser()))
    logging.info('Host: {0}'.format(gethostname()))
    logging.info('Machine: {0}'.format(machine()))
    logging.info('Platform: {0}'.format(platform()))
    logging.info('CPU Count: {0}'.format(cpu_count()))
    logging.info('Total Physical Memory: {0}GB'.format(virtual_memory().total/(1024**3)))
    logging.info('Python Version: {0}'.format(python_version()))
    logging.info('Astropy Version: {0}'.format(astro_version))
    logging.info('SQLAlchemy Version: {0}'.format(sql_version))
    logging.info('PIL Version: {0}'.format(PIL_version))