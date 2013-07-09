"""
File: mpegCreator.py
Date: July 1st, 2013
Project: MT Pipeline
Organisation: Space Telescope Science Institute

Utility to automatically create mpeg movies from png images. Uses 
subprocess module calls to the ffmpeg application.

"""

import argparse 
import subprocess 
import os 


PATH = "/astro/3/mutchler/mt/drizzled" #image path

def parse_args():
    '''
    parse the command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description = 'Create mpeg movies from pngs using ffmpeg')
    parser.add_argument(
        '-source',
        '-s',
        required = False,        
        default = False,
        help = 'carry out operation for the specified folder only')
    args = parser.parse_args()
    return args

def buildMovies(movieType, path):
    """
    makes a subprocess call to the ffmpeg tool to create the movies.
    """
    SOURCE=path.split('/')[6]
    temp = os.path.join(PATH, 'temp')
    listDir = os.listdir(path)

    output = os.path.join(PATH, "movies", "temp", SOURCE + "All" + movieType + ".mp4") 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1',
                    '-pattern_type', 'glob', '-i','*'+ movieType + '*linear.png',
                    output])
    #for the comsmic ray rejected images   
    output = os.path.join(PATH, "movies", "temp", SOURCE + "CR" + movieType + ".mp4") 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1',
                    '-pattern_type', 'glob', '-i', '*cr*' + movieType + '*linear.png',
                    output])
    #for the non-cosmic ray rejected images
    output = os.path.join(PATH, "movies", "temp", SOURCE + "nonCR" + movieType + ".mp4") 
    #make a list of non-CR rejected images
    nonCRWideInput = [i for i in listDir if movieType in i and'linear' in i and 'cr' not in i]
    #copy all the non-CR rejected images to the temp directory
    for files in nonCRWideInput:
        subprocess.call(['cp', files, temp])
    os.chdir(temp) 
    #carry out the ffmpeg script for our copied files
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1',
                '-pattern_type', 'glob', '-i','*'+ movieType + '*linear.png',
                output])
    subprocess.call('rm *.png', shell=True) #delete the temporary files 
    os.chdir(path) #change back to our PATH


def runScript(path):
    '''
    run scripts for both center and wide images
    '''
    path = os.path.join(path,'png')
    try:
        os.chdir(path)
    except:
        return 
    buildMovies('wide', path)
    buildMovies('center', path)
    
def createMovie():
    """
    parses whether the script is to be run for a particular subfolder or
    all the subfolders and calls the runScript function accordingly.
    If no subfolder given calls runScript iteratively on all subfolders.
    """
    path = PATH 
    if SOURCE: #add sub-directory to path if given
        path = PATH + '/' + SOURCE
        runScript(path)
    else: #else carry out operation for ALL sub-drectories
        for dirs in os.listdir(path):
            if dirs[0].isdigit():
                path = PATH + '/' + dirs
                runScript(path)


if __name__ == '__main__':
    args = parse_args() 
    SOURCE = args.source 
    createMovie() 