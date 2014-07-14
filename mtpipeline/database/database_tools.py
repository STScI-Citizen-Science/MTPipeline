"""General utility functions for interacting with that database."""

import datetime
from mtpipeline.database.database_interface import session

def counter(count, update=100):
    '''
    Advance the count and print a status message every 100th item.
    '''
    check_type(count, int)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if count == 0:
        print now + ': Starting processing'
    count += 1
    if count % update == 0:
        print now + ': Completed ' + str(count)
    check_type(count, int)
    return count


def check_type(instance, expected_type):
    '''
    A wrapper around my standard assert isinstance pattern.
    '''
    assert isinstance(instance, expected_type), \
        'Expected ' + str(expected_type) + ' got ' +  \
        str(type(instance)) + ' instead.'


def insert_record(record_dict, tableclass_instance):
    '''
    Insert the value into the database using SQLAlchemy.

    This is being phased out in favor of a proper __init__ method for 
    the mapped classes.
    '''
    record = tableclass_instance
    check_type(record_dict, dict)
    for key in record_dict.keys():
        setattr(record, key, record_dict[key])
    session.add(record)
    session.commit()


def update_record(record_dict, query):
    '''
    Update a record in the database using SQLAlchemy. See 
    insert_record for details.
    '''
    check_type(record_dict, dict)
    count = query.update(record_dict)
    session.commit()
