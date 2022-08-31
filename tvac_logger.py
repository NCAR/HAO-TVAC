import logging
from pathlib import Path
import datetime
import time
import sys

try:
    ExecFileURL = Path(__main__.__file__)
except:
    ExecFileURL = Path(".")

LogFileURL = (ExecFileURL.parent / 'logs' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')).with_suffix('.log')

try:
    LogFileURL.parent.mkdir(parents=True)
except:
    pass
logger = logging.getLogger(ExecFileURL.stem)
logger.setLevel(logging.DEBUG)
FileLogger = logging.FileHandler(LogFileURL)
CommandLineLogger = logging.StreamHandler()
FileLogger.setLevel(logging.DEBUG)
CommandLineLogger.setLevel(logging.INFO)
format = logging.Formatter('%(asctime)19s %(levelname)7s - %(message)s', '%Y-%m-%d %H:%M:%S')
FileLogger.setFormatter(format)
CommandLineLogger.setFormatter(format)
logger.addHandler(CommandLineLogger)
logger.addHandler(FileLogger)
