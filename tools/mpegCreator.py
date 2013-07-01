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

PATH = "/astro/3/mutchler/mt/drizzled" #default path to the images 

def parse_args():
    '''
    parse the command line arguemnts.
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
    1. All the wide images
    2. The cosmic ray rejected wide images
    3. The non-cosmic ray rejected wide images
    4. All the center images
    5. The cosmic ray rejected center images
    6. The non-cosmic ray rejected center images
    """
    global source
    path = os.path.join(path,'png')
    os.chdir(path)
    #for all wide images
    output = source + "AllWide.mp4" 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1', '-pattern_type',
                    'glob','-i','*wide*.png', output])
    #for the comsmic ray rejected wide images
    output = source + "CRWide.mp4" 
    subprocess.call(['ffmpeg','-f','image2','-r','1','-pattern_type',
                    'glob','-i','*cr*wide*.png', output])
    #for the non-cosmic ray rejected wide images
    output = source + "nonCRWide.mp4"
    #for all the center images
    output = source + "AllCenter.mp4" 
    subprocess.call(['ffmpeg','-f','image2','-r','1','-pattern_type',
                    'glob','-i','*center*.png', output])
    #for all the comsic ray rejected center images
    output = source + "CRCenter.mp4" 
    subprocess.call(['ffmpeg','-f','image2','-r','1','-pattern_type',
                    'glob','-i','*cr*center*.png', output])
    #for all the non-cosmic ray rejected center images
    output = source + "nonCRCenter.mp4"

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
                runScript(os.path.join(path, dirs)) #run the script for each subdir


args = parse_args()
source = args.source #get the source folder name (false if none)
currentDir = os.getcwd() #get the current working directory
createMovie(source) #run the movie script 

