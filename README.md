HST Moving Tartget Pipeline
===========================

The Hubble Space Telescope (HST) Moving Target Pipeline (MTP) is an image processing pipeline specifically designed for to unique processing challenges of solar system ("moving target") data. 

The pipeline take as its input FITS (Flexible Image Transport System) images and produces the following outputs. The outputs and processing steps are described in detail further in this document.

 - Reprocessed FITS files
 - Dyanmically scaled PNG preview images
 - A database of expected ephemerides for targets with known moons.
 - Ephemeris overlays labeling moons.

The pipeline is compatible with images from the following active and legacy HST cameras: 

 - Advanced Camera for Surverys (ACS):
  - High Resolution Channel (HRC)
  - Solar Blind Channel (SBC)
  - Wide Field Channel (WFC)
 - Wide Field Camera 3 (WFC3): 
  - IR
  - UVIS
 - Wide Field Plantary Camera 2 (WFPC2)

Overview
--------

MTPipeline is written in pure Python with some Python-wrapped C extensions. The pipeline can actually be viewed as two separate pipelines. One for producing the FITS and PNG files and a second for producing the ephemerides database. We will discuss both of these in order.

Imaging Pipeline
----------------

The steps for the imaging pipeline are:

 - Cosmic ray rejection
 - Drizzling
 - PNG Creation

### Cosmic Ray Rejection

Single-image cosmic ray rejection is performed using lacosmicsx, C. Mccully's python-wrapped C implementation of the Laplacian cosmic ray detection algorithm (LA Cosmics). 

lacosmicx: https://github.com/cmccully/lacosmicx
LA Cosmic: http://www.astro.yale.edu/dokkum/lacosmic/

This step produces a new FITS product. If the input was, for instance, an
ACS/HRC observation of Jupiter and its moon Europa in the F606 filter, say 

    asdfghjkl_flt.fits

The resulting output would be

    hlsp_mt_hst_acs-hrc_asdfghjkl_jupiter-europa_f606w_v1-0_flt.fits

Were the input a WFPC2 observation of the same,

    asdfghjkl_c0m.fits
    asdfghjkl_c1m.fits

The resulting output would be

    hlsp_mt_hst_wfpc2_asdfghjkl_jupiter-europa_f606w_v1-0_c0m.fits
    hlsp_mt_hst_wfpc2_asdfghjkl_jupiter-europa_f606w_v1-0_c1m.fits

CR rejection is performed with different settings for each detector, and, in the case of WFPC2, different settings for each chip. These can be found in `MTPipeline/cosmicx_cfg`.

Prior to running cosmic ray rejection, the pipeline sets all pixels in the
image with a value below -10 to 0. Pixels with values in the negative thousands
have been observed within ACS and WFC3 images, and not just along the chip
gaps, which typically have suspect pixel values. These pixels are presumably
the result of errors in the subtraction pipeline which produces `_flt.fits`
images. When run through CR rejection, however, pixels near these highly
negative pixels will frequently be marked as cosmic rays, due to the sharp
slope in the pixel value. When their surrounding environment is averaged, the
negative pixel predominates, and often the new values for the "bad" pixels will
be negative. As a result, these highly negative pixels spread into
large negative blobs after CR rejection. We clip all pixels below -10 to
eliminate this effect. It is believed that this does not impact any science
content, as pixels with such highly negative values are already bad to begin
with.

### Drizzling

Single-image drizzling is performed using the AstroDrizzle tool in STScI's
DrizzlePac software. AstroDrizzle corrects for geometric distortion, makes
calibration adjustments, and stitches the images from multiple chips into a
single-extension FITS image. It aligns this image with the WCS.

DrizzlePac: http://www.stsci.edu/hst/HST_overview/drizzlepac

This step takes both the original FITS file and the CR-rejected FITS output of
the CR-rejection step. Each detector has its own unique configuration
determined by the files in the `astrodrizzle_cfg` folder.  Users can change the
settings by editing those files.


This step looks for two files: the cr rejected output file, and the original input file. That is, it takes inputs files like:

    asdfghjkl_flt.fits
    hlsp_mt_hst_acs-hrc_asdfghjkl_jupiter-europa_f606w_v1-0_flt.fits

And will output, respectively,

    hlsp_mt_hst_acs-hrc_asdfghjkl_jupiter-europa_f606w_v1-0_sci.fits
    hlsp_mt_hst_acs-hrc_asdfghjkl_jupiter-europa_f606w_v1-0_img.fits
    hlsp_mt_hst_acs-hrc_asdfghjkl_jupiter-europa_f606w_v1-0_wht.fits

The `_sci.fits` file is the AstroDrizzle CR-rejected output, and the `_img.fits` file is the AstroDrizzle output of the original input file. The `_wht.fits` file is a weight map denoting pixel quality.

Note that AstroDrizzle produces other outputs in this process, like
`_dqmasks.fits` files, which we automatically delete.

#### CTE Correction

