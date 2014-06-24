import glob
logs_list = glob.glob('/astro/mtpipeline/logs/run_imaging_pipeline/*.log')
import datetime as dt

total_times_dict = {}
check_log_dict = {'cr_times': {'sum_avg': 0, 'count_avg': 0, 'avg_master': 0, 'sum_var': 0, 'var_master': 0, 'std_master': 0},
                'dr_times': {'sum_avg': 0, 'count_avg': 0, 'avg_master': 0, 'sum_var': 0, 'var_master': 0, 'std_master': 0},
                'png_times': {'sum_avg': 0, 'count_avg': 0, 'avg_master': 0, 'sum_var': 0, 'var_master': 0, 'std_master': 0}}
for log_file in logs_list:

    with open(log_file, 'r') as f:
        check_log_dict[log_file] = {'host': {'user': '', 'hostname': '', 'cpu': '', 'memory': '', 'filelist': ''},
                                    'cr_master': {'sum_sec': 0, 'count': 0, 'avg': 0, 'sum_var': 0, 'var': 0, 'std': 0},
                                    'dr_master': {'sum_sec': 0, 'count': 0, 'avg': 0, 'sum_var': 0, 'var': 0, 'std': 0},
                                    'png_master': {'sum_sec': 0, 'count': 0, 'avg': 0, 'sum_var': 0, 'var': 0, 'std': 0}}
        file_key = ''
        lines = list(f)
        for line in lines:
            list_line = line.split(' ')
            if len(list_line) <= 3:
                continue
            if 'User:' in line:
                check_log_dict[log_file]['host']['user'] = list_line[-1].strip()
   
            if 'Host:' in line:
                check_log_dict[log_file]['host']['hostname'] = list_line[-1].replace('\n', '')
                if check_log_dict[log_file]['host']['hostname'] not in total_times_dict.keys():
                    total_times_dict[check_log_dict[log_file]['host']['hostname']] = {'cr': {'avg': [], 'std': []},
                                                                                    'dr': {'avg': [], 'std': []},
                                                                                    'png': {'avg': [], 'std': []},
                                                                                    'info': {'cpu': '', 'memory': '', 'count': 0}}
   
            if 'Count:' in line:
                check_log_dict[log_file]['host']['cpu'] = list_line[-1].strip()
                if check_log_dict[log_file]['host']['cpu'] != '':
                    total_times_dict[check_log_dict[log_file]['host']['hostname']]['info']['cpu'] = check_log_dict[log_file]['host']['cpu']

            if 'Memory:' in line:
                check_log_dict[log_file]['host']['memory'] = list_line[-1].strip()
                if check_log_dict[log_file]['host']['memory'] != '':
                    total_times_dict[check_log_dict[log_file]['host']['hostname']]['info']['memory'] = check_log_dict[log_file]['host']['memory']
  
            if 'filelist:' in line:
                check_log_dict[log_file]['host']['filelist'] = list_line[-1].strip()

            if 'Current File:' in line:
                file_key = list_line[-1].replace('\n', '')
                check_log_dict[log_file][file_key] = {'cr_file': {'start': '', 'end': '', 'diff': 0},
                                                    'dr_file': {'start': '', 'end': '', 'diff': 0},
                                                    'png_file': {'start': '', 'end': '', 'diff': 0}}

            if 'Running cr_reject' in line:
                check_log_dict[log_file][file_key]['cr_file']['start'] = list_line[-5]

            if 'Done running cr_reject' in line:
                if check_log_dict[log_file][file_key]['cr_file']['start'] != '':
                    check_log_dict[log_file][file_key]['cr_file']['end'] = list_line[-6]
                    start_dt = dt.datetime.strptime(check_log_dict[log_file][file_key]['cr_file']['start'], '%H:%M:%S')
                    end_dt = dt.datetime.strptime(check_log_dict[log_file][file_key]['cr_file']['end'], '%H:%M:%S')
                    diff = (end_dt - start_dt)
                    check_log_dict[log_file][file_key]['cr_file']['diff'] = diff.seconds
                    check_log_dict[log_file]['cr_master']['sum_sec'] += diff.seconds
                    check_log_dict[log_file]['cr_master']['count'] += 1
                    total_times_dict[check_log_dict[log_file]['host']['hostname']]['info']['count'] += 2
 
            if 'Running Astrodrizzle' in line:
                check_log_dict[log_file][file_key]['dr_file']['start'] = list_line[-5]

            if 'Done running astrodrizzle' in line:
                if check_log_dict[log_file][file_key]['dr_file']['start'] != '':
                    check_log_dict[log_file][file_key]['dr_file']['end'] = list_line[-6]
                    start_dt = dt.datetime.strptime(check_log_dict[log_file][file_key]['dr_file']['start'], '%H:%M:%S')
                    end_dt = dt.datetime.strptime(check_log_dict[log_file][file_key]['dr_file']['end'], '%H:%M:%S')
                    diff = (end_dt - start_dt)
                    check_log_dict[log_file][file_key]['dr_file']['diff'] = diff.seconds
                    check_log_dict[log_file]['dr_master']['sum_sec'] += diff.seconds
                    check_log_dict[log_file]['dr_master']['count'] += 1
                    total_times_dict[check_log_dict[log_file]['host']['hostname']]['info']['count'] += 8
  
            if 'Running png' in line:
                check_log_dict[log_file][file_key]['png_file']['start'] = list_line[-5]
   
            if 'Done running png' in line:
                if check_log_dict[log_file][file_key]['png_file']['start'] != '':
                    check_log_dict[log_file][file_key]['png_file']['end'] = list_line[-6]
                    start_dt = dt.datetime.strptime(check_log_dict[log_file][file_key]['png_file']['start'], '%H:%M:%S')
                    end_dt = dt.datetime.strptime(check_log_dict[log_file][file_key]['png_file']['end'], '%H:%M:%S')
                    diff = (end_dt - start_dt)
                    check_log_dict[log_file][file_key]['png_file']['diff'] = diff.seconds
                    check_log_dict[log_file]['png_master']['sum_sec'] += diff.seconds
                    check_log_dict[log_file]['png_master']['count'] += 1
                    total_times_dict[check_log_dict[log_file]['host']['hostname']]['info']['count'] += 28


    for key in check_log_dict[log_file].keys():
        if key in ['cr_master', 'dr_master', 'png_master'] and 'count' in check_log_dict[log_file][key].keys():
            if check_log_dict[log_file][key]['count'] != 0:
                check_log_dict[log_file][key]['avg'] = check_log_dict[log_file][key]['sum_sec'] / check_log_dict[log_file][key]['count']
                total_times_dict[check_log_dict[log_file]['host']['hostname']][key.split('_')[0]]['avg'].append(check_log_dict[log_file][key]['avg'])

    for key in check_log_dict[log_file].keys():
        if key not in ['host', 'cr_master', 'dr_master', 'png_master']:
            for file_key in check_log_dict[log_file][key].keys():
                if file_key == 'cr_file':
                    check_log_dict[log_file]['cr_master']['sum_var'] += (check_log_dict[log_file][key][file_key]['diff'] - check_log_dict[log_file]['cr_master']['avg'])**2
                elif file_key == 'dr_file':
                    check_log_dict[log_file]['dr_master']['sum_var'] += (check_log_dict[log_file][key][file_key]['diff'] - check_log_dict[log_file]['dr_master']['avg'])**2
                else:
                    check_log_dict[log_file]['png_master']['sum_var'] += (check_log_dict[log_file][key][file_key]['diff'] - check_log_dict[log_file]['png_master']['avg'])**2

    for key in check_log_dict[log_file].keys():
        if key != 'host' and 'count' in check_log_dict[log_file][key].keys():
            if check_log_dict[log_file][key]['count'] != 0:
                check_log_dict[log_file][key]['var'] = check_log_dict[log_file][key]['sum_var'] / check_log_dict[log_file][key]['count']
                check_log_dict[log_file][key]['std'] = (check_log_dict[log_file][key]['var'])**0.5
                total_times_dict[check_log_dict[log_file]['host']['hostname']][key.split('_')[0]]['std'].append(check_log_dict[log_file][key]['std'])

for key in total_times_dict.keys():
    print 'Host: {}'.format(key)
    for type_key in total_times_dict[key].keys():
        avg = 0
        std = 0
        if type_key != 'info':
            if len(total_times_dict[key][type_key]['avg']) != 0:
                avg = sum(total_times_dict[key][type_key]['avg']) / float(len(total_times_dict[key][type_key]['avg']))
            if len(total_times_dict[key][type_key]['std']) != 0:
                std = sum(total_times_dict[key][type_key]['std']) / float(len(total_times_dict[key][type_key]['std']))
            print '{0}:\nAVG: {1:.2f}\nSTD: {2:.2f}'.format(type_key, avg, std)
    print 'CPU: {}\nMemory: {}\nFile Count: {}\n'.format(total_times_dict[key]['info']['cpu'], total_times_dict[key]['info']['memory'], total_times_dict[key]['info']['count'])