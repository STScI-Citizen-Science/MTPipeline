"""Script for executing the imaging_pipeline.

This module is used to execute the mtpipeline.imaging_pipeline code. 
It contains the logic for parsing the command line arguments, logging 
the execution, an email decorator to send out a end of script message, 
and a try/execpt loop to catch exceptions. 

Authors:
    Alex Viana, April 2014
"""

from mtpipeline.imaging_pipeline import imaging_pipeline


def parse_args():
    """Parse the input arguments using `argparse` module.

    Parameters: 
        nothing

    Returns: 
        args : an instance of the class returned by 
        `parser.parse_args` with the arguments as instance attributes.

    Outputs:
        nothing
    """
    parser = argparse.ArgumentParser(
        description = 'Run the moving target pipeline.' )
    parser.add_argument(
        '-filelist',
        required = True,
        help = 'Search string for files. Wildcards accepted.')
    parser.add_argument(
        '-output_path',
        required = False,
        help = 'Set the path for the output. Default is the input directory.')
    parser.add_argument(
        '-no_cr_reject',
        required = False,
        action='store_false',
        default = True,
        dest = 'cr_reject',
        help = 'Toggle off the cosmic ray rejection step.')
    parser.add_argument(    
        '-no_astrodrizzle',
        required = False,
        action='store_false',        
        default = True,
        dest = 'astrodrizzle',
        help = 'Toggle off the astrodrizzle step.')
    parser.add_argument(
        '-no_png',
        required = False,
        action = 'store_false',        
        default = True,
        dest = 'png',
        help = 'Toggle off the png step.')
    parser.add_argument(
        '-reproc',
        required = False,
        action = 'store_true',
        default = False,
        dest = 'reproc',
        help = 'Reprocess all files, even if outputs already exist.')
    args = parser.parse_args()
    return args


@email_decorator
def run_imaging_pipeline():
    """The script for executing the imaging_pipeline function.

    This function is the wrapper for the `imaging_pipeline` function 
    in `mtpipeline`. It adds logging information and parses the 
    command line arguments returned by `parse_args`. Completion emails 
    are added by the `email_decorator` function. 

    Parameters: 
        nothing

    Returns: 
        nothing

    Outputs:
        The outputs of this are the same as the wrapped 
        `imaging_pipeline`.
    """
    args = parse_args()
    logger = logging.getLogger('mtpipeline')
    logger.setLevel(logging.DEBUG)
    log_file = logging.FileHandler(
        os.path.join(
            LOGFOLDER, 'mtpipeline', 
            'mtpipeline-' + datetime.now().strftime('%Y-%m-%d') + '.log'))
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger.addHandler(log_file)
    logger.info('User: {0}'.format(getuser()))
    logger.info('Host: {0}'.format(gethostname())) 
    logger.info('Machine: {0}'.format(machine()))
    logger.info('Platform: {0}'.format(platform()))
    logger.info("Command-line arguments used:")
    for arg in args.__dict__:
        logger.info(arg + ": " + str(args.__dict__[arg]))
    rootfile_list = glob.glob(args.filelist)
    rootfile_list = [x for x in rootfile_list if len(os.path.basename(x)) == 18]
    assert rootfile_list != [], 'empty rootfile_list in mtpipeline.py.'
    for filename in rootfile_list:
        logger.info("Current File: " + filename)
        try:
            imaging_pipeline(filename, 
                output_path =  args.output_path,
                cr_reject_switch = args.cr_reject,
                astrodrizzle_switch = args.astrodrizzle, 
                png_switch = args.png,
                reproc_switch = args.reproc)
            logger.info("Completed: " + filename)
        except Exception as err:
            logger.critical('{0} {1} {2}'.format(
                type(err), err.message, sys.exc_traceback.tb_lineno))
    logger.info("Script completed")


if __name__ == '__main__':
    run_imaging_pipeline()