'''
iterate run_cosmics.py with different parameters 
'''

import subprocess


for iters in range(0,10):
	readnoise = 2.5
	while readnoise <= 7.5:
		subprocess.call(['python', 'run_cosmics.py', '--files', 
						'../../temp/fits/u2mi0102t_c0m.fits',
						'-i', str(iters), '-sigmaclip', '3.0', '-readnoise', str(readnoise)]);
		readnoise = readnoise + 1;
	sigmaclip = 0.5
	while sigmaclip <= 6.0:
		subprocess.call(['python', 'run_cosmics.py', '--files', 
					'../../temp/fits/u2mi0102t_c0m.fits',
					'-i', str(iters), '-sigmaclip', str(sigmaclip), '-readnoise', '5.0']);
		sigmaclip = sigmaclip+1
