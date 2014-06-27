#!/usr/bin/env python

"""
Setuptools-style setup.py file for the mtpipeline package.
"""

from setuptools import find_packages
from setuptools import setup

setup(name='MTPipeline',
      description='HST Moving Target Pipeline',
      author='Space Telescope Science Institute',
      url='https://github.com/STScI-Citizen-Science/MTPipeline',
      packages=find_packages(),
      install_requires=['matplotlib', 'numpy', 'Pillow', 'pymysql', 'pyyaml', 
                        'sqlalchemy', 'psutil'],
     )
