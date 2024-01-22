import logging
import os
import re
import sqlite3
import sys

from datetime import datetime
from shutil import copyfile

from .utils import regenIgnoreList, collectIgnoreList, Run


class Database:
    '''
    Database class that handles all sqlite operations
    '''
    def __init__(self, dbInfo, queries, logger, inputDirs, folderRegex):
        """
        Initialise database object.

        :param dbInfo: Dictionary containing database location and backup folder
        :type dbInfo: dict
        :param queries: Dictionary containing sqlite queries
        :type queries: dict
        :param logger: Logger object
        :type logger: logging.Logger
        :param inputDirs: List of input directories to scan for folders
        :type inputDirs: list
        :param folderRegex: Regex to match folders in input directories
        :type folderRegex: str
        :return: Database object
        :rtype: Database
        """
        self.logger = logger
        self.location = os.path.abspath(dbInfo["location"])
        self.backups = os.path.abspath(dbInfo["backupfolder"])
        self.folderTable = dbInfo["foldertable"]
        self.inputDirs = inputDirs
        self.queries = queries
        self.folderRegex = folderRegex
        self.checkInputs()
        self.connection = self.initConnection()


    def checkInputs(self):
        """
        Check if all input directories and database location exists.

        :raises SystemExit: If any input directory or database location does not exist
        """
        for d in [os.path.dirname(self.location), self.backups] + self.inputDirs:
            if not os.path.exists(d) or not os.path.isdir(d):
                self.logger.error("Directory does not exist: " + d + " Check config.ini file.")
                self.inputDirs.remove(d)

    def initConnection(self):
        """
        Initialise sqlite connection

        :return: sqlite connection object
        :rtype: sqlite3.Connection
        """
        return sqlite3.connect(self.location)

    def closeConnection(self):
        """
        Close sqlite connection

        :return: None
        :rtype: None
        """
        return self.connection.close()
    
    def createDb(self):
        """
        Create new sqlite instance

        :return: None
        :rtype: None
        """
        c = self.connection.cursor()
        c.execute(self.queries["createtable"].format(self.folderTable))
        self.connection.commit()
        self.closeConnection()
        self.logger.info("Database initialised!")

    def backupDb(self):
        """
        Backup database file (specified in config)

        :return: None
        :rtype: None
        """
        backupDbFile = F"{self.backups}/backup_{datetime.now():%Y_%m_%d_%H_%M_%S}.db"
        copyfile(self.location, backupDbFile)
        self.logger.info("Database backup completed!")
    
    def getFolderList(self):
        """
        Get list of folders from db that need uploading

        :return: List of folders to upload
        :rtype: list[str]
        """
        c = self.connection.cursor()
        c.execute(self.queries["getfolderstoupload"].format("folder" ,self.folderTable, "FINISHED"))
        result = c.fetchall()
        if result:
            return result
        else:
            self.logger.info("No new folders to upload")
            return []

    def prepFolders(self, folderName):
        """
        Check and add folders to db

        :param folderName: Name of folder to check
        :type folderName: str
        :return: None
        :rtype: None
        """
        try:
            if folderName and self._checkFolder(folderName):
                self._insertFolders(folderName)
        except (sqlite3.OperationalError, OSError) as error:
            self.logger.error("Fatal error: {0}".format(error))
            exit(1)

    def getAllFolders(self):
        """
        Get list of all folders in db

        :return: List of all folders in db
        :rtype: list[str]
        """
        c = self.connection.cursor()
        c.execute(self.queries["selectallfolders"].format(self.folderTable))
        result = c.fetchall()
        if result:
            return result
        else:
            self.logger.info("No folders in database")
            return []

    def printDb(self):
        """
        Print all folders in db

        :return: None
        :rtype: None
        """
        folders = self.getAllFolders()
        for folder in folders:
            print(','.join(folder))

    def createIgnoreFile(self):
        """
        Create ignore file for folders that should not be added to db

        :return: None
        :rtype: None
        """
        for d in self.inputDirs:
            collectIgnoreList(d, self.folderRegex, self.logger)

    def _insertFolders(self, folderName):
        """
        Internal function for inserting folder data into db

        :param folderName: Name of folder to insert
        :type folderName: str
        :return: None
        :rtype: None
        """
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
        """
        Function to check if folder in ignore file or exists in any directories

        :param folderName: Name of folder to check
        :type folderName: str
        :return: False if folder in ignore file or does not exist in any directories, else return directory path
        :rtype: bool or str
        """
        for inputDir in self.inputDirs:
            if folderName in regenIgnoreList(inputDir):
                self.logger.info("{0} in ignore list, will not be added to db or FINISHED".format(folderName))
                return False
            for folder in os.listdir(inputDir):
                if re.match(self.folderRegex, folder) and folderName==folder:
                    return inputDir
        self.logger.error("Please check folder name {} and/or its location".format(folderName))
        return False

    def watchDirectories(self, watchFile, inOutMap, dryRun=False):
        """
        Iterate through input directories and check if any folders match watch file from config.
        If found, add to list to be uploaded. If dry run, do not add to db.
        If directory does not exist, log error, skip that input dir and continue.

        :param watchFile: Name of watch file to check
        :type watchFile: str
        :param inOutMap: Dictionary mapping input directories to output directories
        :type inOutMap: dict
        :param dryRun: Flag to indicate dry run
        :type dryRun: bool
        :return: List of runs to upload
        :rtype: list[Run]
        """
        runs = []
        for inputDir in self.inputDirs:
            if not os.path.exists(inputDir):
                self.logger.error("Directory does not exist: " + inputDir)
                continue
            for folder in os.listdir(inputDir):
                #Check if regex matches directory name
                if re.match(self.folderRegex, folder):
                    #Enumerate subfolders in directory
                    for subFolder in os.listdir(inputDir+folder):
                        #Check if any subfolders matches watchfile from config
                        if subFolder == watchFile:
                            #Add to list to be uploaded
                            newRun = Run(folder, inputDir, inOutMap[inputDir])
                            runs.append(newRun)
                            if not dryRun:
                                self.logger.info("Adding {0} to DB".format(folder))
                                self.prepFolders(folder)
        return runs

    def markFileInDb(self, folderName, markAs):
        """
        Mark folder as FINISHED or FAILED in db

        :param folderName: Name of folder to mark
        :type folderName: str
        :param markAs: Status to mark folder as
        :type markAs: str
        :return: None
        :rtype: None
        """
        c = self.connection.cursor()
        c.execute(self.queries["markfileindb"].format(self.folderTable, markAs, folderName))
        self.connection.commit()
        self.logger.info("Folder {0} marked in DB as {1}".format(folderName, markAs))
