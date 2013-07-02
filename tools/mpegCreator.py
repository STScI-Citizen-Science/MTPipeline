"""
File: mpegCreator.py
Date: July 1st, 2013
Project: MT Pipeline
Organisation: Space Telescope Science Institute

Utility to automatically create mpeg movies from png images. Uses 
subprocess module calls to the ffmpeg application.

Arguments: 
-source [-s] for carrying out the script on a 
particular sub-directory only
"""

import argparse #module for parsing command-line arguments easily
import subprocess #subprocess module to execute external modules
import os #the standard os module for folder and file operations
import shutil #module with high level file operations 

PATH = "/astro/3/mutchler/mt/drizzled" #default path to the images 

def parse_args():
    '''
    parse the command line arguemnts. uses argparse module.
    '''
    parser = argparse.ArgumentParser(
        description = 'Create mpeg movies from pngs using ffmpeg')
    parser.add_argument(
        '-name',
        '-n',
        required = False,        
        default = False,
        help = 'include the name of the objects in the output video')
    parser.add_argument(
        '-source',
        '-s',
        required = False,        
        default = False,
        help = 'carry out operation for the specified folder only')
    args = parser.parse_args()
    return args

def runScript(path):
    """
    makes a subprocess call to the ffmpeg tool to create 6 different movies:
    1. All the wide images (<source>.AllWide.mp4)
    2. The cosmic ray rejected wide images(<source>.CRWide.mp4)
    3. The non-cosmic ray rejected wide images(<source>.nonCRWide.mp4)
    4. All the center images (<source>.AllCenter.mp4)
    5. The cosmic ray rejected center images (<source>.CRCenter.mp4)
    6. The non-cosmic ray rejected center images (<source>.nonCRCenter.mp4)
    """
    global source
    temp=os.path.join(PATH, 'temp')
    path = os.path.join(path,'png')
    os.chdir(path)
    listDir=os.listdir(path)
    #for all wide images
    output = os.path.join(PATH,"movies", source + "AllWide.mp4") 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1',
                    '-pattern_type', 'glob', '-i','*wide*.png',
                    output])
    #for the comsmic ray rejected wide images   
    output = os.path.join(PATH,"movies", source + "CRWide.mp4") 
    subprocess.call(['ffmpeg', '-f',' image2', '-r', '1',' -pattern_type',
                    'glob', '-i', '*cr*wide*.png', output])
    #for the non-cosmic ray rejected wide images
    output = os.path.join(PATH,"movies", source + "nonCRWide.mp4") 
    #make a list of non-CR rejected wide images
    nonCRWideInput=[i for i in listDir if 'wide' in i and 'cr' not in i]
    #copy all the non-CR rejected wide images to the temp directory
    for files in nonCRWideInput:
        subprocess.call(['cp', files, temp])
    os.chdir(temp) #change to temp directory
    #carry out the ffmpeg script for our copied files
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1', '-pattern_type',
                   'glob', '-i', '*.png', output])
    subprocess.call('rm *.png', shell=True) #delete the temporary files 
    os.chdir(path) #change back to our PATH
    #for all the center images
    output = os.path.join(PATH,"movies", source + "AllCenter.mp4") 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1', '-pattern_type',
                    'glob', '-i', '*center*.png', output])
    #for all the comsic ray rejected center images
    output = os.path.join(PATH,"movies", source + "CRCenter.mp4") 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1', '-pattern_type',
                    'glob', '-i', '*cr*center*.png', output])
    #for all the non-cosmic ray rejected center images
    output = os.path.join(PATH,"movies", source + "nonCRCenter.mp4") 
    #make a list of non-CR rejected center images
    nonCRCenterInput=[i for i in listDir if 'center' in i and 'cr' not in i]
    #copy all the non-CR rejected center images to the temp directory
    for files in nonCRCenterInput:
        subprocess.call(['cp', files, temp])
    os.chdir(temp) #change to temp directory
    #carry out the ffmpeg script for our copied files
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1', '-pattern_type',
                   'glob', '-i', '*.png', output])
    subprocess.call('rm *.png', shell=True) #delete the temporary files 
    os.chdir(path) #change back to our PATH
def createMovie(source):
    """
    parses whether the script is to be run for a particular subfolder or
    all the subfolders and calls the runScript function accordingly.
    If no subfolder given calls runScript iteratively on all subfolders.
    """
    path = PATH #path to default path
    if source != False: #add sub-directory to path if given
        path = PATH + '/' + source
        runScript(path)
    else: #else carry out operation for ALL sub-drectories
        for dirs in os.listdir(path): 
            if os.path.isdir(os.path.join(path, dirs)):
                runScript(os.path.join(path, dirs)) #run script on subdirs

if __name__ == '__main__':
    args = parse_args() #parse the input arguments
    source = args.source #get the source folder name (false if none)
    currentDir = os.getcwd() #get the current working directory
    createMovie(source) #run the movie script 

