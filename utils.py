import sqlite3, os
from datetime import datetime

class database:
    def __init__(self, dbInfo, queries):
        self.location = os.path.join(os.path.dirname(__file__), dbInfo["location"])
        print("DB location: ",self.location)
        self.folderTable = dbInfo["foldertable"]
        self.connection = self.initConnection()
        self.queries = queries

    def initConnection(self):
        return sqlite3.connect(self.location)

    def closeConnection(self):
        return self.connection.close()
    
    def createDb(self):
        c = self.connection.cursor()
        c.execute(self.queries["sqlcreatetable"].format(self.folderTable))
        self.connection.commit()
        self.closeConnection()
        print("DB table folderinfo created!")

    def getFolderList(self):
        '''
        Get list of folders from db that need uploading
        '''
        c = self.connection.cursor()
        c.execute(queries.sql_get_folders_to_upload.format(self.folderTable, "UPLOADED"))
        result = c.fetchall()
        self.closeConnection()
        if result:
            return result
        else:
            logging.info("No new files to upload")
            return None

    def addToFolderList(self, folderName):
        '''
        Add folder to table
        '''
        c = self.connection.cursor()
        c.execute(self.queries["checkfolderpresence"].format(self.folderTable, folderName))
        if c.fetchone() is None:
            print("Inserting Folder {}".format(folderName))
            runDate, seqId, runNum, flowCellId = folderName.split("_")
            currenttime = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            c.execute(self.queries["insertfolder"].format(self.folderTable, folderName, runDate, seqId, runNum, flowCellId, "CREATED", currenttime))
            self.connection.commit()
            self.closeConnection()
        else:
            print("Folder Already Present {}".format(folder))

    def destroyDb(self):
        '''
        Destroy database file
        '''
        pass

        