# iterate run_cosmics.py with different parameters 

import subprocess

#python run_cosmics.py --files ../../temp/fits/u2mi0102t_c0m.fits -i 1 -sc 3.0 -rn 5.0

for iters in range(0,10):
	rn=2.5
	while rn <= 7.5:
		subprocess.call(['python', 'run_cosmics.py', '--files', 
						'../../temp/fits/u2mi0102t_c0m.fits',
						'-i', str(iters), '-sc', '3.0', '-rn', str(rn)]);
		rn=rn+1;
	sc=0.5
	while sc <= 6.0:
		subprocess.call(['python', 'run_cosmics.py', '--files', 
					'../../temp/fits/u2mi0102t_c0m.fits',
					'-i', str(iters), '-sc', str(sc), '-rn', '5.0']);
		sc=sc+1
