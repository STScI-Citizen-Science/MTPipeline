#! /usr/bin/env python

from mtpipeline.get_settings import SETTINGS
from mtpipeline.database.database_interface import Base, engine
from mtpipeline.database.database_interface import MasterImages
from mtpipeline.database.database_interface import MasterFinders
from mtpipeline.database.database_interface import Finders
from mtpipeline.database.database_interface import SubImages

def reset_db(conn_string):
    """
        Resets database.
        
        Parameters:
        conn_string: string
            Database name given by user when the script starts to run.
        
        Returns:
        nothing
        
        Output:
        nothing
    """
    if conn_string == str(engine.url).split('/')[-1]:
        meta = Base.metadata
        meta.drop_all()
        meta.create_all()
    else:
        print "Incorrect database name, not performing reset."

if __name__ == '__main__':
    reset_db(raw_input("You are about to reset a dababase. All existing data will be lost. Please enter the database name to confirm this action: "))