The image processing pipeline does not perform pixel-based CTE correction. Pixel-based CTE correction exists [for WFC3/UVIS](http://www.stsci.edu/hst/wfc3/ins_performance/CTE/), and for ACS/WFC as the [`PCTECORR` routine within `CALACS`](http://ssb.stsci.edu/doc/stsci_python_dev/acstools.doc/acstools.pdf).

Pixel-based CTE correction was not implemented into the pipeline for several
reasons. It is not supported for cameras other than WFC3/UVIS and ACS/WFC,
which comprise only 1/5 of the present Moving Target dataset. It is highly
computationally expensive, taking approximately 15 minutes to run on the
smallest UVIS subarrays, and takes about an hour or more for larger frames. It
is most relevant for those wishing to perform aperture photometry on point
sources, which are a minority in our dataset. Finally, pixel-based CTE
correction, developed to work on point sources, has undesireable effects on the
limbs of extended sources, such as planets and moons, which comprise the
majority of our dataset.

### PNG Creation

Two PNG preview images are produced per AstroDrizzle output, one with a linear
scaling, another with a logarithmic scaling. In general, the linear scaling is
useful for fields containing extended sources, such as planets, whereas the
logarithmic scaling is useful for displaying dimmer fields consisting of point
sources. 

The PNG preview images should not be used for any scientific application. To
yield a useful scaling, all pixel values about 20,000 have been set to 20,000,
and all negative pixels are set to 0 before a linear or logarithmic stretch is
applied. 

--- Lots of images  ---

The PNG scaling is performed in the matplotlib library with the `agg` backend and written using the Pillow fork of the Python Image Library (PIL).

Ephemerides Pipeline
-------------------

The ephemerides pipeline exists to help catalog the rich set of "incidental" observations that occur when observing an object with known moons. We do not attempt to automatically identify any other types of incidental observations such as asteroids. Finally, these ephemerides are predicted positions only, no validation of fidelity with the image is performed. The ephemerides are generated by sending target, date, and time information to the JPL HORIZONS system.

The steps for the ephemerides pipeline are:

 - Target name normalization
 - JPL Horizons query
 - Coordinate transformation (celestial to physical)

### Target Name Normalization

The first step in generating the ephemerides is normalizing the observer generated  target name in the FITS `TARGNAME` header keyword in a object name recognized by the JPL HORIZONS system. The `TARNAME` value is matched against the names in the `planets_and_moons.txt` file. Because the same target could be called `Jupiter`, `jupiter`, `jup`, `jup-io`, etc. this is essentially a string parsing problem. 

### JPL Horizons Query

We communicate with the JPL HORIZONS system using an undocumented CGI interface. We were explicitly given permission to use this interface by the JPL HORIZONS engineers. Please do not use this CGI without consulting with them as well. This query returns, the predicted RA, Dec, magnitude, and diameter of the object.

### Coordinate Transformation

The last step is to translate the HORIZONS RA and Dec information into the pixel space of the image. This is done using pixel scale, the reference pixel, and the pointing information from the header.

Installation
------------

### At STScI

STScI provides many of the pipeline's external dependencies at various
locations on its filesystem. However, the accessibility of some of these
dependencies varies between the filesystems seen by the Institute's Macs and
 by the RedHat science cluster. Two different installation procedures are thus provided. 

#### On Macs:

The ssbx development distribution of Ureka is required. Install it following the
instructions [here](http://ssb.stsci.edu/ssb_software.shtml).

The AstroDrizzle step in the pipeline requires defining three variables in your pipeline. If you use bash,

    export uref=/grp/hst/cdbs/uref/
    export iref=/grp/hst/cdbs/iref/
    export jref=/grp/hst/cdbs/jref/

These can be added to your `.bashrc`, along with the `ur_setup` command above. 

If you use tcsh, add these to your `.cshrc`. 

    setenv uref /grp/hst/cdbs/uref/
    setenv iref /grp/hst/cdbs/iref/
    setenv jref /grp/hst/cdbs/jref/

Don't forget to start a new terminal session if you are adding these to your terminal profile files. Now, cd to `MTPipeline/`, and run

`python setup.py develop`

This takes advantage of Python's `setuptools` to install or locate the
remaining external dependencies. If everything goes well, it will do two things:

1. Build the C components of `lacosmicx`, for which it needs the `cfitsio`
   library. The path to this library on the institute's filesystem is
   hard-coded in `setup.py`. If you are seeing errors involving '.h` files, then the
   location of the `cfitsio` library has changed, and you should see `setup.py`
   for more information.

2. Install any remaning python modules, such as Pillow, pymysql, psuitl.

In order to run 

This should suffice to install the pipeline in-place on Macs.

#### On the RedHat Science Cluster

The ssbx development version of Ureka is already installed on science3 and
science4. Use it by adding the following to your `.setenv`:

    # If a local Ureka installation is active (i.e. ur_setup has been executed)
    # do nothing. Otherwise load SSB's build in /usr/stsci
    if ( ! $?UR_DIR ) then
        if ( -f /usr/stsci/envconfig.mac/cshrc ) then
            source /usr/stsci/envconfig.mac/cshrc
            ssbx
        endif
    endif

Also in `.setenv`, define the variables

    setenv uref /grp/hst/cdbs/uref/
    setenv iref /grp/hst/cdbs/iref/
    setenv jref /grp/hst/cdbs/jref/

Make sure to restart your terminal session after making these changes.

As this version of Ureka is read-only, however, the pipeline's external modules
will need a separate environment to install into. Following the instructions
[here](http://ssb.stsci.edu/customize_python_environment.shtml), to set up and
activate a virtual environment for this purpose.

`setup.py` is currently configured to install on a Mac connected to the
institute filesystem. The science cluster sees a slightly different filesyste.
Edit `setup.py` to change the paths

    cfitslib_path = '/sw/include'
    cfitsinc_path = '/sw/lib' 

to

    cfitslib_path = '/usr/include'
    cfitsinc_path = '/usr/lib' 

Having done this, run

    python setup.py develop

The pipeline should be ready to run.

### External Users

Installing the pipeline, at least the image processing pipeline, outside the
institute filesystem is entirely possible. Successfully running it, however,
faces hurdles. 

All the image processing pipeline should require is a cfitsio
library (which does not need to be built) and  a Python 2.7 installation with
NumPy. Follow the instructions in setup.py to point setuptools to the cfitsio
library.

The pipeline has been successfully installed on Ubuntu virtual environments
provided by Travis CI. The automated script for doing so can be found in
`MTPipeline/.travis.yml`. Note that, at the moment, that script sets the
`CPLUS_INCLUDE_PATH` and `LIBRARY_PATH`, and so it is not wisely used outside
of a fresh virtual environment.

The main hindrance to running the pipeline outside of the STScI filesystem
is the AstroDrizzle step. AstroDrizzle requires reference files, the path to
which is defined by the uref, iref, and jref environment variables. There are
more than a terabyte of reference files in total, and different referrences
will be required for the proper processing of different input images.

The AstroDrizzle step will run, however, so long as the paths described in the
installation guide are defined. If it is unable to find the appropriate
reference files in those paths, AstroDrizzle will simply skip the steps
requiring them. The resulting output files appear superficially correct, with
the chips stitched together, corrected for geometric distortion, and the
resulting image aligned with the WCS.  However, the outputs will not have
undergone slight calibration corrections.

The cosmic ray rejection and png creation should both be fully functional outside
the Institute's filesystem.

Use
---
The standard interface for running the pipeline is through the terminal,
calling various python scripts that drive different sections of the pipeline.

From a usage perspective, the pipeline can be divided up into three sections:

 - Image processing pipeline
 - Database and ephemeris pipeline

Each is run by their own separate scripts.

However, before the any component of the pipeline is run, make a copy of
`MTPipeline/template_settings.yaml`, rename it to `MTPipeline/settings.yaml`,
and edit the values within.

### Image Processing Pipeline

The image processing pipeline should be run from the top level directory, `MTPipeline/`,
by calling the following script:

    python scripts/production/run_imaging_pipeline.py -filelist "/path/to/files/*.fits"

The `-filelist` argument accepts a glob wildcard search string. The imaging pipeline will only process input files of the formats 

    ib2k95nqq_flt.fits

for ACS and WFC inputs, or

    u2h50203t_c0m.fits
    u2h50203t_c1m.fits

for WFPC2 inputs. If other files are found as a result of the filelist search
string, such as pipeline outputs files, they will be excluded.

`run_imaging_pipeline()` also accepts the follwoing optional flags

 - output_path: sets the directory the output files are written to. By default,
 ouputs are written to the same directory as the input file. This is reccomended.
 - no_cr_reject, -no_astrodrizzle, -no_png: if these flags are set to True, the pipeline will skip these steps.
 - reproc: if set to True, the pipeline will reprocess its outputs, even if
   they already exist.


### Ephemeris Pipeline

Creating ephemeris overlays requires an already-built MySQL database, consisting of, most importantly, two tables: the `master_images` table and the `master_finders` table. These can be built by:

    python mtpipeline/ephem/build_master_images_table.py -filelist '/astro/ -reproc

    python mtpipeline/ephem/build_master_finders_table.py  -missing_only



Contacts
--------

**Ariel Bowers**  
Space Telescope Science Institute (STScI)  
abowers [at] gmail [dot] com

**Alex C. Viana**  
http://acviana.github.com/  
alex [dot] costa [dot] viana [at] gmail [dot] com  

**Kevin Hale**
Harvey Mudd College
kevinfhale [at] gmail [dot] com
  
**Space Telescope Science Institute (STScI)**  
http://www.stsci.edu  
  
**CosmoQuest**  
http://cosmoquest.org/  

License
=======

Fast Cosmics is licensed under a 3-clause BSD style license:

Copyright (c) 2013, Space Telescope Science Institute.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
- Neither the name of Space Telescope Science Institute, CosmoQuest, nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


