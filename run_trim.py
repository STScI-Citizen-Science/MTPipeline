#! /usr/bin/env python

'''
Scales the images and produces the output images.
'''

# Standard modules
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

def bottom_clip(input, percent):
    '''
    Rescale the bottom 1% of pixels.
    '''    
    # Clip the top and bottom 1% of pixels.
    sorted_array = copy.copy(input)
    sorted_array = sorted_array.ravel()
    sorted_array.sort()
    bottom = sorted_array[int(len(sorted_array) * percent)]
    bottom_index = N.where(input < bottom)
    input[bottom_index] = bottom
    return input

# -----------------------------------------------------------------------------

def log_scale(array):
    '''
    Returns the log of the input array.
    '''
    # Log Scale
    print '\t' + time.asctime() + ' log scaling' 
    array_log = N.log(array)
    return array_log
        
# -----------------------------------------------------------------------------

def make_png(data,filename):
    '''
    Use the Python image library (PIL) to write out the png file. Note 
    that the image flux is rescaled between be between 0 and 256.
    '''
    # Scale the data.
    data = data - data.min()            
    data = (data / data.max()) * 255.
    data = N.flipud(data)
    data = N.uint8(data)
    # Write to the file.    
    image = Image.new('L',(data.shape[1],data.shape[0]))
    image.putdata(data.ravel())
    image.save(filename)

# -----------------------------------------------------------------------------

def median_scale(array, box):
    '''
    Perform a local-median subtraction (box smoothing). The box size 
    must be odd and is set by the box parameter.
    '''
    assert box % 2 == 1, 'Box size must be odd.'
    output = N.zeros((array.shape[0],array.shape[1]))        
    for x in xrange(array.shape[0]):
        xmin = max(0, x - (box / 2)) 
        xmax = min(x + (box / 2) + 1, array.shape[0])
        for y in xrange(array.shape[1]):
            ymin = max(0, y - (box / 2)) 
            ymax = min(y + (box / 2) + 1, array.shape[1])
            local_region = array[xmin:xmax,ymin:ymax]
            local_median = N.median(local_region)
            output[x,y] = copy.copy(array[x,y] - local_median)
    return output
    
# -----------------------------------------------------------------------------

def positive(array):
    '''
    Shift all the pixels so there are no negative or 0 pixels. Needed 
    to prevent taken the log of negative values.
    '''
    min_val = N.min(array)
    if min_val <= 0:
        print '\t' + time.asctime() + ' Min value is ' + str(min_val)
        print '\t' + time.asctime() + ' Correction is ' + str((min_val *
        -1.0) + 0.0001)
        array = array + ((min_val * -1.0) + 0.0001) #Rescale min to >0 for log
        min_val = N.min(array)
        print '\t' + time.asctime() + ' Min value is ' + str(min_val)
    return array

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

def subarray(array,xmin,xmax,ymin,ymax):
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
            
def run_trim(filename):
    '''
    '''
    # Get Data
    h = pyfits.open(filename) 
    data = h[0].data
    h.close()

    # Make png folder    
    png_path = os.path.join(os.path.split(filename)[0], 'png')
    test = os.access(png_path,os.F_OK)
    if test == False:
        os.mkdir(png_path)

    #median 
    median_scaled_data = median_scale(data, 25)
    #before_after(data, median_scaled_data)
    #before_after(median_scaled_data, bottom_clip(median_scaled_data))

    # Linear
    linear_switch = False
    if linear_switch == True:
        linear_png_name = os.path.basename(filename)
        linear_png_name = os.path.splitext(linear_png_name)[0] + '_linear.png'
        linear_png_name = '/astro/3/mutchler/mt/code/median_test/' + linear_png_name
        make_png(bottom_clip(median_scaled_data), linear_png_name)
    
    # Log
    log_switch = True
    if log_switch == True:
        log_median_scaled_data = positive(median_scaled_data)
        log_median_scaled_data = log_scale(log_median_scaled_data)
  
        # Make a before/after plot
        #before_after(median_scaled_data, log_median_scaled_data)
        #output = os.path.basename(filename)
        #log_png_name = os.path.splitext(log_png_name)[0] + '_log.png'
        #log_png_name = '/astro/3/mutchler/mt/code/median_test/' + log_png_name
        before_after(
            log_median_scaled_data,
            bottom_clip(log_median_scaled_data, 0.1))
    
        # Write the output filename
        log_png_name = os.path.basename(filename)
        log_png_name = os.path.splitext(log_png_name)[0] + '_log.png'
        log_png_name = '/astro/3/mutchler/mt/code/median_test/' + log_png_name
    
        before_after(
            median_scaled_data, 
            log_median_scaled_data,
            'test')
        
        make_png(log_median_scaled_data, log_png_name)



    