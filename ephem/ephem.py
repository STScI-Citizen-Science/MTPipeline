import coords
import datetime
import os
import pyfits
import telnetlib

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
        output = tn.read_until('] :', timeout = 2)
        if command == '1,2,3,4':     
            data = output
        if verbose:
            print output
    tn.close()
    return data

# ----------------------------------------------------------------------------

def trim_data(data):
    '''
    Grab the relevent information from the telnet output.
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
                    
# ----------------------------------------------------------------------------

def get_header_info(filename):
    '''
    Gets the header info from the FITS file. 
    '''
    output = {}
    output['targname'] = pyfits.getval(filename, 'targname')
    output['date_obs'] = pyfits.getval(filename, 'date-obs')
    output['time_obs'] = pyfits.getval(filename, 'time-obs')
    output['ra_targ']  = pyfits.getval(filename,  'ra_targ')
    output['dec_targ'] = pyfits.getval(filename, 'dec_targ')
    return output

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

def jpl_to_pixels(file_dict):
    '''
    Take the RA and Dec returned by JPL Horizons and return pixel 
    coordinates on the image.
    '''
    jpl_pos = coords.Hmsdms(
        file_dict['jpl_ra'] + ' ' + file_dict['jpl_dec'])
    hst_pointing = coords.Degrees(
        (file_dict['ra_targ'], file_dict['dec_targ']))

    file_dict['jpl_ra'], file_dict['jpl_dec'] = jpl_pos._calcinternal()
    file_dict['ra_targ'], file_dict['dec_targ'] = hst_pointing.a1, hst_pointing.a2

    print (file_dict['ra_targ'] - file_dict['jpl_ra']) * (20./15)
    print (file_dict['dec_targ'] - file_dict['jpl_dec']) * (20./15)

# ----------------------------------------------------------------------------

def main():
    '''
    '''
    file_dict = get_header_info(os.path.abspath(
        '../../Data/Neptune/u40n0102m_c0m_cr_slice_single_sci.fits'))
    file_dict = convert_datetime(file_dict)

    command_list = ['899',
        'e', 'o', 'geo',
        file_dict['horizons_start_time'],
        file_dict['horizons_end_time'],
        '1m', 'y','1,2,3,4', 'n']
    data = telnet_session(command_list, verbose=True)
    data_dict = trim_data(data)
    file_dict.update(data_dict)
    jpl_to_pixels(file_dict)

if __name__ == '__main__':
    main()

