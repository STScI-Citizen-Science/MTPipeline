'''
Logger setup for MTPipeline
'''
import logging

logger = logging.getLogger('mtpipeline')
logger.setLevel(logging.DEBUG)
logFile = logging.FileHandler('mtpipeline.log')
logFile.setLevel(logging.DEBUG)
logFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logFile.setFormatter(logFormat)
logger.addHandler(logFile)
