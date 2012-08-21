#! /usr/bin/env python

'''
Scales the images and produces the output images.
'''

# Standard modules
import argparse
import copy
import glob
import Image
import numpy as N
import os
import pyfits
import string
import sys
import time

# Custom modules
import display_tools
from display_tools import *

# -----------------------------------------------------------------------------
# Low-Level Functions
# -----------------------------------------------------------------------------

def bottom_clip(input, pixels_to_change, inspect=False):
    '''
    Rescale the bottom X pixels.
    '''
    error = 'pixels_to_change in bottom_clip must be an int type.'
    assert type(pixels_to_change) == int, error
    sorted_array = copy.deepcopy(input)
    sorted_array = sorted_array.ravel()
    sorted_array.sort()
    bottom = sorted_array[pixels_to_change - 1]
    bottom_index = N.where(input < bottom)
    output = copy.deepcopy(input)
    output[bottom_index] = bottom
    if inspect:
        before_after(
            before_array = input, 
            after_array = output, 
            before_array_name = 'Input Data',
            after_array_name = 'Remove Bottom ' + str(pixels_to_change) + ' Pixels',
            pause = True)  
    return output

# -----------------------------------------------------------------------------

def log_scale(array, inspect=True):
    '''
    Returns the log of the input array.
    '''
    # Log Scale
    print '\t' + time.asctime() + ' log scaling' 
    array_log = N.log(array)
    if inspect == True:
        before_after(before_array = array, 
            after_array = array_log, 
            before_array_name = 'Input Data',
            after_array_name = 'Log',
            pause = False) 
    return array_log
        
# -----------------------------------------------------------------------------

def make_png(data, filename):
    '''
    Use the Python image library (PIL) to write out the png file. Note 
    that the image flux is rescaled between be between 0 and 256.
    '''
    data = data - data.min()            
    data = (data / data.max()) * 255.
    data = N.flipud(data)
    data = N.uint8(data)
    image = Image.new('L',(data.shape[1],data.shape[0]))
    image.putdata(data.ravel())
    image.save(filename)

# -----------------------------------------------------------------------------

def make_png_name(path, filename, ext):
    '''
    Return the name of the png output file.
    '''
    png_name = os.path.basename(filename)
    png_name = os.path.splitext(png_name)[0] + '_' + ext + '.png'
    png_name = os.path.join(path, png_name)
    return png_name
    
# -----------------------------------------------------------------------------
                    
def median_scale(array, box, verbose=False):
    '''
    Perform a local-median subtraction (box smoothing). The box size 
    must be odd and is set by the box parameter.
    '''
    print 'Starting the median scale.'
    assert box % 2 == 1, 'Box size must be odd.'
    output = N.zeros((array.shape[0],array.shape[1]))        
    for x in xrange(array.shape[0]):
        xmin = max(0, x - (box / 2)) 
        xmax = min(x + (box / 2) + 1, array.shape[0])
        for y in xrange(array.shape[1]):
            ymin = max(0, y - (box / 2)) 
            ymax = min(y + (box / 2) + 1, array.shape[1])
            local_region = array[xmin:xmax, ymin:ymax]
            local_median = N.median(local_region)
            output[x, y] = copy.copy(array[x, y] - local_median)
    print 'Done with the median scale.'
    return output
    
# -----------------------------------------------------------------------------

def positive(input_array, inspect=False):
    '''
    Shift all the pixels so there are no negative or 0 pixels. Needed 
    to prevent taken the log of negative values.
    '''
    min_val = N.min(input_array)
    if min_val <= 0:
        output_array = input_array + ((min_val * -1.0) + 0.0001) 
    if inspect == True:
        before_after(before_array = input_array, 
            after_array = output_array, 
            before_array_name = 'Input Data',
            after_array_name = 'Positive Corrected',
            show = False)    
    return output_array

# -----------------------------------------------------------------------------

