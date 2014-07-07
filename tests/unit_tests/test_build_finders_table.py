from ephem.build_finders_table import get_ephem_region
from ephem.build_finders_table import get_region_list

def test_get_ephem_region():
    '''
    Generator for the check_ephem_region function:
    '''
    # Check in the lower x bound.
    yield check_ephem_region,  424,    0,  3
    yield check_ephem_region,  425,    0,  6
    yield check_ephem_region,  426,    0,  6
    yield check_ephem_region,  449,    0,  6
    yield check_ephem_region,  450,    0,  6
    yield check_ephem_region,  451,    0,  6
    yield check_ephem_region, 1725,    0, 12

    # Check the upper x bound.
    yield check_ephem_region,    0, 1300,  1
    yield check_ephem_region,  424, 1300,  1
    yield check_ephem_region,  425, 1300,  4
    yield check_ephem_region,  426, 1300,  4
    yield check_ephem_region,  449, 1300,  4
    yield check_ephem_region,  450, 1300,  4
    yield check_ephem_region,  451, 1300,  4
    yield check_ephem_region, 1725, 1300, 10    

    # Check in the lower y bound.
    yield check_ephem_region,    0,  424,  3
    yield check_ephem_region,    0,  425,  2 
    yield check_ephem_region,    0,  426,  2 
    yield check_ephem_region,    0,  449,  2
    yield check_ephem_region,    0,  450,  2
    yield check_ephem_region,    0,  451,  2
    yield check_ephem_region,    0, 1300,  1

    # Check the upper y bound.
    yield check_ephem_region, 1725,  424, 12
    yield check_ephem_region, 1725,  425, 11 
    yield check_ephem_region, 1725,  426, 11 
    yield check_ephem_region, 1725,  449, 11
    yield check_ephem_region, 1725,  450, 11
    yield check_ephem_region, 1725,  451, 11
    yield check_ephem_region, 1725, 1300, 10

    # Check in the diagonal direction
    yield check_ephem_region,    0,    0,  3
    yield check_ephem_region,  424,  424,  3
    yield check_ephem_region,  425,  425,  5
    yield check_ephem_region,  426,  426,  5
    yield check_ephem_region,  449,  449,  5
    yield check_ephem_region,  450,  450,  5
    yield check_ephem_region,  451,  451,  5
    yield check_ephem_region, 1274,  849,  8
    yield check_ephem_region, 1275,  850, 10
    yield check_ephem_region, 1276,  851, 10
    yield check_ephem_region, 1299,  874, 10
    yield check_ephem_region, 1300,  875, 10
    yield check_ephem_region, 1301,  876, 10   
    yield check_ephem_region, 1725, 1300, 10


def check_ephem_region(x, y, region):
    '''
    Tests get_ephem_region.
    '''
    assert get_ephem_region(x,y) == region, \
        'FAILED: {}, {}, {} != {}'.format(x, y, region, get_ephem_region(x,y))


def test_get_region_list():
    '''
    Generator for the check_get_region_list function:
    '''
    # Check in the lower x bound.
    yield check_get_region_list,  424,    0, [3]
    yield check_get_region_list,  425,    0, [6, 3]
    yield check_get_region_list,  426,    0, [6, 3]
    yield check_get_region_list,  449,    0, [6, 3]
    yield check_get_region_list,  450,    0, [6, 3]
    yield check_get_region_list,  451,    0, [6]
    yield check_get_region_list, 1725,    0, [12]

    # Check in the upper x bound.
    yield check_get_region_list,    0, 1300, [1]
    yield check_get_region_list,  424, 1300, [1]
    yield check_get_region_list,  425, 1300, [4, 1]
    yield check_get_region_list,  426, 1300, [4, 1]
    yield check_get_region_list,  449, 1300, [4, 1]
    yield check_get_region_list,  450, 1300, [4, 1]
    yield check_get_region_list,  451, 1300, [4]
    yield check_get_region_list, 1725, 1300, [10]  

    # Check in the lower y bound.
    yield check_get_region_list,    0,  424, [3]
    yield check_get_region_list,    0,  425, [2, 3]
    yield check_get_region_list,    0,  426, [2, 3] 
    yield check_get_region_list,    0,  449, [2, 3]
    yield check_get_region_list,    0,  450, [2, 3]
    yield check_get_region_list,    0,  451, [2]
    yield check_get_region_list,    0, 1300, [1]

    # Check in the upper y bound.
    yield check_get_region_list, 1725,  424, [12]
    yield check_get_region_list, 1725,  425, [11, 12] 
    yield check_get_region_list, 1725,  426, [11, 12]
    yield check_get_region_list, 1725,  449, [11, 12]
    yield check_get_region_list, 1725,  450, [11, 12]
    yield check_get_region_list, 1725,  451, [11]
    yield check_get_region_list, 1725, 1300, [10]

    # Check in the diagonal direction
    yield check_get_region_list,    0,    0, [3]
    yield check_get_region_list,  424,  424, [3]
    yield check_get_region_list,  425,  425, [5, 2, 6, 3]
    yield check_get_region_list,  426,  426, [5, 2, 6, 3]
    yield check_get_region_list,  449,  449, [5, 2, 6, 3]
    yield check_get_region_list,  450,  450, [5, 2, 6, 3]
    yield check_get_region_list,  451,  451, [5]
    yield check_get_region_list, 1274,  849, [8]
    yield check_get_region_list, 1275,  850, [10, 7, 11, 8]
    yield check_get_region_list, 1276,  851, [10, 7, 11, 8]
    yield check_get_region_list, 1299,  874, [10, 7, 11, 8]
    yield check_get_region_list, 1300,  875, [10, 7, 11, 8]
    yield check_get_region_list, 1301,  876, [10]
    yield check_get_region_list, 1725, 1300, [10]    

    yield check_get_region_list,   25,  301, [3]

def check_get_region_list(x, y, region_list):
    '''
    Test get_region_list.
    '''
    assert get_region_list(x,y) == region_list, \
        'FAILED: {}, {}, {} != {}'.format(x, y, region_list, get_region_list(x,y))
