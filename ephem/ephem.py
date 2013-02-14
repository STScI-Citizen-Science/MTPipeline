import argparse
import coords
import datetime
import glob
import os
import pyfits
import telnetlib

# ----------------------------------------------------------------------------

def calc_delta(file_dict):
    '''
    Find the difference between the JPL coordinates at the HST 
    reference pixel coordinates. Perform the difference in degrees and 
    return the result in pixels.
    '''
    assert isinstance(file_dict, dict), 'Expected dict got ' + str(type(file_dict))
    
    # Get the JPL coordinates in degrees
    jpl_pos = coords.Hmsdms(
        file_dict['jpl_ra'] + ' ' + file_dict['jpl_dec'])
    file_dict['jpl_ra'], file_dict['jpl_dec'] = jpl_pos._calcinternal()
    
    # Get the HST coordinates in degrees
    hst_pointing = coords.Degrees(
        (file_dict['ra_targ'], file_dict['dec_targ']))
    file_dict['ra_targ'], file_dict['dec_targ'] = hst_pointing.a1, hst_pointing.a2

    # Take the difference and convert to pixels.
    delta_x = (file_dict['ra_targ'] - file_dict['jpl_ra']) * (3600. / 0.05)
    delta_y = (file_dict['dec_targ'] - file_dict['jpl_dec']) * (3600. / 0.05)
    assert isinstance(delta_x, float), 'Expected dict got ' + str(type(delta_x))
    assert isinstance(delta_y, float), 'Expected dict got ' + str(type(delta_y))
    return delta_x, delta_y

# ----------------------------------------------------------------------------

def calc_ephem(file_dict):
    '''
    Calculate the x and y position of the ephemeris in detector
    coordinates.
    '''
    assert type(file_dict) == dict, 'Expected dict type got ' + str(type(file_dict))
    ephem_x = file_dict['targ_x'] + file_dict['delta_x']
    ephem_y= file_dict['targ_y'] + file_dict['delta_y']    
    return ephem_x, ephem_y

# ----------------------------------------------------------------------------

def calc_targ(file_dict):
    '''
    Calculate the x and y positions of the target in detector 
    coordinates.
    '''
    assert type(file_dict) == dict, 'Expected dict type got ' + str(type(file_dict))
    refpic_pointing = coords.Degrees(
        (file_dict['CRVAL1'], file_dict['CRVAL2']))
    file_dict['CRVAL1'], file_dict['CRVAL2'] = refpic_pointing.a1, refpic_pointing.a2
    delta_x = (file_dict['ra_targ'] - file_dict['CRVAL1']) * (3600. / 0.05)
    delta_y = (file_dict['dec_targ'] - file_dict['CRVAL2']) * (3600. / 0.05)
    targ_x = file_dict['CRPIX1'] + delta_x
    targ_y = file_dict['CRPIX2'] + delta_y
    return targ_x, targ_y

# ----------------------------------------------------------------------------

def convert_datetime(header_dict):
    '''
    Builds a datetime object from header keywords and returns a 
    datetime object in the JPL Horizons format.
    '''
    header_dict['header_time'] = datetime.datetime.strptime(
        header_dict['date_obs'] + ' ' + header_dict['time_obs'],
        '%Y-%m-%d %H:%M:%S')
    header_dict['horizons_start_time'] = header_dict['header_time'].strftime('%Y-%b-%d %H:%M')
    header_dict['horizons_end_time'] = header_dict['header_time'] + datetime.timedelta(minutes=1)
    header_dict['horizons_end_time'] = header_dict['horizons_end_time'].strftime('%Y-%b-%d %H:%M')
    return header_dict

# ----------------------------------------------------------------------------

