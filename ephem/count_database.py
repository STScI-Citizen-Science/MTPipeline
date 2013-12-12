#! /usr/bin/env python

'''
Check to ensure that all the file counts are correct.
'''
import glob
import os

#----------------------------------------------------------------------------
# Load all the SQLAlchemy ORM bindings
#----------------------------------------------------------------------------

from database_interface import session
from database_interface import Base
from database_interface import Finders
from database_interface import MasterFinders
from database_interface import MasterImages
from database_interface import SubImages

#----------------------------------------------------------------------------
# Global Variables
#----------------------------------------------------------------------------

ARCHIVE = '/astro/3/mutchler/mt/drizzled'
OUTPUT_FILE = '/Users/viana/Dropbox/Work/MTPipeline/Other/project_status.txt'
OUTPUT_STRING = '| {:35} | {:8} |\n'
BORDER_STRING = '+ {:35} + {:8} +\n'
PLANET_LIST = ['mars', 'neptune', 'saturn', 'uranus', 'jupiter']

#----------------------------------------------------------------------------
# Functions
#----------------------------------------------------------------------------

def count_files(search_string, file_object):
    file_count = len(glob.glob(search_string))
    search_name = search_string.replace(ARCHIVE,'')
    file_object.write(OUTPUT_STRING.format(search_name, file_count))


def table_generator(search_list, catagory_name, count_name, file_object):
    '''
    Generate a Table.
    '''
    file_object.write(BORDER_STRING.format(35 * '-', 8 * '-'))
    file_object.write(OUTPUT_STRING.format(catagory_name, count_name))
    file_object.write(BORDER_STRING.format(35 * '-', 8 * '-'))
    for search_string in search_list:
        count_files(os.path.join(ARCHIVE, search_string), file_object)
    file_object.write(BORDER_STRING.format(35 * '-', 8 * '-'))
    file_object.write('\n')    


def count_records():
    pass


def count_moons():
    '''
    Given the number of moons per planet based on the contents of the 
    planets_and_moons.txt text file.
    '''
    with open('/Users/viana/Dropbox/Work/MTPipeline/Code/ephem/planets_and_moons.txt', 'r') as f:
        data = f.readlines()
    data = [item.strip().split() for item in data]
    moon_count_dict = {}
    new_planet = True
    for item in data:
        if new_planet:
            planet = item[1]
            moon_count_dict[planet] = 1
            new_planet = False
        elif item == []:
            new_planet = True
        else:
            moon_count_dict[planet] += 1
    return moon_count_dict

#----------------------------------------------------------------------------
# Comand Line Execution
#----------------------------------------------------------------------------

if __name__ == '__main__':
    f = open(OUTPUT_FILE, 'w')
    search_list = ['*/']
    for planet in PLANET_LIST:
        search_list.append('*' + planet + '/')
    table_generator(search_list, 'Proposals', 'Count', f)

    search_list = ['*/*c0m.fits']
    for planet in PLANET_LIST:
        search_list.append('*' + planet + '/*c0m.fits')
    table_generator(search_list, 'c0m.fits Files by Target', 'Count', f)

    search_list = ['*/*c0m.fits',
        '*/*c1m.fits',
        '*/*cr*c0m.fits',
        '*/*wide_single_sci.fits',
        '*/*center_single_sci.fits',
        '*/*single_sci.fits']
    table_generator(search_list, 'Total Fits Files', 'Count', f)

    search_list = ['*/*single_sci.fits']
    for planet in PLANET_LIST:
        search_list.append('*' + planet + '/*single_sci.fits')
    table_generator(search_list, '*single_sci.fits Files by Target', 'Count', f)   

    search_list = ['*/png/*linear.png',
        '*/png/*wide*linear.png',
        '*/png/*center*linear.png']
    table_generator(search_list, 'Master PNG Files', 'Count', f)

    search_list = ['*/png/*linear_*.png',
        '*/png/*wide*linear_*.png']
    table_generator(search_list, 'Subimage PNG Files', 'Count', f)

    moon_count_dict = count_moons()
    f.write(BORDER_STRING.format(35 * '-', 8 * '-'))
    f.write(OUTPUT_STRING.format('Planet', 'Moons'))
    f.write(BORDER_STRING.format(35 * '-', 8 * '-'))
    for key in moon_count_dict:
        f.write(OUTPUT_STRING.format(key, moon_count_dict[key]))
    f.write(BORDER_STRING.format(35 * '-', 8 * '-'))
    f.write('\n')  

    table_class_list = [Finders, MasterFinders, MasterImages, SubImages]
    for table_class in table_class_list:
        f.write(BORDER_STRING.format(35 * '-', 8 * '-'))
        f.write(OUTPUT_STRING.format(table_class.__tablename__, 'Records'))
        f.write(BORDER_STRING.format(35 * '-', 8 * '-'))
        field_list = table_class.__table__.columns
        for field in field_list:
            f.write(OUTPUT_STRING.format(field, session.query(table_class).filter(field != None).count()))
        f.write(BORDER_STRING.format(35 * '-', 8 * '-'))
        f.write('\n')
    f.close()

