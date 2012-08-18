#! /usr/env/bin python
'''
A script to run Astrodrizzle.
'''
import argparse
import drizzlepac
from drizzlepac import astrodrizzle
import glob
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

def prase_args():
    '''
    Prase the command line arguemnts.
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

def rename_files(rootfile,mode):
    '''
    Rename all the files that match the root of the filename input 
    paramater, excluding the input filename itself.
    '''
    # Build the file list.
    print rootfile
    rootfile = os.path.abspath(rootfile)
    basename = os.path.splitext(rootfile)[0]
    print basename
    search = basename + '_sci*'
    file_list_1 = glob.glob(search)
    search = basename + '_single*'
    file_list_2 = glob.glob(search)
    file_list = file_list_1 + file_list_2
    
    # Loop over the files and rename.
    for filename in file_list:
        dst = string.split(basename,'/')[-1] + '_' + mode 
        dst += string.split(filename,basename)[1]
        dst = os.path.join('/astro/3/mutchler/mt/drizzled/neptune', dst)       
        shutil.copyfile(filename,dst)
        os.remove(filename)

    # Generate and return the output list.
    search = basename + '*single_sci.fits'
    print search
    output_list = glob.glob(search)
    return output_list

# ------------------------------------------------------------------------------

def run_astrodrizzle(filename):
    '''
    '''
    configobj_list = [
        '/astro/3/mutchler/mt/code/cfg_files/z3_neptune_slice.cfg',
        '/astro/3/mutchler/mt/code/cfg_files/z3_neptune_wide.cfg',
        '/astro/3/mutchler/mt/code/cfg_files/z3_neptune_zoom.cfg']
        
    mode_list = [
        'slice',
        'wide',
        'zoom']
    for configobj, mode in zip(configobj_list, mode_list):
        print filename
        astrodrizzle.AstroDrizzle(
            input = filename,
            configobj = configobj)
        rename_files_output = rename_files(filename, mode)
            
# ------------------------------------------------------------------------------
# The main controller. 
# ------------------------------------------------------------------------------

def main(args):
    '''
    The main controller.
    '''
    archive_file_list = get_archive_file_list(args.target)
    move_files(args.target, archive_file_list, args.recopy)
    file_list = get_file_list(args.target)
    run_astrodrizzle(file_list)
    
# ------------------------------------------------------------------------------
# For command line execution.
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    args = prase_args()
    main(args)
    