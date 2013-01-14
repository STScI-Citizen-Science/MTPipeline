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
from display_tools import before_after

# -----------------------------------------------------------------------------
# Low-Level Functions: Image Manipulation, etc.
# -----------------------------------------------------------------------------

def clip(input_array, clip_val, top_or_bottom, output=False):
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
    if output != False:
        before_after(
            before_array = input_array, 
            after_array = output_array, 
            before_array_name = 'Input Data',
            after_array_name = 'Clip ' + top_or_bottom + ' at ' + str(clip_val),
            output = output)
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

def log_scale(array, output=False):
    '''
    Returns the log of the input array.
    '''
    assert isinstance(array, N.ndarray), 'array must be numpy array'
    array_log = N.log(array)
    if output != False:
        before_after(before_array = array, 
            after_array = array_log, 
            before_array_name = 'Input Data',
            after_array_name = 'Log',
            output = output) 
    return array_log
        
# -----------------------------------------------------------------------------

def make_png(data, filename):
    '''
    Use the Python image library (PIL) to write out the png file. The 
    data is flipped in the "up-down" direction and converted to 8bit
    encoding before writing.
    '''
    assert isinstance(data, N.ndarray), 'array must be numpy array'
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
                    
def median_scale(array, box, output=False):
    '''
    Perform a local-median subtraction (box smoothing). The box size 
    must be odd and is set by the box parameter.
    '''
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
    if output != False:
        before_after(
            before_array = array, 
            after_array = output_array, 
            before_array_name = 'Input Data',
            after_array_name = 'Median with ' + str(box) + ' box',
            output = output,
            pause = False) 
    return output_array
    
# -----------------------------------------------------------------------------

def positive(input_array, output=False):
    '''
    Shift all the pixels so there are no negative or 0 pixels. Needed 
    to prevent taken the log of negative values.
    '''
    assert isinstance(input_array, N.ndarray), 'array must be numpy array'
    min_val = N.min(input_array)
    if min_val <= 0:
        output_array = input_array + ((min_val * -1.0) + 0.0001) 
    if output != False:
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
    output_array = array[xmin:min(xmax,array.shape[0]), ymin:min(ymax,array.shape[1])]
    assert output_array.shape[0] == min(xmax,array.shape[0]) - xmin, \
        'Output shape is unexpected: ' + str(min(xmax,array.shape[0]) - xmin)
    assert output_array.shape[1] == min(ymax,array.shape[1]) - ymin, \
        'Output shape is unexpected: ' + str(min(ymax,array.shape[1]) - ymin)
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
    place. The __init__ method creates a new copy of the array, not a 
    pointer, by using the deepcopy fucntion. In this way you can create
    a new instance of the PNGCreator class on the self.data attribute 
    of another class to make changes that will not affect the other 
    class instance.
    '''
    def __init__(self, data):
        '''
        Check the input type on instantiation.
        '''
        self.data = copy.deepcopy(data)
        assert isinstance(data, N.ndarray), 'Expected N.ndarray got ' + str(type(data))

    def bottom_clip(self, output=False):
        '''
        Clip the bottom 10 pixels from the self.data attribute.
        '''
        bottom_value = get_value_by_pixel_count(self.data, 10, 'bottom')
        self.data = clip(self.data, bottom_value, 'bottom', output = output)

    def compress(self):
        '''
        Compress the range of the array to be between 0 and 256. This
        is the range expected for the PIL call in the save_png method.
        This method should be called on the whole image before the 
        trimming to ensure that the trimmed images all have the same
        stretch. 
        '''
        self.data = self.data - self.data.min()            
        self.data = (self.data / self.data.max()) * 255.
    
    def log(self, output=False):
        '''
        Take the log of self.data.
        '''
        self.data = log_scale(self.data, output = output)
    
    def median(self, output=False):
        '''
        Take a 25x25 median box smoothing of the self.data attribute.
        '''
        self.data = median_scale(self.data, 25, output = output)

    def positive(self, output=False):
        '''
        Transform all the data in the self.data attribute to a positive
        value.
        '''
        self.data = positive(self.data, output = output)
    
    def saturated_clip(self, output=False):
        '''
        Clip any saturated pixels.
        '''
        self.data = clip(self.data, 4095.0, 'top', output = output)

    def save_png(self, png_name):
        '''
        Save the self.data attribute to a png.
        '''                          
        make_png(self.data, png_name)

    def trim(self, xmin, xmax, ymin, ymax):
        '''
        Trim the self.data attribute.
        '''
        self.data = subarray(self.data, xmin, xmax, ymin, ymax)

# -----------------------------------------------------------------------------
# Control Functions
# -----------------------------------------------------------------------------

def run_trim(filename, output_path):
    '''
    The main controller for the png creation. Checks for and creates an
    output folder. Opens the data header extention. Uses a PNGCreator 
    instance to create trimmed and scaled pngs.
    '''
    
    astrodrizzle_mode = filename.split('_')[-3]
    print astrodrizzle_mode

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
    print 'Creating log PNGs'
    pngc_log = PNGCreator(data)
    pngc_log.saturated_clip(output = make_png_name(output_path, filename, 'saturated_clip_stat'))
    pngc_log.positive(output = make_png_name(output_path, filename, 'positive_stat'))
    pngc_log.log(output = make_png_name(output_path, filename, 'log_stat'))
    pngc_log.bottom_clip(output = make_png_name(output_path, filename, 'bottom_clip_stat'))
    pngc_median = PNGCreator(pngc_log.data)
    pngc_log.compress() 
    pngc_log.save_png(make_png_name(output_path, filename, 'log'))

    # Create and save the trimmed log images.
    if astrodrizzle_mode == 'wide':
        counter = 0
        for ymin in range(0, 1351, 450):
            for xmin in range(0, 901, 450):
                counter += 1
                pngc_trimmed = PNGCreator(pngc_log.data)
                pngc_trimmed.trim(xmin, xmin + 450, ymin, ymin + 450)
                pngc_trimmed.save_png(make_png_name(output_path, filename, 'log_' + str(counter)))

    # Create and save a full median image.
    print 'Creating median PNGs'
    pngc_median.median(output = make_png_name(output_path, filename, 'median_stat'))
    pngc_median.compress()
    pngc_median.save_png(make_png_name(output_path, filename, 'median'))

    # Create and save the trimmed median images. Remeber to switch x and y.
    if astrodrizzle_mode == 'wide':
        counter = 0
        for ymin in range(0, 1351, 450):
            for xmin in range(0, 901, 450):
                counter += 1
                pngc_trimmed = PNGCreator(pngc_median.data)
                pngc_trimmed.trim(xmin, xmin + 450, ymin, ymin + 450)
                pngc_trimmed.save_png(make_png_name(output_path, filename, 'median_' + str(counter)))
        
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