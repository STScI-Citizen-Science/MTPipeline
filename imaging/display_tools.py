#! /usr/bin/env python

'''
Tools for plotting and displaying images from the MTPipeline
'''

import matplotlib
import numpy as N

# Try to use the Agg backend to prevent the images from being 
# displayed to the screen.
try: 
    matplotlib.use('agg')
except:
    print 'Failed loading agg backend.'

import matplotlib.cm as cm
import pylab as P

# -----------------------------------------------------------------------------

def before_after(before_array, after_array, before_array_name='Before',
        after_array_name='After', show=True, output=False, pause=False):
    '''
    Display a before, after, and delta array with a log-historgram.
    '''
    # Plot the before and after images.
    P.clf()
    delta_array = after_array - before_array

    # Step through the arrays.
    for array, image_counter, array_name in \
            zip([before_array, after_array, delta_array], 
                [1,3,5], 
                [before_array_name, after_array_name, 'Delta']):
        
        # Create the image.
        ax1 = P.subplot(320 + image_counter)
        ax1.imshow(array, cmap = cm.gray)
        ax1.grid(True)
        
        # Set the title
        ax1.set_ylabel(array_name) 
        
        # Create the histogram.
        ax1 = P.subplot(320 + image_counter + 1)
        n, bins, patches = ax1.hist(
            array.ravel(), 100, facecolor = 'green', 
            alpha=0.75, log = True)
        ax1.grid(True)
        
    # Draw, write to file, pause.   
    if output != False:
        assert type(output) == str, 'Output must be a string type.'
        assert output[-4:] == '.png', 'Output must end in .png'
        P.savefig(output)  
    if show == True:
        P.draw()
    if pause == True:
        raw_input('Paused') 

# -----------------------------------------------------------------------------

def display(array, title = ''):
    '''
    Plot to the screen.
    '''
    P.clf()
    ax1 = P.subplot(111)
    ax1.set_title(title)
    ax1.imshow(array, cmap=cm.gray)
    ax1.grid(True)
    P.draw()
    
    raw_input('wait')
    
# -----------------------------------------------------------------------------

def histo_plot(array, title):
    '''
    Created: 11/12/11 (Viana)
    '''
    P.clf()
    ax1 = P.subplot(121)
    n, bins, patches = ax1.hist(
        array.ravel(), 50, facecolor='green', alpha=0.75)
    ax1.grid(True)
    ax2 = P.subplot(122)
    ax2.imshow(array, cmap=cm.gray)
    ax2.grid(True)
    ax2.set_title(title)
    P.figtext(
        0.5, 0.95, simple_stat(array), ha='center', 
        color='black', weight='bold', size='large')
    ax2.text(
        1, -0.6, mode, ha = 'right', color = 'black',
        transform = ax2.transAxes)
    P.draw()
    P.savefig(title + '.png')

# -----------------------------------------------------------------------------

def mark_pixels(array, mask):
    '''
    Mark pixels in a mask with a red pixel.
    '''
    P.clf()
    ax1 = P.subplot(111)
    ax1.imshow(array, cmap = matplotlib.cm.gray)
    ax1.plot(mask[1], mask[0], 'r.', alpha = 0.5)
    P.draw()

# -----------------------------------------------------------------------------

def simple_stat(array):
    '''
    Created: 11/24/11 (Viana)
    '''
    min_val = N.min(array)
    max_val = N.max(array)
    med_val = N.median(array)
    mean_val = N.mean(array)
    std_val = N.std(array)

    text = min_val, max_val, med_val, mean_val, std_val
    format = 'Min: %5.3f Max: %5.3f Median: %5.3f, Mean: %5.3f, STD: %5.3f'
    return format % text
        