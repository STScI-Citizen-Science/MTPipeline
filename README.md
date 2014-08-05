_This is pre-release alpha version of the software. In order to provide a maintainable production-ready pipeline for the MAST group at STScI by the release deadline, the decision was made to remove the CosmoQuest-specific products from the the pipeline. The features needed to develop the CQ-specific products were for the most part in a stable beta version for the WFPC2 camera with most of remaining work focusing on performance and organization improvements. The code to produce the CQ products for the ACS and WFC3 instruments was non-existent beyond anything that could use the existing WFPC2 code without modification._

_The CQ products were removed from the pipeline with the understanding that they could be generated later (and probably more easily) by building another pipeline that takes the outputs of the MAST-specific pipeline this code will become as inputs._ 

_The **only** purpose of this release is to document the implementation of the existing CosmoQuest specific features so they can be recreated for a future pipeline to produce the CQ products. Additionally, at that time, the developers are encouraged to consult the GitHub wiki and issues for additional background information._

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

Single-image cosmic ray rejection is performed using lacosmicsx, C. Mccully's python-wrapped c implementation of the Laplacian cosmic ray detection algorithm (LA Cosmics). This step produces a new FITS product named `filename_cr_c0m.fits`.  

lacosmicx: https://github.com/cmccully/lacosmicx
LA Cosmic: http://www.astro.yale.edu/dokkum/lacosmic/

### Drizzling

Single-image drizzling is performed using the AstroDrizzle tool in STScI's DrizzlePac software. This step takes both the original FITS file and the CR-rejected FITS output of the CR-rejection step. Depending on the options the drizzling step will produce between 1 and 3 outputs for each input. These outputs at the "wide", "slice", and "zoom" scalings.

DrizzlePac: http://www.stsci.edu/hst/HST_overview/drizzlepac

### Scaling

The images are optimally scaled for the CosmoQuest web tool and then written to a PNG file. The scaling algorithm is still being refined. The PNG is produced using the Python Image Library (PIL).


Contacts
-------- 
  
**Space Telescope Science Institute (STScI)**  
http://www.stsci.edu  
  
**CosmoQuest**  
http://cosmoquest.org/  

License
=======

The HST Moving Target Pipeline is licensed under a 3-clause BSD style license:

Copyright (c) 2013, Space Telescope Science Institute.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
- Neither the name of Space Telescope Science Institute, CosmoQuest, nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


