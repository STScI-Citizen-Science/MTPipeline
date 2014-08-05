#! /usr/bin/env python

'''
Scales the images and produces the output images.
'''

# Standard modules
import argparse
import copy
import glob
import logging
import numpy as N
import os
import pyfits
import time

from PIL import Image


# Custom modules
from display_tools import before_after

logger = logging.getLogger('mtpipeline.run_trim')


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

def get_fits_data(filename, ext=0):
    '''
    Return the data from the extention as a numpy array.
    '''
    assert os.path.splitext(filename)[1] == '.fits', 'Inputs must be FITS file.'
    data = pyfits.getdata(filename)
    data = N.flipud(data)
    return data

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

def make_png_name(path, filename, ext):
    '''
    Return the name of the png output_array file.
    '''
    png_name = os.path.basename(filename)
    png_name = os.path.splitext(png_name)[0] + '_' + ext + '.png'
    png_name = os.path.join(path, png_name)
    return png_name

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
    output_array = array[max(xmin,0):min(xmax,array.shape[0]), \
        max(ymin,0):min(ymax,array.shape[1])]
    assert output_array.shape[0] == min(xmax,array.shape[0]) - max(xmin,0), \
        'Output shape is unexpected: ' + str(min(xmax,array.shape[0]) - max(xmin,0))
    assert output_array.shape[1] == min(ymax,array.shape[1]) - max(ymin,0), \
        'Output shape is unexpected: ' + str(min(ymax,array.shape[1]) - max(ymin,0))
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
        array_log = N.log(self.data)

        if output != False:
            before_after(before_array = self.data,
                after_array = array_log,
                before_array_name = 'Input Data',
                after_array_name = 'Log',
                output = output)

        self.data = array_log

    def positive(self, output=False):
        '''
        Shift all the values in self.data so there are no negative or 0 pixels.
        Needed to prevent taking the log of negative values.
        '''
        min_val = N.min(self.data)
        if min_val <= 0:
            output_array = self.data + ((min_val * -1.0) + 0.0001)
        else:
            output_array = self.data

        if output != False:
            before_after(before_array = self.data,
                after_array = output_array,
                before_array_name = 'Input Data',
                after_array_name = 'Positive Corrected',
                output = output,
                pause = False)

        self.data = output_array

        print 'MINIMUM VALUE:'
        print N.min(self.data)

    def saturated_clip(self, weight_array, output=False):
        '''
        Replace all the pixels that have a weight value of 0 with the local
        3x3 median. A copy of the image is created so that the values of
        the replaced pixels don't affect the medians of other pixels as
        they are replaced. The subarray function is used to generate the
        subarrays to prevent error at the array edge.

        The indices are set keeping in mind that a[0:2,0:2] returns a 2x2
        array while a[0:3,0:3] returns a 3x3 array. Both arrays are
        centered on (1,1).
        '''

        assert isinstance(weight_array, N.ndarray), 'array must be numpy array'
        output_array = copy.copy(self.data)
        saturated_indices = N.where(weight_array == 0)
        for index in zip(saturated_indices[0], saturated_indices[1]):
             output_array[index] = N.median(subarray(self.data, index[0] - 1, \
                index[0] + 2, index[1] - 1, index[1] + 2))

        if output != False:
            before_after(before_array = self.data,
                after_array = output_array,
                before_array_name = 'Input Data',
                after_array_name = '0-Weight Corrected',
                output = output,
                pause = False)

        self.data = output_array

    def save_png(self, png_name):
        '''
        Use the Python image library (PIL) to write self.data as a png file.
        self.data is flipped in the "up-down" direction and converted to 8bit
        encoding before writing.
        '''
        self.data = N.uint8(self.data)
        image = Image.new('L', (self.data.shape[1], self.data.shape[0]))
        image.putdata(self.data.ravel())
        image.save(png_name)

    def threshold_clip(self, minimum, maximum, output=False):
        '''
        Set all values below minum and above maximum to the
        minimum and maximum, respectively 
        '''
        output_array = copy.deepcopy(self.data)
        output_array[output_array > maximum] = maximum
        output_array[output_array < minimum] = minimum

        if output != False:
            before_after(before_array = self.data,
                after_array = output_array,
                before_array_name = 'Input Data',
                after_array_name = 'Threshold Clipped',
                output = output,
                pause = False)

        self.data = output_array

    def trim(self, xmin, xmax, ymin, ymax):
        '''
        Trim the self.data attribute using the subarray function.
        '''
        self.data = subarray(self.data, xmin, xmax, ymin, ymax)