def sigma_clip(array):
    '''
    '''
    P.clf()
    ax1 = P.subplot(121)
    ax1.set_title('Original')
    ax1.imshow(array,cmap=cm.gray)
    ax1.grid(True)
        
    min_val = N.min(array)
    med_val = N.median(array)
    std_val = N.std(array)
    zero = med_val - (2. * std_val)
    array = array - zero
    array = array * (array >= 0)
    
    ax2 = P.subplot(122)
    ax2.set_title('Rescaled')
    ax2.imshow(array,cmap=cm.gray)
    ax2.grid(True)    
    P.draw()
    
    return array

# -----------------------------------------------------------------------------

def subarray(array, xmin, xmax, ymin, ymax):
    '''
    Returns a subarray.
    '''
    status = '\t' + time.asctime() + ' trimming to '
    status += '[' + str(xmin) + ',' + str(xmax) + ':' 
    status += str(ymin) + ',' + str(ymax) + ']'
    print status
    output = array[xmin:xmax,ymin:ymax]
    return output

# -----------------------------------------------------------------------------

def top_bottom_clip(array):
    '''
    Clip the top and bottom 1% of pixels.
    '''
    sorted_array = copy.copy(array)
    sorted_array = sorted_array.ravel()
    sorted_array.sort()
    top = sorted_array[int(len(sorted_array) * 0.99)]
    bottom = sorted_array[int(len(sorted_array) * 0.01)]
    top_index = N.where(array > top)
    array[top_index] = top
    bottom_index = N.where(array < bottom)               
    array[bottom_index] = bottom
    return array

# -----------------------------------------------------------------------------
# The Main Controller
# -----------------------------------------------------------------------------
            
def run_trim(filename, output_path, stretch_switch):
    '''
    Set the stretch and create the output image.
    '''
    # Check the inputs
    error = 'strech_switch must me "log" or "median".'
    assert stretch_switch in ['log', 'median'], error
    
    # Get Data
    h = pyfits.open(filename) 
    data = h[0].data
    h.close()

    # Make png folder    
    png_path = os.path.join(os.path.dirname(filename), 'png')
    test = os.access(png_path,os.F_OK)
    if test == False:
        os.mkdir(png_path)

    # Median
    #if median_switch == True:
    #    median_scaled_data = median_scale(data, 25)
    
    # Make a before/after plot
    #before_after(median_scaled_data, log_median_scaled_data)
    #output = os.path.basename(filename)
    #log_png_name = os.path.splitext(log_png_name)[0] + '_log.png'
    #log_png_name = '/astro/3/mutchler/mt/code/median_test/' + log_png_name
    #before_after(
    #    log_median_scaled_data,
    #    bottom_clip(log_median_scaled_data, 0.1))
        
    # Linear
    linear_switch = False
    if linear_switch == True:
        linear_png_name = os.path.basename(filename)
        linear_png_name = os.path.splitext(linear_png_name)[0] + '_linear.png'
        if output_path == None:
            linear_png_name = os.path.join(
                os.path.dirname(filename), linear_png_name)
        elif output_path != None:
            linear_png_name = os.path.join(
                output_path, linear_png_name)
        make_png(bottom_clip(median_scaled_data), linear_png_name)
    
    if stretch_switch == 'log':        
        log_output = positive(data, inspect = True)
        log_output = log_scale(log_output, inspect = True)
        log_output = bottom_clip(log_output, 10, inspect = True)
        log_output_path = os.path.join(os.path.dirname(filename), 'png')
        log_png_name = make_png_name(log_output_path, filename, 'log')            
        make_png(log_output, log_png_name)

# -----------------------------------------------------------------------------
# For command line execution.
# -----------------------------------------------------------------------------

def prase_args():
    '''
    Prase the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'A script to scale and trim the images.' )
    parser.add_argument(
        '-filelist', 
        required = True,
        help = 'Search string for files to used. Wild cards accepted')
    parser.add_argument(
        '-output_path',
        required = False,
        help = 'Set the path for the output. Default is the input directory.')        
    args = parser.parse_args()        
    return args
    
# -----------------------------------------------------------------------------
    
if __name__ == '__main__':
    args = prase_args()
    file_list = glob.glob(args.filelist)
    assert file_list != [], 'run_trim found no files matching ' + args.filelist
    for filename in file_list:
        run_trim(filename, args.output_path, stretch_switch = 'log')