def get_header_info(filename):
    '''
    Gets the header info from the FITS file. Checks to ensure that the 
    target name, after string parsing, matches a known planet name.
    '''
    assert os.path.splitext(filename)[1] == '.fits', 'Expected .fits got ' + filename
    output = {}
    output['targname'] = pyfits.getval(filename, 'targname').lower().split('-')[0]
    output['date_obs'] = pyfits.getval(filename, 'date-obs')
    output['time_obs'] = pyfits.getval(filename, 'time-obs')
    output['ra_targ']  = pyfits.getval(filename, 'ra_targ')
    output['dec_targ'] = pyfits.getval(filename, 'dec_targ')
    output['CRVAL1']   = pyfits.getval(filename, 'CRVAL1')
    output['CRVAL2']   = pyfits.getval(filename, 'CRVAL2')
    output['CRPIX1']   = pyfits.getval(filename, 'CRPIX1')
    output['CRPIX2']   = pyfits.getval(filename, 'CRPIX2')
    planet_list = ['mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    error = 'Header TARGNAME not in planet_list'
    assert output['targname'] in planet_list, error
    return output

# ----------------------------------------------------------------------------

def make_moon_dict(filename, file_dict):
    '''
    Parses the text file for id numbers of the moons and the planet. 
    Returns a dict.
    '''
    path_to_code = os.path.dirname(__file__)
    f = open(os.path.join(path_to_code, 'planets_and_moons.txt'))
    full_moon_list = f.readlines()
    f.close()

    moon_dict = {}
    moon_switch = False
    for line in full_moon_list:
        line = line.strip().split()
        if line != [] and line[-1] == file_dict['targname']:
            moon_switch = True
        if moon_switch:
            if line != []:
                moon_dict[line[1]] = {'id': line[0]}
            else:
                break
    return moon_dict

# ----------------------------------------------------------------------------    

def telnet_session(command_list, verbose=False):
    '''
    Performs the telnet operations and returns the ephemeride data.
    '''
    tn = telnetlib.Telnet()
    tn.open('ssd.jpl.nasa.gov', '6775')
    output = tn.read_until('Horizons>', timeout = 5)
    if verbose:
        print output
    for command in command_list:
        tn.write(command + '\r\n')
        output = tn.read_until('] :', timeout = 5)
        if command == '1,2,3,4':     
            data = output
        if verbose:
            print output
    tn.close()
    return data

# ----------------------------------------------------------------------------

def trim_data(data):
    '''
    Grab the relevant information from the telnet output.
    '''
    section = 0
    output = {}
    keys = []
    data = data.split('\n')
    for line in data:
        line = line.strip()
        if line != '':
            if line[0] == '*':
                section += 1
            elif section == 1:
                line = line.split()
                if line[0] == 'Target':
                    output['target'] = line[3]
            elif section == 2:
                pass
            elif section == 4:
                pass
            elif section == 5:
                if line[0] != '$':
                    line = line.split()
                    output['date'] = line[0] + ' ' + line[1]
                    output['jpl_ra'] = line[2] + ':' + line[3] + ':' + line[4]
                    output['jpl_dec'] = line[5] + ':' + line[6] + ':' + line[7]
                    output['jpl_re_apparent'] = line[8] + ':' + line[9] + ':' + line[10]
                    output['jpl_dec_apparent'] = line[11] + ':' + line[12] + ':' + line[13]
                    output['jpl_ra_delta'] = line[14]
                    output['jpl_dec_delta'] = line[15]
                    return output

#----------------------------------------------------------------------------
# The main controller.
#----------------------------------------------------------------------------

def ephem_main(filename):
    '''
    The main controller for the ephem.py module. 
    '''
    file_dict = get_header_info(os.path.abspath(filename))
    file_dict = convert_datetime(file_dict)
    moon_dict = make_moon_dict('planets_and_moons.txt', file_dict)
    for moon in moon_dict.keys():
        command_list = [moon_dict[moon]['id'],
            'e', 'o', 'geo',
            file_dict['horizons_start_time'],
            file_dict['horizons_end_time'],
            '1m', 'y','1,2,3,4', 'n']
        data = None
        while data == None:
            data = telnet_session(command_list, verbose=True)
        data_dict = trim_data(data)
        file_dict.update(data_dict)
        moon_dict[moon]['delta_x'], moon_dict[moon]['delta_y'] = calc_delta(file_dict)
        moon_dict[moon]['targ_x'], moon_dict[moon]['targ_y'] = calc_targ(file_dict)
        moon_dict[moon]['ephem_x'], moon_dict[moon]['ephem_y'] = calc_ephem(moon_dict[moon])
    return moon_dict
