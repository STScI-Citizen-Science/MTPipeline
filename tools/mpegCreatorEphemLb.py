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

#add logs to this and the original

ROOTPATH = "/astro/3/mutchler/mt/drizzled" #image path

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

def buildMovies(movieType, path, scaleType):
    """
    makes a subprocess call to the ffmpeg tool to create the movies.
    """
    source=path.split('/')[6]
    temp = os.path.join(ROOTPATH, 'temp')
    listDir = os.listdir(path)

    output = os.path.join(ROOTPATH, "movies", "temp", source + "All" + movieType + scaleType + "_ephem_lb.mp4") 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1',
                    '-pattern_type', 'glob', '-i','*'+ movieType + '*'+ scaleType + '_ephem_lb.png',
                    output])
    #for the comsmic ray rejected images   
    output = os.path.join(ROOTPATH, "movies", "temp", source + "CR" + movieType + scaleType + "_ephem_lb.mp4") 
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1',
                    '-pattern_type', 'glob', '-i', '*cr*' + movieType + '*' + scaleType + '_ephem_lb.png', 
                    output])
    #for the non-cosmic ray rejected images
    output = os.path.join(ROOTPATH, "movies", "temp", source + "nonCR" + movieType + scaleType + "_ephem_lb.mp4") 
    #make a list of non-CR rejected images
    nonCRWideInput = [i for i in listDir if movieType in i and scaleType + '_ephem_lb' in i and 'cr' not in i]
    #copy all the non-CR rejected images to the temp directory
    for files in nonCRWideInput:
        subprocess.call(['cp', files, temp])
    os.chdir(temp) 
    #carry out the ffmpeg script for our copied files
    subprocess.call(['ffmpeg', '-f', 'image2', '-r', '1',
                '-pattern_type', 'glob', '-i','*'+ movieType + '*' + scaleType + '_ephem_lb.png',
                output])
    subprocess.call('rm *.png', shell=True) #delete the temporary files 
    os.chdir(path) #change back to our ROOTPATH


def runScript(path):
    '''
    run scripts for both center and wide images
    '''
    path = os.path.join(path,'png')
    
    os.chdir(path)

    buildMovies('wide', path, 'linear')
    buildMovies('center', path, 'linear')
    buildMovies('wide', path, 'log')
    buildMovies('center', path, 'log')
    
def createMovie():
    """
    parses whether the script is to be run for a particular subfolder or
    all the subfolders and calls the runScript function accordingly.
    If no subfolder given calls runScript iteratively on all subfolders.
    """
    path = ROOTPATH 
    if source: #add sub-directory to path if given
        path = ROOTPATH + '/' + source
        runScript(path)
    else: #else carry out operation for ALL sub-drectories
        for dirs in os.listdir(path):
            if dirs[0].isdigit():
                path = ROOTPATH + '/' + dirs
                try:
                    runScript(path)
                except:
                    print "path not valid"


if __name__ == '__main__':
    args = parse_args() 
    source = args.source 
    createMovie() 