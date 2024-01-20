import os, logging, re, sys, pytz, time
from logging.handlers import RotatingFileHandler
from urllib.request import urlopen
from urllib.error import URLError
from datetime import datetime
from dataclasses import dataclass, asdict
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

@dataclass
class Run:
    """
    Run class that handles all run info based operations
    A run is defined as illumina directory that needs to be transferred
    """
    name: str
    inputDir: str
    outputDir: str

class Formatter(logging.Formatter):
    """
    Override logging.Formatter to use an aware datetime object
    
    :param logging.Formatter: logging.Formatter object
    :type logging.Formatter: logging.Formatter
    :return: Formatter object
    :rtype: Formatter
    """
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        tzinfo = pytz.timezone('America/Vancouver')
        pst_now = dt.astimezone(tzinfo)
        return pst_now

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s

def setupLogger(logFile, maxBytes=5000, backupCount=5):
    """
    Setup up logger to output stdout/stderr to terminal and logfile (path from config)

    :param logFile: Path to logfile
    :type logFile: str
    :param maxBytes: Max size of logfile before rotating, defaults to 5000
    :type maxBytes: int, optional
    :param backupCount: Number of logfiles to keep, defaults to 5
    :type backupCount: int, optional
    :return: Logger object
    :rtype: logging.Logger
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = Formatter("%(asctime)s [%(levelname)s] module: %(module)s, function: %(funcName)s, line: %(lineno)d, message: %(message)s")

    #Set STDOUT
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    #Set Log file
    fh = RotatingFileHandler(logFile, maxBytes, backupCount)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def formatStdout(result, logger):
    """
    Format output result correctly

    :param result: Output from subprocess
    :type result: subprocess.CompletedProcess
    :param logger: Logger object
    :type logger: logging.Logger
    :return: None
    :rtype: None
    """
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.info(result.stderr)
    if result.return_code:
        logger.info(result.return_code)

def regenIgnoreList(inputDir):
    """
    Refresh/regenerate ignore.txt file

    :param inputDir: Path to input directory
    :type inputDir: str
    :return: List of folders to ignore
    :rtype: list
    """
    ignoreList = []
    ignoreFileLoc = os.path.join(inputDir, "ignore.txt")
    if "ignore.txt" in os.listdir(inputDir):
        with open(ignoreFileLoc) as fileio:
            ignoreList = fileio.read().splitlines()
    else:
        open(ignoreFileLoc, "a").close()
    ignoreList = list(filter(None, ignoreList)) #remove empty lines
    ignoreList = list(set(ignoreList))          #remove duplicate lines
    return ignoreList

def collectIgnoreList(inputDir, folder_regex, logger):
    """
    Collect current folders into ignore.txt
    useful when setting up on new sequencer

    :param inputDir: Path to input directory
    :type inputDir: str
    :param folder_regex: Regex to match folders in input directories
    :type folder_regex: str
    :param logger: Logger object
    :type logger: logging.Logger
    :return: None
    :rtype: None
    """
    existing_run_directories = []
    for f in os.listdir(inputDir):
        if os.path.isdir(os.path.join(inputDir, f)) and re.match(folder_regex, f):
            existing_run_directories.append(f)

    ignorefile_path = os.path.join(inputDir, "ignore.txt")
    if not os.path.isfile(ignorefile_path):
        with open(ignorefile_path, 'w') as f:
            for d in existing_run_directories:
                f.write(d + '\n')
    else:
        logger.info('File: ' + ignorefile_path + ' exists. New ignore.txt file not created.')
                


def addToList(inputDir, folderName, listType):
    """
    Add folder name to ignore list

    :param inputDir: Path to input directory
    :type inputDir: str
    :param folderName: Name of folder to add to ignore list
    :type folderName: str
    :param listType: Type of list to add folder to
    :type listType: str
    :return: None
    :rtype: None
    """
    fileLoc = inputDir+listType
    with open(fileLoc, "a") as fileio:
        fileio.write("\n"+folderName)

def convDirToRsyncFormat(inputDir):
    """
    Only for windows machines. Converts path starting with c:/ to /cygdrive/c/, for use with Cygwin rsync.

    :param inputDir: Path to input directory
    :type inputDir: str
    :return: Path to input directory in rsync format
    :rtype: str
    """
    return inputDir.replace("c:/","/cygdrive/c/")

def sendEmailUsingPlover(emailUrl, args, logger):
    """
    Format and add 3 sec delay before sending out email

    :param emailUrl: URL to send email
    :type emailUrl: str
    :param args: Arguments from command line
    :type args: dict
    :param logger: Logger object
    :type logger: logging.Logger
    :return: None
    :rtype: None
    """
    if not args['debug']:
        time.sleep(3)
        emailUrl = emailUrl.format_map(args)
        emailUrl = emailUrl.replace("|","%7C").replace(" ","%20")
        try:
            response = urlopen(emailUrl)
        except URLError as e:
            logger.error('Email notification failed using url: ' + emailUrl)

def getCorrectTimezone(utc_now):
    """
    Fix timezone

    :param utc_now: UTC datetime object
    :type utc_now: datetime.datetime
    :return: PST datetime object
    :rtype: datetime.datetime
    """
    pst_timezone = pytz.timezone("America/Vancouver")
    pst_now = utc_now.astimezone(pst_timezone)
    return pst_now

def getDateTimeNow():
    """
    Get current datetime in PST

    :return: Current datetime in PST
    :rtype: str
    """
    utc_now = pytz.utc.localize(datetime.utcnow())
    pst_now = getCorrectTimezone(utc_now)
    return pst_now.strftime("%Y-%m-%d %H:%M:%S")
    
def getDateTimeNowIso():
    """
    Get current datetime in PST

    :return: Current datetime in PST
    :rtype: str
    """
    utc_now = pytz.utc.localize(datetime.utcnow())
    pst_now = getCorrectTimezone(utc_now)
    return pst_now.isoformat()
