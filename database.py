import sqlite3, os, re, logging, sys
from utils import regenIgnoreList
from datetime import datetime
from shutil import copyfile

class Database:
    '''
    Database class that handles all sqlite operations
    TODO replace with DjangoORM in future
    '''
    def __init__(self, dbInfo, queries, logger, inputDirs, folderRegex):
        self.location = os.path.join(os.path.dirname(__file__), dbInfo["location"])
        self.backups = os.path.join(os.path.dirname(__file__), dbInfo["backupfolder"])
        self.folderTable = dbInfo["foldertable"]
        self.connection = self.initConnection()
        self.queries = queries
        self.logger = logger
        self.inputDirs = inputDirs
        self.folderRegex = folderRegex

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
        backupDbFile = F"{self.backups}/backup_{datetime.now():%Y_%m_%d_%H_%M_%S}.db"
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

    def prepFolders(self, folderName):
        '''
        Check and add folders to db
        '''
        try:
            if folderName and self._checkFolder(folderName):
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
            currenttime = F"{datetime.now():%Y-%m-%d %H:%M:%S}"
            c.execute(self.queries["insertfolder"].format(self.folderTable, folderName, "CREATED", currenttime))
            self.connection.commit()
        else:
            self.logger.info("Folder Already Present {}".format(folderName))

    def _checkFolder(self, folderName):
        '''
        Function to check if folder in ignore file or exists in any directories
        '''
        for inputDir in self.inputDirs:
            if folderName in regenIgnoreList(inputDir):
                self.logger.info("{0} in ignore list, will not be added to db or uploaded".format(folderName))
                return False
            for folder in os.listdir(inputDir):
                if re.match(self.folderRegex, folder) and folderName==folder:
                    return inputDir
        self.logger.error("Please check folder name {} and/or its location".format(folderName))
        return False

    def findFolder(self, folderName):
        '''
        Function to check if folder in ignore file or exists in any directories
        '''
        for inputDir in self.inputDirs:
            for folder in os.listdir(inputDir):
                if re.match(self.folderRegex, folder) and folderName==folder:
                    return inputDir
        self.logger.error("Error finding {} in all input locations".format(folderName))
        raise Exception("Error finding {} in all input locations".format(folderName))

    def watchDirectories(self, watchFile):
        '''
        Check for watch file and prep folder if matched
        '''
        for inputDir in self.inputDirs:
            for folder in os.listdir(inputDir):
                if re.match(self.folderRegex, folder): #Check if regex matches directory name
                    for subFolder in os.listdir(inputDir+folder): #Enumerate subfolders in directory
                        if subFolder == watchFile: #Check if any subfolders matches watchfile from config
                            self.logger.info("Adding {0} to DB".format(folder))
                            self.prepFolders(folder)

    def markFileInDb(self, folderName, markAs):
        '''
        Mark folder as UPLOADED or FAILED in db
        '''
        c = self.connection.cursor()
        c.execute(self.queries["markfileindb"].format(self.folderTable, markAs, folderName))
        self.connection.commit()
        self.logger.info("Folder {0} marked in DB as {1}".format(folderName, markAs))
