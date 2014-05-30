#! /usr/bin/env python

from mtpipeline.get_settings import get_settings

def check_filesystem_completeness_main():
    """
    
    Printing the settings located in settings.yaml
        
    """
    print get_settings()

if __name__ == "__main__":
    check_filesystem_completeness_main()