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
import time

# Custom modules
from display_tools import *

# -----------------------------------------------------------------------------
# Low-Level Functions
# -----------------------------------------------------------------------------

def clip(input_array, clip_val, top_or_bottom, inspect=False, output=False):
    '''
    Clip an input numpy array and set the clipped pixels to the 
    clipping value. Bottom clip scales pixels below the clip_val.
    Top does the same for pixels above.
    '''
    # Input validation
    error = 'input_array for clip must be a numpy array instance.'
    assert isinstance(input_array, N.ndarray), error
    error = 'clip_val must be float'
    assert isinstance(clip_val, float), error
    error = 'top_or_bottom for clip must be "top" or "bottom".'
    assert top_or_bottom in ['top', 'bottom'], error

    if top_or_bottom == 'bottom':   
        index = N.where(input_array < clip_val)
    elif top_or_bottom == 'top':
        index = N.where(input_array > clip_val)
    output_array = copy.deepcopy(input_array)
    output_array[index] = clip_val
    if inspect:
        before_after(
            before_array = input_array, 
            after_array = output_array, 
            before_array_name = 'Input Data',
            after_array_name = 'Clip ' + top_or_bottom + ' at ' + str(clip_val),
            output = output,
            pause = False)  
    return output_array

# -----------------------------------------------------------------------------

def get_value_by_pixel_count(input_array, pixel_number ,top_or_bottom):
    '''
    Return the value for the ith pixel from the top or bottom.
    '''
    error = 'input_array for get_value_by_pixel_count must be a numpy array instance.'
    assert isinstance(input_array, N.ndarray), error
    error = 'pixel_count for get_value_by_pixel_count must by int.'
    assert isinstance(pixel_number, int)
    error = 'top_or_bottom for get_value_by_pixel_count must be "top" or "bottom".'
    assert top_or_bottom in ['top', 'bottom'], error
    sorted_array = copy.deepcopy(input_array)
    sorted_array = sorted_array.ravel()
    sorted_array.sort()
    if top_or_bottom == 'top':
        output = sorted_array[pixel_number]
    elif top_or_bottom == 'bottom':
        output = sorted_array[pixel_number - 1]
    output = float(output)
    return output

# -----------------------------------------------------------------------------

def log_scale(array, inspect=True):
    '''
    Returns the log of the input array.
    '''
    assert isinstance(array, N.ndarray), 'array must be numpy array'
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
    assert isinstance(data, N.ndarray), 'array must be numpy array'
    data = data - data.min()            
    data = (data / data.max()) * 255.
    data = N.flipud(data)
    data = N.uint8(data)
    image = Image.new('L', (data.shape[1], data.shape[0]))
    image.putdata(data.ravel())
    image.save(filename)

# -----------------------------------------------------------------------------

def make_png_name(path, filename, ext):
    '''
    Return the name of the png output_array file.
    '''
    png_name = os.path.basename(filename)
    png_name = os.path.splitext(png_name)[0] + '_' + ext + '.png'
    png_name = os.path.join(path, png_name)
    return png_name
    
# -----------------------------------------------------------------------------
                    
def median_scale(array, box):
    '''
    Perform a local-median subtraction (box smoothing). The box size 
    must be odd and is set by the box parameter.
    '''
    print 'Starting the median scale.'
    assert box % 2 == 1, 'Box size must be odd.'
    assert isinstance(array, N.ndarray), 'array must be numpy array'
    output_array = N.zeros((array.shape[0], array.shape[1]))        
    for x in xrange(array.shape[0]):
        xmin = max(0, x - (box / 2)) 
        xmax = min(x + (box / 2) + 1, array.shape[0])
        for y in xrange(array.shape[1]):
            ymin = max(0, y - (box / 2)) 
            ymax = min(y + (box / 2) + 1, array.shape[1])
            local_region = array[xmin:xmax, ymin:ymax]
            local_median = N.median(local_region)
            output_array[x, y] = copy.copy(array[x, y] - local_median)
    print 'Done with the median scale.'
    return output_array
    
# -----------------------------------------------------------------------------

