#!/usr/bin/env python

"""
Edited 2014

Setuptools-style setup.py file for the mtpipeline package.

This setup script will install the mtpipeline package, making it
importable by python code located in any directory. In the process, it
builds cmccully's lacosmicx, a python-wrapped c implementation of van
Dokkum's laplacian cosmic ray identification routine.

This script should be able to install the mtpipeline package when run on a
system with 

Python 2.7
numpy
A built cfitsio library, in '/sw/lib', and cfitsio .h files in 
'/sw/include'

These, at the moment, are standard on STScI machines. 

But it is possible the location of the cfitsio library on the Institute
filesystem has changed. If so, you need to edit cfitslib_path to point to
a directory containing `libcfitsio.a`, and cfitsinc_path to one containing
`drvrsmem.h', `fitsio.h`, `fitsio2.h`, and `longnam.h`.

We require numpy to be already installed, as its :func:`get_include`
should yield where numpy's c header files are located. At present, this
does not appear to be the case. Instead, they are located inside a
direcory named `numpy` within the path given by :func:'`get_include`. If
you are getting an error involving not being able to find `arrayobject.h`,
then this is no longer true, and you will have to find where the numpy
header files are relative to the path returned by :func:`get_include`, and
change numpy_path accordingly.
"""

from setuptools import find_packages
from setuptools import setup
from setuptools import Extension

cfitslib_path = '/sw/include'
cfitsinc_path = '/sw/lib'

try:
    # Numpy knows more or less where its header files are.
    import numpy as np
    # ... although it seemingly needs a little help.
    numpy_path = np.get_include() + '/numpy/'
except:
    print 'Failed to find numpy. numpy should be installed.'

module1 = Extension('_lacosmicx',
                    include_dirs = [cfitsinc_path, numpy_path],
                    library_dirs = [cfitslib_path],
                    libraries = ['cfitsio'],
                    extra_compile_args=['-O3','-funroll-loops'],
                    sources = ['src/lacosmicx.cpp',
                               'src/lacosmicx_py.cpp',
                               'src/functions.cpp']
                    )

setup(name='MTPipeline',
      description='HST Moving Target Pipeline',
      author='Space Telescope Science Institute',
      url='https://github.com/STScI-Citizen-Science/MTPipeline',
      packages=find_packages(),
      install_requires=['matplotlib', 'numpy', 'Pillow', 'pymysql', 'pyyaml', 
                        'sqlalchemy', 'psutil'],
      ext_modules=[module1],
      install_requires=['matplotlib', 'numpy', 'Pillow', 'pymysql', 
			'pyyaml', 'sqlalchemy', 'psutil']
     )
