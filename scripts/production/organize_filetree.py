import glob
import os
import sys
import shutil
from astropy.io import fits
from mtpipeline.get_settings import SETTINGS

def organize_filetree(path):
    """
        Organizes the new files, copying them to their new folders.
        
        Parameters:
            input: path
                The folder in which the files will be organized.
        
        Returns:
            nothing
        
        Output:
            nothing
    """
    all_files_list = glob.glob(os.path.join(path, '*.fits'))
    all_files_set = set(all_files_list)
    for fits_file in all_files_set:
        with fits.open(fits_file) as hdulist:
            proposed_folder = '{}_{}'.format(hdulist[0].header['PROPOSID'], hdulist[0].header['TARGNAME'])
            proposed_path = os.path.join(path, proposed_folder)
            rootname = os.path.basename.split('_')[0]
            if not os.path.exists(proposed_path):
                os.mkdir(proposed_path)
                shutil.copy2(fits_file, proposed_path)
            elif not os.path.exists(proposed_path + rootname):
                shutil.copy2(fits_file, proposed_path)

if __name__ == '__main__':
    organize_filetree(SETTINGS['wfc3_input_path'])
    organize_filetree(SETTINGS['acs_input_path'])