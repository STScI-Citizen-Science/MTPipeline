#! usr/bin/env python

'''
Viewing tools for WFC3 images.
'''

import argparse
import glob
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.cm as cm
import matplotlib.patches as mpatches 
import os
import pyfits


from PIL import Image

#----------------------------------------------------------------------------
# Connect the SQLAlchemy ORM declaritive base classes.
#----------------------------------------------------------------------------

from database_interface import MasterImages
from database_interface import MasterFinders

from database_interface import session

#----------------------------------------------------------------------------
# 
#----------------------------------------------------------------------------

class EphemPlot(object):
    '''
    Class for creating a overplot of the ephemerides.
    '''
    def __init__(self, filename):
        '''
        Take the png name and check the input.
        '''
        assert os.path.splitext(filename)[1] == '.png', 'Expected a .png file.'
        self.filename = filename

    def getcrpix(self):
        '''
        Get the cr pixel information from the single_sci.fits file.
        '''
        fitsfile = master_images_query = session.query(MasterImages.fits_file).filter(\
            MasterImages.name == os.path.basename(self.filename)).one()[0]
        png_path = os.path.split(self.filename)[0]
        png_path = os.path.split(png_path)[0]
        fitsfile = os.path.join(png_path, fitsfile)
        self.crpix1 = pyfits.getval(fitsfile, 'CRPIX1', 0)
        self.crpix2 = pyfits.getval(fitsfile, 'CRPIX2', 0)

    def getEphem(self):
        '''
        Get the ephemerids information from the database.
        '''
        master_images_query = session.query(MasterImages.id).filter(\
            MasterImages.name == os.path.basename(self.filename)).one()
        master_finders_query = session.query(MasterFinders).filter(\
            MasterFinders.master_images_id == master_images_query.id).count()
        assert master_finders_query != 0, \
            'No record found in master_finders_query'
        master_finders_query = session.query(MasterFinders).filter(\
            MasterFinders.master_images_id == master_images_query.id).all()
        self.master_finders_query = master_finders_query

    def plot_image(self):
        '''
        Perform the actual plotting
        '''
        data = Image.open(self.filename)
        fig = plt.figure()
        ax1 = plt.subplot(111)
        im = ax1.imshow(data, cmap=cm.gray)
        ax1.set_xlim(ax1.get_xlim())
        ax1.set_ylim(ax1.get_ylim())
        for moon in self.master_finders_query:
            if isinstance(moon.diameter, float) and (  moon.diameter/0.05) > 10:
                diam = moon.diameter/0.05 #conversion form arcsecs to pixels
            else:
                diam = 10
            # old way of marking objects using markersize and not mpatches    
            # ax1.plot(moon.ephem_x, moon.ephem_y, 'o', markersize = 10,    
            #     markerfacecolor = 'none', markeredgecolor = 'white')
            circle = mpatches.Circle((moon.ephem_x, moon.ephem_y),
                     diam/2, fill = False, ec = "r")
            ax1.add_patch(circle)
            print args.label
            if args.label == "True":
                ax1.text(moon.ephem_x + 20, moon.ephem_y + 20, moon.object_name.title(),
                        color="blue")
          # ax1.text(moon.ephem_x, moon.ephem_y, moon.object_name, 
          #   color = 'white')
        #ax1.plot(self.crpix1, self.crpix2, 'o', markersize = 10, 
        #    markerfacecolor = 'none', markeredgecolor = 'white')
        #ax1.text(self.crpix1, self.crpix2, 
        #    'CRPIX: (' + str(self.crpix1) + ',' + str(self.crpix2) + ')', 
        #    color = 'white')
        ax1.set_title(os.path.basename(self.filename))
        outputFile = sourceFile.split('.')[0] + "_ephem.png"
        plt.savefig(outputFile)
        plt.draw()
        plt.grid(True)

#----------------------------------------------------------------------------

def ephem_viewer_main(filename):
    '''
    The main controller.
    '''
    ep = EphemPlot(filename)
    ep.getEphem()
    ep.getcrpix()
    ep.plot_image()
    
#----------------------------------------------------------------------------
# For command line execution
#----------------------------------------------------------------------------

def parse_args():
    '''
    parse the command line arguemnts.
    '''
    parser = argparse.ArgumentParser(
        description = 'Plots the ephemeride data from the database.')
    parser.add_argument(
        '-file',
        required = True,
        help = 'The file to display.')
    parser.add_argument(
        '-label',
        required = False,
        default = False,
        help = 'Toggle labelling of objects.'
        )
    args = parser.parse_args()
    return args

#----------------------------------------------------------------------------

if __name__ == '__main__':
    args = parse_args()
    rootfile_list = glob.glob(args.file)
    for sourceFile in rootfile_list:
        ephem_viewer_main(sourceFile)
