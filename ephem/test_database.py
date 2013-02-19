#! /usr/bin/env python

'''
Check to ensure that all the file counts are correct.
'''
import glob
import os

ARCHIVE = '/Users/viana/mtpipeline/archive'
output_string = '| {:30} | {:10} |'

def counter(search_string):
    file_count = len(glob.glob(search_string))
    search_name = search_string.split('/')[-1]
    print output_string.format(search_name, file_count)

print output_string.format(30 * '-', 10 * '-')
print output_string.format('FITS Files', 'Count')
print output_string.format(30 * '-', 10 * '-')
proposal_count = len(glob.glob(os.path.join(ARCHIVE, '*/')))
print output_string.format('Proposals', proposal_count)
c0m_list = glob.glob(os.path.join(ARCHIVE, '*/*c0m.fits'))
c0m_cr_list = [x for x in c0m_list if x.split('_')[2] == 'cr']
print output_string.format('CR Rejected c0m.fits ', len(c0m_cr_list))
c0m_count = len(c0m_list)
print output_string.format('c0m.fits', c0m_count)

search_list = ['*/*c1m.fits',
    '*/*wide_single_sci.fits',
    '*/*center_single_sci.fits',
    '*/*single_sci.fits']

for search_string in search_list:
    counter(os.path.join(ARCHIVE, search_string))
print output_string.format(30 * '-', 10 * '-')

print '\n'
print output_string.format(30 * '-', 10 * '-')
print output_string.format('PNG Files', 'Count')
print output_string.format(30 * '-', 10 * '-')


search_list = ['*/png/*linear.png',
    '*/png/*linear_*.png']

for search_string in search_list:
    counter(os.path.join(ARCHIVE, search_string))
print output_string.format(30 * '-', 10 * '-')
