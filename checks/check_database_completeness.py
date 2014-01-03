#! /usr/bin/env python

import datetime
import logging
import os
import socket

from ..database.database_interface import session
from ..database.database_interface import Base
from ..database.database_interface import Finders
from ..database.database_interface import MasterFinders
from ..database.database_interface import MasterImages
from ..database.database_interface import SubImages


MOONS_PER_PLANET_DICT = {'neptune':14, 
                         'pluto':5, 
                         'jupiter':68, 
                         'uranus':28, 
                         'mars':3, 
                         'saturn':62}

def get_target_name(item):
    """Take a query record, split the name field, and return the 
    target name."""
    return item.file_location.split('/')[-2].split('_')[-1]


def setup_logging():
    """Set up the logging."""
    module = 'check_database_completeness'
    log_file = os.path.join('/astro/3/mutchler/mt/logs/', module, 
        module + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.log')
    logging.basicConfig(filename = log_file,
        format = '%(asctime)s %(levelname)s: %(message)s',
        datefmt = '%m/%d/%Y %H:%M:%S %p',
        level = logging.INFO)


def check_database_completeness_main():
	"""The main function for the module."""
	logging.info('Host is {}'.format(socket.gethostname()))
	master_images_query = session.query(MasterImages).all()
	logging.info('{} records found in master_images'.\
		format(len(master_images_query)))
	for record in master_images_query:
		target_name = get_target_name(record)
		master_finders_count = session.query(MasterFinders).\
			filter(MasterFinders.master_images_id == record.id).count()
		if master_finders_count != MOONS_PER_PLANET_DICT[target_name]:
			logging.error('Expected {} moons for {} got {}'.\
				format(MOONS_PER_PLANET_DICT[target_name], 
					os.path.join(record.file_location, record.name), 
					master_finders_count))

if __name__ == '__main__':
	setup_logging()
	check_database_completeness_main()