# -----------------------------------------------------------------------------
# Control Functions
# -----------------------------------------------------------------------------

def make_subimage_pngs(input_pngc_instance, output_path, filename, suffix):
    '''
    Wrapper function to make trimmed png outputs for the astrodrizzle
    'wide' outputs.
    '''
    assert isinstance(output_path, str), 'Expected str got ' + str(type(output_path))
    assert isinstance(filename, str), 'Expected str got ' + str(type(filename))
    assert isinstance(suffix, str), 'Expected str got ' + str(type(suffix))
    assert isinstance(input_pngc_instance, PNGCreator), \
        'Expected instnace of PNGCreator, got ' + str(type(input_pngc_instance))
    counter = 0
    for ymin in range(0, 1351, 425):
        for xmin in range(0, 901, 425):
            counter += 1
            pngc_trimmed = PNGCreator(input_pngc_instance.data)
            pngc_trimmed.trim(xmin, xmin + 450, ymin, ymin + 450)
            pngc_trimmed.save_png(make_png_name(output_path, filename, suffix + str(counter)))

# -----------------------------------------------------------------------------

def run_trim(filename, weight_file, output_path, log_switch=False,
        stat_switch=True):
    '''
    The main controller for the png creation. Checks for and creates an
    output folder. Opens the data header extention. Uses a pngcreator
    instance to create trimmed and scaled pngs.
    '''
    #import pdb; pdb.set_trace()
    logger.info('filename: {0}'.format(filename))
    astrodrizzle_mode = filename.split('_')[-3]
    logger.info('astrodrizzle mode: {0}'.format(astrodrizzle_mode))

    # Define a default output folder
    # Make the output folder if it doesn't exist.
    if output_path == None:
        output_path = os.path.join(os.path.dirname(filename), 'png')
    test = os.access(output_path, os.F_OK)
    if test == False:
        os.mkdir(output_path)

    # If we want to output before-after histograms for the image
    # manipulations we make, stat_switch will be True.
    if stat_switch:
        positive_stat = make_png_name(output_path, filename, 'positive_stat')
        log_stat = make_png_name(output_path, filename, 'log_stat')
        threshold_clip_stat = make_png_name(output_path, filename, 'threshold_clip_stat')

    # Otherwise, setting it to false prevents computing the histograms.
    else:
        positive_stat = False
        log_stat = False
        threshold_clip_stat = False

    # Get the data.
    data = get_fits_data(filename)
    weight_data = get_fits_data(weight_file)

    # Create Linear full image
    logger.info('Creating linear PNGs')
    pngc_linear = PNGCreator(data)
    pngc_linear.threshold_clip(minimum = 0.0001, maximum = 2e5, 
                               output = threshold_clip_stat)

    if log_switch:
        pngc_log = PNGCreator(pngc_linear.data)

    pngc_linear.compress()
    pngc_linear.save_png(make_png_name(output_path, filename, 'linear'))

    # Create Log full Image
    if log_switch:
        logger.info('Creating log PNGs')

        #pngc_log.positive(output = positive_stat)
        pngc_log.log(output = log_stat)
        pngc_log.compress()
        pngc_log.save_png(make_png_name(output_path, filename, 'log'))

    else:
        logger.info('Skipping log pngs.')

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
