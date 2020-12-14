import sqlite3, os, re
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
        c.execute(self.queries["createtable"].format(self.folderTable))
        self.connection.commit()
        self.closeConnection()
        print("DB table folderinfo created!")
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
            print("No new folders to upload")
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
                    print("Please check folder name {} and/or location {}".format(folderName, inputdir))
                    exit(1)
            else:
                for subFolderName in self._checkFolders(inputdir, folderRegex):
                    self._insertFolders(subFolderName)
        except (sqlite3.OperationalError, OSError) as error:
            print("Fatal error: {0}".format(error))
            exit(1)

    def _insertFolders(self, folderName):
        c = self.connection.cursor()
        c.execute(self.queries["checkfolderpresence"].format(self.folderTable, folderName))
        if c.fetchone() is None:
            print("Inserting Folder {}".format(folderName))
            currenttime = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            c.execute(self.queries["insertfolder"].format(self.folderTable, folderName, "CREATED", currenttime))
            self.connection.commit()
        else:
            print("Folder Already Present {}".format(folderName))

    def _checkFolder(self, inputdir, folderRegex, folderName):
        for folder in os.listdir(inputdir):
            if re.match(folderRegex, folder) and folderName==folder:
                return True
        return False

    def _checkFolders(self, inputdir, folderRegex):
        for folder in os.listdir(inputdir):
            if re.match(folderRegex, folder):
                yield folder

    def watchDirectory(self):
        pass

    def backupDb(self):
        '''
        Backup database file
        '''
        pass


if __name__ == "__main__":
    pass