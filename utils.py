import os, logging, sys, pytz, time
from logging.handlers import RotatingFileHandler
from urllib.request import urlopen
from datetime import datetime
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class Formatter(logging.Formatter):
     """override logging.Formatter to use an aware datetime object"""
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
    '''
    Setup up logger to output stdout/stderr to terminal and logfile (path from config)
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = Formatter("%(asctime)s [%(levelname)s] %(message)s")

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
    '''
    Format output result correctly
    '''
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.info(result.stderr)
    if result.return_code:
        logger.info(result.return_code)

def regenIgnoreList(inputDir):
    ignoreList = []
    ignoreFileLoc = inputDir+"ignore.txt"
    if "ignore.txt" in os.listdir(inputDir):
        with open(ignoreFileLoc) as fileio:
            ignoreList = fileio.read().splitlines()
    else:
        open(ignoreFileLoc, "a").close()
    #TODO make more efficient
    ignoreList = list(filter(None, ignoreList)) #remove emplty lines
    ignoreList = list(set(ignoreList)) #remove duplicate lines
    return ignoreList

def addToList(inputDir, folderName, listType):
    fileLoc = inputDir+listType
    with open(fileLoc, "a") as fileio:
        fileio.write("\n"+folderName)

def convDirToRsyncFormat(inputDir):
    #TODO Use os.path magic here
    return inputDir.replace("c:/","/cygdrive/c/")

def sendEmailUsingPlover(emailUrl, args):
    time.sleep(5) #Add time delay before sending out email
    emailUrl = emailUrl.format_map(args)
    emailUrl = emailUrl.replace("|","%7C").replace(" ","%20")
    response = urlopen(emailUrl)

def getCorrectTimezone(utc_now):
    pst_timezone = pytz.timezone("America/Vancouver")
    pst_now = utc_now.astimezone(pst_timezone)
    return pst_now

def getDateTimeNow():
    utc_now = pytz.utc.localize(datetime.utcnow())
    pst_now = getCorrectTimezone(utc_now)
    return pst_now.strftime("%Y-%m-%d %H:%M:%S")
    
def getDateTimeNowIso():
    utc_now = pytz.utc.localize(datetime.utcnow())
    pst_now = getCorrectTimezone(utc_now)
    return pst_now.isoformat()