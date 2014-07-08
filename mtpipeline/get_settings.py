"""Module for the get_settings function. 

This module defines a global variable named SETTINGS which is used by 
other moduels in the mtpipeline package to define user/host specific 
settings.

Authors:
    Alex Viana, April 2014
"""

import inspect
import os
import yaml

def get_settings():
    """Return a dictionary of host specific settings.

    This function will look for a file called `settings.yaml` that 
    contains all the host specific settings for the mtpipeline 
    package. These values will be returned as a dictionary. This 
    function should never be called directly. Instead the module 
    will exectue this function upon import and create a global 
    variable called SETTINGS that can be directly imported by any 
    module that needs it. 
    
    Parameters: 
        nothing

    Returns: 
        settings : dictionary
            A dictionary of the values in the `settings.yaml` file.

    Outputs:
        nothing
    """
    # Note the os.path.dirname is called twice because the yaml file is 
    # expected to be one level above this module.
    settings_path = os.path.dirname(os.path.dirname(
        os.path.abspath(inspect.getfile(inspect.currentframe()))))
    
    try:
        settings = yaml.load(open(os.path.join(settings_path,'settings.yaml')))
    except IOError:
        settings = yaml.load(open(os.path.join(settings_path,'template_settings.yaml')))


    return settings

SETTINGS = get_settings()
