#! /usr/env/bin python
'''
A script to run Astrodrizzle.
'''
import argparse
from drizzlepac import astrodrizzle
from astropy.io import fits
import glob
import inspect
import os
import string
import shutil

# ------------------------------------------------------------------------------
# Low-level Functions (alphabetical)
# ------------------------------------------------------------------------------

def get_archive_file_list(target):
    '''
    Get a list of the absolute paths to the fits files located in
    /astro/3/mutchler/mt/archive.
    '''
    target = target.lower()
    root = '/astro/3/mutchler/mt/archive'
    search = os.path.join(root, '*' + target + '*')
    path_list = glob.glob(search)
    file_list = []
    for path in path_list:
        search = os.path.join(path, '*c0m.fits')
        temp_file_list = glob.glob(search)
        file_list.extend(temp_file_list)
    
    return file_list

# ------------------------------------------------------------------------------

def get_file_list(target):
    '''
    Get the local list of files.
    ''' 
    target = target.lower()
    search = os.path.join('/astro/3/mutchler/mt/drizzled', target, '*c0m.fits')
    file_list = glob.glob(search)
    
    return file_list
    
# ------------------------------------------------------------------------------

def insert_dateobs(output, dateobs):
    """ Put the DATE-OBS keyword back into the AstroDrizzle outputs.
    AstroDrizzle removes this keyword, and it is needed for the database and
    ephemeris later. 

    Parameters: 
        output: string
                The renamed AstroDrizzle output the DATE-OBS keyword needs to be
                put back into.
        dateobs: string
                 The value of the dateobs keyword from the original _flt or _c0m
                 file.

    Returns: nothing

    Outputs:
        The AstroDrizzle output file, edited to include DATE-OBS.
    """

    # Since we are changing only a single keyword, using the convenience
    # function is permissible.
    fits.setval(filename = output,
                keyword = 'date-obs',
                value = dateobs)

# ------------------------------------------------------------------------------
    
def move_files(target, file_list, recopy_switch):
    '''
    Move the files.
    '''
    target = target.lower()
       
    dst_root = os.path.join('/astro/3/mutchler/mt/drizzled', target)
    if os.access(dst_root, os.F_OK) == False:
        os.mkdir(dst_root)
        
    for filename in file_list:
        rootname = os.path.basename(filename)
        dst = os.path.join(dst_root, rootname)
        if os.access(dst, os.F_OK) != True or recopy_switch == True:
            print 'Copying: ' + filename + ' -> ' + dst
            shutil.copyfile(filename, dst)

# ------------------------------------------------------------------------------

def rename_files(rootfile, output):
    '''
    Rename all desirable files that match the root of the filename input 
    paramater, excluding the input filename itself. Remove all other
    AstroDrizzle outputs.
    '''
    print 'Renaming Files:'
    
    rootfile = os.path.abspath(rootfile)

    # Remove unwanted AstroDrizzle outputs
    search = rootfile[:-8] + '*mask*'
    bad_list = glob.glob(search)
    search = rootfile[:-8] + '*c0m_d2im*'
    bad_list = bad_list + glob.glob(search)
    for filename in bad_list:
        print "Removing " ,filename
        os.remove(filename)

    # Find the wanted files
    search = rootfile[:-8] + '*single_sci.fits'
    sci_list = glob.glob(search)
    search = rootfile[:-8] + '*single_wht.fits'
    wht_list = glob.glob(search)
    # Loop over the wanted files and rename.
    for filename in sci_list:
        print "Renaming ",filename, " to ",output
        os.rename(filename,output)
    for filename in wht_list:
        output = output.replace('_sci','_wht')
        output = output.replace('_img','_wht')
        print "Renaming ",filename, " to ",output
        os.rename(filename,output)

# ------------------------------------------------------------------------------

def run_astrodrizzle(filename, output, detector, dateobs):
    '''
    Executes astrodrizzle.AstroDrizzle.
    '''
    cfg_path = os.path.realpath(__file__)
    if '.pyc' in cfg_path:
        cfg_path = cfg_path.replace('/mtpipeline/imaging/run_astrodrizzle.pyc',
                                '/astrodrizzle_cfg/')
    else:
        cfg_path = cfg_path.replace('/mtpipeline/imaging/run_astrodrizzle.py',
                                '/astrodrizzle_cfg/')

    config_sets = {'WFPC2' : 'wfpc2_wideslice.cfg',
                   'WFC' : 'acs_wide.cfg',
                   'HRC' : 'acs_hrc_wide.cfg',
                   'SBC' : 'acs_wide.cfg',
                   'UVIS':'wfc3_wide.cfg',
                   'IR': 'wfc3_ir_wide.cfg'
                  }

    config_file = os.path.join(cfg_path, config_sets[detector])
    astrodrizzle.AstroDrizzle(input = filename, configobj = config_file)
    rename_files(filename, output)
    insert_dateobs(output, dateobs)
            
# ------------------------------------------------------------------------------
# The main controller. 
# ------------------------------------------------------------------------------

def main(target, recopy):
    '''
    The main controller.
    '''
    archive_file_list = get_archive_file_list(target)
    move_files(target, archive_file_list, recopy)
    file_list = get_file_list(target)
    run_astrodrizzle(file_list)
    
# ------------------------------------------------------------------------------
# For command line execution.
# ------------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'A script to run Astrodrizzle.' )
    parser.add_argument(
        '-target', 
        required = True,
        help = 'Target name, e.g. "vesta"')
    parser.add_argument(
        '-recopy',
        action = 'store_true',
        required = False,
        help = 'Recopy the c0m.fits file to the drizzled area.')
    args = parser.parse_args()        
    return args
    
# ------------------------------------------------------------------------------
        
if __name__ == '__main__':
    args = parse_args()
    main(args.target, args.recopy)
    
