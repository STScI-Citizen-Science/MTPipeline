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

def log_scale(array, inspect=False, output=False):
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
            output = False,
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
                    
def median_scale(array, box, inspect=False, output=False):
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
    if inspect:
        before_after(
            before_array = array, 
            after_array = output_array, 
            before_array_name = 'Input Data',
            after_array_name = 'Median with ' + str(box) + ' box',
            output = output,
            pause = False) 
    return output_array
    
# -----------------------------------------------------------------------------

def positive(input_array, inspect=False, output=False):
    '''
    Shift all the pixels so there are no negative or 0 pixels. Needed 
    to prevent taken the log of negative values.
    '''
    assert isinstance(input_array, N.ndarray), 'array must be numpy array'
    min_val = N.min(input_array)
    if min_val <= 0:
        output_array = input_array + ((min_val * -1.0) + 0.0001) 
    if inspect:
        before_after(before_array = input_array, 
            after_array = output_array, 
            before_array_name = 'Input Data',
            after_array_name = 'Positive Corrected',
            output = output,
            pause = False)   
    return output_array

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
    assert xmin < xmax, 'xmin must be stictly less than xmax.'
    assert ymin < ymax, 'ymin must be stictly less than ymax.'
    if xmax > array.shape[0] or ymax > array.shape[1]:
        border_array = N.zeros((max(xmax,array.shape[0]), max(ymax,array.shape[1])))
        print xmin, xmax, ymin, ymax
        print array.shape, border_array.shape
        border_array[:array.shape[0], :array.shape[1]] = array
        array = border_array
    output_array = array[xmin:xmax, ymin:ymax]
    assert output_array.shape[0] == xmax - xmin, 'Output shape is unexpected.'
    assert output_array.shape[1] == ymax - ymin, 'Output shape is unexpected.' 
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
# Main Class
# -----------------------------------------------------------------------------

class PNGCreator(object):
    '''
    The PNGCreator class incorperates all the functions in the run_trim
    module to create a smoother interface for passing the numpy array 
    around and for saving the result. All manipulations are done in 
    place, with the expection of the trim method which returns a new 
    PNGCreator instance.
    '''
    def __init__(self, data):
        '''
        Check the input type on instantiation.
        '''
        self.data = data
        assert isinstance(data, N.ndarray), 'Expected N.ndarray got ' + str(type(data))

    def trim(self, xmin, xmax, ymin, ymax):
        '''
        Trim the self.data attribute and another instance of PNGCreator
        for the trimmed data. This allows you to apply the save_png 
        method to the trimmed data.
        '''
        return PNGCreator(subarray(self.data, xmin, xmax, ymin, ymax))
    
    def log(self, output=False):
        '''
        Transform all the data in the self.data attribute to a positive
        value and take the log of image.
        '''
        self.data = positive(self.data, inspect = False, output = output)
        self.data = log_scale(self.data, inspect = False, output = output)
    
    def bottom_clip(self, output=False):
        '''
        Clip the bottom 10 pixels from the self.data attribute.
        '''
        bottom_value = get_value_by_pixel_count(self.data, 10, 'bottom')
        self.data = clip(self.data, bottom_value, 'bottom', inspect = False, 
            output = output)
    
    def saturated_clip(self, output=False):
        '''
        Clip any saturated pixels.
        '''
        self.data = clip(self.data, 4095.0, 'top', inspect = False, 
            output = output)

    def save_png(self, png_name):
        '''
        Save the self.data attribute to a png.
        '''                          
        make_png(self.data, png_name)

    def median(self, output=False):
        '''
        Take a 25x25 median box smoothing of the self.data attribute.
        '''
        self.data = median_scale(self.data, 25, output = output)

# -----------------------------------------------------------------------------
# The Main Controller
# -----------------------------------------------------------------------------
            
def run_trim(filename, output_path):
    '''
    The main controller for the png creation. Checks for and creates an
    output folder. Opens the data header extention. Uses a PNGCreator 
    instance to create trimmed and scaled pngs.
    '''
    # Make png folder if it doesn't exist.
    png_path = os.path.join(os.path.dirname(filename), 'png')
    test = os.access(png_path, os.F_OK)
    if test == False:
        os.mkdir(png_path)

    # Get the data.
    h = pyfits.open(filename) 
    data = h[0].data
    h.close()
    
    # Itinital scaling.
    pngc = PNGCreator(data)
    pngc.bottom_clip(make_png_name(output_path, filename, 'bottom_clip_stat'))
    pngc.saturated_clip(make_png_name(output_path, filename, 'saturated_clip_stat'))

    # Create and save a full log image.
    pngc.log(make_png_name(output_path, filename, 'log_stat'))
    log_png_name = make_png_name(output_path, filename, 'log') 
    pngc.save_png(log_png_name)

    # Create and save the trimmed log images.
    counter = 0
    for xmin in range(0, 1351, 450):
        for ymin in range(0, 901, 450):
            counter += 1
            pngc_trimmed = pngc.trim(xmin, xmin + 450, ymin, ymin + 450)
            log_png_name = make_png_name(output_path, filename, 'log_' + str(counter))
            pngc_trimmed.save_png(log_png_name)

    # Create and save a full median image.
    pngc.median(make_png_name(output_path, filename, 'median_stat'))
    median_png_name = make_png_name(output_path, filename, 'median')   
    pngc.save_png(median_png_name)

    # Create and save the trimmed median images.
    counter = 0
    for xmin in range(0, 1351, 450):
        for ymin in range(0, 901, 450):
            counter += 1
            pngc_trimmed = pngc.trim(xmin, xmin + 450, ymin, ymin + 450)
            median_png_name = make_png_name(output_path, filename, 'median_' + str(counter))   
            pngc_trimmed.save_png(median_png_name)
        
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
    args = parser.parse_args()        
    return args
    
# -----------------------------------------------------------------------------
    
if __name__ == '__main__':
    args = parse_args()
    file_list = glob.glob(args.filelist)
    assert file_list != [], 'run_trim found no files matching ' + args.filelist
    for filename in file_list:
        run_trim(filename, args.output_path)