def positive(input_array, inspect=False):
    '''
    Shift all the pixels so there are no negative or 0 pixels. Needed 
    to prevent taken the log of negative values.
    '''
    assert isinstance(input_array, N.ndarray), 'array must be numpy array'
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
    Performs a sigma clip. Not sure if this is going to be in the final 
    version.
    '''
    assert isinstance(array, N.ndarray), 'array must be numpy array'
    P.clf()
    ax1 = P.subplot(121)
    ax1.set_title('Original')
    ax1.imshow(array, cmap=cm.grey)
    ax1.grid(True)
        
    min_val = N.min(array)
    med_val = N.median(array)
    std_val = N.std(array)
    zero = med_val - (2. * std_val)
    array = array - zero
    array = array * (array >= 0)
    
    ax2 = P.subplot(122)
    ax2.set_title('Rescaled')
    ax2.imshow(array, cmap=cm.grey)
    ax2.grid(True)    
    P.draw()
    
    return array

# -----------------------------------------------------------------------------

def subarray(array, xmin, xmax, ymin, ymax):
    '''
    Returns a subarray.
    '''
    assert isinstance(array, N.ndarray), 'array must be numpy array'
    assert isinstance(xmin, int), 'xmin in subarray must be an int.'
    assert isinstance(xmax, int), 'xmax in subarray must be an int.'
    assert isinstance(ymin, int), 'ymin in subarray must be an int.'
    assert isinstance(ymax, int), 'ymax in subarray must be an int.'    
    status = '\t' + time.asctime() + ' trimming to '
    status += '[' + str(xmin) + ',' + str(xmax) + ':' 
    status += str(ymin) + ',' + str(ymax) + ']'
    print status
    output_array = array[xmin:xmax, ymin:ymax]
    return output_array

# -----------------------------------------------------------------------------

def top_bottom_clip(array):
    '''
    Clip the top and bottom 1% of pixels.
    '''
    assert isinstance(array, N.ndarray), 'array must be numpy array'
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
            
def run_trim(filename, output_path, stretch_switch, trim=False):
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
    test = os.access(png_path, os.F_OK)
    if test == False:
        os.mkdir(png_path)
    
    # Trim image.
    if trim != False:
        trim = trim[0]
        assert len(trim) == 3, 'len(trim) in run_trim must be 3.'
        trim[0] = int(trim[0])
        trim[1] = int(trim[1])
        trim[2] = int(trim[2])
        xmin = trim[0] - (trim[2] / 2)
        xmax = trim[0] + (trim[2] / 2)
        ymin = trim[1] - (trim[2] / 2)
        ymax = trim[1] + (trim[2] / 2)
        data = subarray(data, xmin, xmax, ymin, ymax)
    
    # Make the log image.
    log_output = positive(data, inspect = True)
    log_output = log_scale(log_output, inspect = True)
    
    # Clip the bottom 10 pixels.
    bottom_value = get_value_by_pixel_count(log_output, 10, 'bottom')
    log_output = clip(
        log_output, 
        bottom_value, 
        'bottom', 
        inspect = True,
        output = os.path.join(png_path, os.path.basename(filename)[:-4] + 'bottom_clip.png'))
    
    # Clip any saturated pixels.
    log_output = clip(
        log_output, 
        4095.0, 
        'top', 
        inspect = True, 
        output = os.path.join(png_path, os.path.basename(filename)[:-4] + 'top_clip.png'))

    if stretch_switch == 'log':                
        log_output_path = os.path.join(os.path.dirname(filename), 'png')
        log_png_name = make_png_name(log_output_path, filename, 'log')            
        make_png(log_output, log_png_name)

    if stretch_switch == 'median':
        median_output = median_scale(log_output, 25)
        median_output_path = os.path.join(os.path.dirname(filename), 'png')
        median_png_name = make_png_name(median_output_path, filename, 'median')            
        make_png(median_output, median_png_name)        
        
# -----------------------------------------------------------------------------
# For command line execution.
# -----------------------------------------------------------------------------

def parse_args():
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
    parser.add_argument(
        '-stretch_switch',
        required = True,
        choices = ['log', 'median'],
        help = 'Choose log or median.')
    parser.add_argument(
        '-trim',
        required = False,
        nargs=3, 
        action='append',
        help = '3 ints: x center, y center, and box size.'),
    args = parser.parse_args()        
    return args
    
# -----------------------------------------------------------------------------
    
if __name__ == '__main__':
    args = parse_args()
    file_list = glob.glob(args.filelist)
    assert file_list != [], 'run_trim found no files matching ' + args.filelist
    for filename in file_list:
        run_trim(filename, args.output_path, args.stretch_switch, args.trim)