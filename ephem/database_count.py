#! /usr/bin/env python

from collections import defaultdict
import pprint
import sys
import yaml

from database_interface import session
from database_interface import Base
from database_interface import Finders
from database_interface import MasterFinders
from database_interface import MasterImages
from database_interface import SubImages


def get_target_name(item):
    """Take a query record, split the name field, and return the 
    target name."""
    return item.file_location.split('/')[-2].split('_')[-1]


def print_dict(input_dict):
    """Print the contents of the counting dictionaries."""
    for target in input_dict:
        print target
        for key in input_dict[target]:
            print '\t{}: {}'.format(key, input_dict[target][key])

fits_count_dict = {'mars': defaultdict(int), 
                   'saturn':defaultdict(int), 
                   'neptune':defaultdict(int)}


def get_fits_count():
    """Get FITS Count from master_images table."""
    fits_query = session.query(MasterImages).all()
    for item in fits_query:
        target = get_target_name(item)
        fits_count_dict[target]['fits_count'] += 1
        if item.name.split('_')[1] == 'cr':
            fits_count_dict[target]['cr_count'] += 1
        elif item.name.split('_')[1] == 'c0m':
            fits_count_dict[target]['no_cr_count'] += 1
        else:
            print 'Derp!'
            break
    print '\nFITS Count from master_images table.'
    print_dict(fits_count_dict)


def get_subimages_count():
    """Get Subimage count from subimages table."""
    subimages_query = session.query(MasterImages, SubImages).\
        join(SubImages, SubImages.master_images_id == MasterImages.id)\
        .all()
    subimage_count_dict = {'mars': defaultdict(int), 
                           'saturn':defaultdict(int), 
                           'neptune':defaultdict(int)}
    for record in subimages_query:
        target = get_target_name(record.MasterImages)
        subimage_count_dict[target]['total_records'] += 1
    for key in subimage_count_dict:
        subimage_count_dict[key]['expected_records'] = fits_count_dict[key]['fits_count'] * 13
    print '\nSubimage count from subimages table.'
    print_dict(subimage_count_dict)


def get_moon_count():
    """Get moon count from master_finders table."""
    ephemeris_query = session.query(MasterFinders, MasterImages)\
        .join(MasterImages, MasterImages.id == MasterFinders.master_images_id)\
        .all()
    #    .filter(MasterFinders.ephem_x >= 0)\
    #    .filter(MasterFinders.ephem_y >= 0)\
    #    .filter(MasterFinders.ephem_x <= 1725)\
    #    .filter(MasterFinders.ephem_y <= 1300)\
    #    .filter(MasterImages.drz_mode == 'wide')\

    moons_per_planet_dict = {'neptune':14, 
                             'pluto':5, 
                             'jupiter':68, 
                             'uranus':28, 
                             'mars':3, 
                             'saturn':62}

    moon_count_dict = {'mars': defaultdict(int), 
                       'saturn':defaultdict(int), 
                       'neptune':defaultdict(int)}
    for item in ephemeris_query:
        target = get_target_name(item.MasterImages)
        if item.MasterFinders.ephem_x != None and item.MasterFinders.ephem_y != None:
            moon_count_dict[target]['complete_records'] += 1
        moon_count_dict[target]['total_records'] += 1
    for key in moon_count_dict:
        moon_count_dict[key]['expected_records'] = moons_per_planet_dict[key] * fits_count_dict[key]['fits_count']
    print '\nMoon count from master_finders table.'
    print_dict(moon_count_dict)

if __name__ == '__main__':
    get_fits_count()
    get_subimages_count()
    get_moon_count()
