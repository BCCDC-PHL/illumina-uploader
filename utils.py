import sqlite3, os, re, logging, sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from shutil import copyfile

def setupLogger(logFile, maxBytes=5000, backupCount=5):
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
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.info(result.stderr)
    if result.return_code:
        logger.info(result.return_code)

class Database:
    def __init__(self, dbInfo, queries, logger):
        self.location = os.path.join(os.path.dirname(__file__), dbInfo["location"])
        self.backups = os.path.join(os.path.dirname(__file__), dbInfo["backupfolder"])
        self.folderTable = dbInfo["foldertable"]
        self.connection = self.initConnection()
        self.queries = queries
        self.logger = logger

    def initConnection(self):
        return sqlite3.connect(self.location)

    def closeConnection(self):
        return self.connection.close()
    
    def createDb(self):
        c = self.connection.cursor()
        c.execute(self.queries["createtable"].format(self.folderTable))
        self.connection.commit()
        self.closeConnection()
        self.logger.info("Database initialised!")
        exit(0)

    def getFolderList(self):
        '''
        Get list of folders from db that need uploading
        '''
        c = self.connection.cursor()
        c.execute(self.queries["getfolderstoupload"].format(self.folderTable, "UPLOADED"))
        result = c.fetchall()
        if result:
            return result
        else:
            self.logger.info("No new folders to upload")
            exit(0)

    def prepFolders(self, inputdir, folderRegex, folderName):
        '''
        Check and add folders to db
        '''
        try:
            if folderName:
                if self._checkFolder(inputdir, folderRegex, folderName):
                    self._insertFolders(folderName)
                else:
                    self.logger.error("Please check folder name {} and/or location {}".format(folderName, inputdir))
                    exit(1)
            else:
                for subFolderName in self._checkFolders(inputdir, folderRegex):
                    self._insertFolders(subFolderName)
        except (sqlite3.OperationalError, OSError) as error:
            self.logger.error("Fatal error: {0}".format(error))
            exit(1)

    def _insertFolders(self, folderName):
        '''
        Internal function
        '''
        c = self.connection.cursor()
        c.execute(self.queries["checkfolderpresence"].format(self.folderTable, folderName))
        if c.fetchone() is None:
            self.logger.info("Inserting Folder {}".format(folderName))
            currenttime = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            c.execute(self.queries["insertfolder"].format(self.folderTable, folderName, "CREATED", currenttime))
            self.connection.commit()
        else:
            self.logger.info("Folder Already Present {}".format(folderName))

    def _checkFolder(self, inputdir, folderRegex, folderName):
        '''
        Internal function
        '''
        for folder in os.listdir(inputdir):
            if re.match(folderRegex, folder) and folderName==folder:
                return True
        return False

    def _checkFolders(self, inputdir, folderRegex):
        '''
        Internal function
        '''
        for folder in os.listdir(inputdir):
            if re.match(folderRegex, folder):
                yield folder

    def watchDirectory(self, inputdir, folderRegex, watchFile, sleeptime):
        '''
        Check and add folders to db
        '''
        for folder in os.listdir(inputdir):
            if re.match(folderRegex, folder):
                for subFolder in os.listdir(inputdir+folder):
                    if subFolder == watchFile:
                        #Add to prepfolders
                        return True
        #Goto sleep for 5 mins
        return False

    def backupDb(self):
        '''
        Backup database file
        '''
        backupDbFile = self.backups + "/backup_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".db"
        copyfile(self.location, backupDbFile)
        self.logger.info("Database backup completed!")
        exit(0)
