MTPipeline
==========

MTPipeline (Moveing Target Pipeline) is an imaging pipeline for Hubble Space Telescope (HST) Wide-Field Planetary Camera 2 (WFPC2) images. It produces processed PNGs from FITS images (Flexible Image Transport System) MTPipeline  was created for use by the CosmoQuest Planet Investigators project and the Space Telescope Science Institute (STScI).

_This is project is still under active development. This is not a stable release. Software license TBA._

Overview
--------

MTPipeline is written in pure Python. The processing steps applied to each input are listed below followed by descriptions.

- Cosmic ray rejection
- Drizzling
- Scaling

### Cosmic Ray Rejection

Single-image cosmic ray rejection is performed using cosmics.py, a python implementation of the Laplacian cosmic ray detection algorithm (LA Cosmics). This step produces a new FITS product named `filename_cr_c0m.fits`.  

cosmics.py: http://obswww.unige.ch/~tewes/cosmics_dot_py/  
LA Cosmic: http://www.astro.yale.edu/dokkum/lacosmic/

### Drizzling

Single-image drizzling is performed using the AstroDrizzle tool in STScI's DrizzlePac software. This step takes both the original FITS file and the CR-rejected FITS output of the CR-rejection step. Depending on the options the drizzling step will produce between 1 and 3 outputs for each input. These outputs at the "wide", "slice", and "zoom" scalings.

DrizzlePac: http://www.stsci.edu/hst/HST_overview/drizzlepac

### Scaling

The images are optimally scaled for the CosmoQuest web tool and then written to a PNG file. The scaling algorithm is still being refined. The PNG is produced using the Python Image Library (PIL).

Future Updates
--------------

* Software license
* Scaling algorithm description
* User's Guide

Contacts
--------

**Alex C. Viana**  
Space Telescope Science Institute (STScI)  
http://acviana.github.com/  
viana [at] stsci [dot] edu  
alex [dot] costa [dot] viana [at] gmail [dot] com  
  
**Space Telescope Science Institute (STScI)**  
http://www.stsci.edu  
  
**CosmoQuest**  
http://cosmoquest.org/  

