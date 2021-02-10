import sqlite3, os, re, logging, sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from shutil import copyfile

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
    ignoreList = list(filter(None, ignoreList)) #remove emplty lines
    ignoreList = list(set(ignoreList)) #remove duplicate lines
    return ignoreList

def addToList(inputDir, folderName, listType):
    ignoreFileLoc = inputDir+listType
    with open(ignoreFileLoc, "a") as fileio:
        fileio.write("\n"+folderName)

class Database:
    '''
    Database class that handles all sqlite operations
    TODO replace with DjangoORM in future
    '''
    def __init__(self, dbInfo, queries, logger, inputDir):
        self.location = os.path.join(os.path.dirname(__file__), dbInfo["location"])
        self.backups = os.path.join(os.path.dirname(__file__), dbInfo["backupfolder"])
        self.folderTable = dbInfo["foldertable"]
        self.connection = self.initConnection()
        self.queries = queries
        self.logger = logger
        self.inputDir = inputDir

    def initConnection(self):
        return sqlite3.connect(self.location)

    def closeConnection(self):
        return self.connection.close()
    
    def createDb(self):
        '''
        Create new sqlite instance
        '''
        c = self.connection.cursor()
        c.execute(self.queries["createtable"].format(self.folderTable))
        self.connection.commit()
        self.closeConnection()
        self.logger.info("Database initialised!")

    def backupDb(self):
        '''
        Backup database file (specified in config)
        '''
        backupDbFile = self.backups + "/backup_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".db"
        copyfile(self.location, backupDbFile)
        self.logger.info("Database backup completed!")
    
    def getFolderList(self):
        '''
        Get list of folders from db that need uploading
        '''
        c = self.connection.cursor()
        c.execute(self.queries["getfolderstoupload"].format("folder" ,self.folderTable, "UPLOADED"))
        result = c.fetchall()
        if result:
            return result
        else:
            self.logger.info("No new folders to upload")
            return []

    def prepFolders(self, folderRegex, folderName):
        '''
        Check and add folders to db
        '''
        try:
            if folderName and self._checkFolder(folderRegex, folderName):
                self._insertFolders(folderName)
        except (sqlite3.OperationalError, OSError) as error:
            self.logger.error("Fatal error: {0}".format(error))
            exit(1)

    def _insertFolders(self, folderName):
        '''
        Internal function for inserting folder data into db
        '''
        c = self.connection.cursor()
        c.execute(self.queries["checkfolderpresence"].format(self.folderTable, folderName))
        if c.fetchone() is None:
            self.logger.info("Inserting Folder {}".format(folderName))
            currenttime = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") #TODO make this pythonic
            c.execute(self.queries["insertfolder"].format(self.folderTable, folderName, "CREATED", currenttime))
            self.connection.commit()
        else:
            self.logger.info("Folder Already Present {}".format(folderName))

    def _checkFolder(self, folderRegex, folderName):
        '''
        Internal function for checking if folder in ignore file or exists in directory 
        '''
        if folderName in regenIgnoreList(self.inputDir):
            self.logger.info("{0} in ignore list, will not be added to db or uploaded".format(folderName))
            return False
        for folder in os.listdir(self.inputDir):
            if re.match(folderRegex, folder) and folderName==folder:
                return True
        self.logger.error("Please check folder name {} and/or location {}".format(folderName, self.inputDir))
        return False

    def watchDirectory(self, folderRegex, watchFile):
        '''
        Check for watch file and prep folder if matched
        '''
        for folder in os.listdir(self.inputDir):
            if re.match(folderRegex, folder): #Check if regex matches directory name
                for subFolder in os.listdir(self.inputDir+folder): #Enumerate subfolders in directory
                    if subFolder == watchFile: #Check if any subfolders matches watchfile from config
                        self.logger.info("Adding {0} to DB".format(folder))
                        self.prepFolders(folderRegex, folder)

    def markAsUploaded(self, folderName):
        '''
        Mark folder as UPLOADED in db
        '''
        c = self.connection.cursor()
        c.execute(self.queries["markasuploaded"].format(self.folderTable, "UPLOADED", folderName))
        self.connection.commit()
        self.logger.info("Folder {0} marked in DB as UPLOADED".format(folderName))
