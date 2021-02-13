import os, logging, sys
from logging.handlers import RotatingFileHandler

def setupLogger(logFile, maxBytes=5000, backupCount=5):
    '''
    Setup up logger to output stdout/stderr to terminal and logfile (path from config)
    '''
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

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

def genUpdateList(outputDir):
    pass

def putCompletedFile(inputDir):
    pass

def generateJson(inputDir):
    pass

def addToList(inputDir, folderName, listType):
    fileLoc = inputDir+listType
    with open(fileLoc, "a") as fileio:
        fileio.write("\n"+folderName)
