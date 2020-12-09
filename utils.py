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
        exit()

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
            print("No new files to upload")
            exit(0)

    def addToFolderList(self, inputdir, folderRegex, folderName=False):
        '''
        Add folder to table
        '''
        if self._folderCheck(folderName, folderRegex, inputdir):
            c = self.connection.cursor()
            c.execute(self.queries["checkfolderpresence"].format(self.folderTable, folderName))
            if c.fetchone() is None:
                print("Inserting Folder {}".format(folderName))
                currenttime = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
                c.execute(self.queries["insertfolder"].format(self.folderTable, folderName, "CREATED", currenttime))
                self.connection.commit()
            else:
                print("Folder Already Present {}".format(folderName))
        else:
            print("Please check folder name and/or location {}".format(folderName))
            exit(0)
    
    
    def _folderCheck(self, folderName, folderRegex, inputdir):
        for folder in os.listdir(inputdir):
            if re.match(folderRegex, folder) and folderName==folder:
                return True
        return False

    def destroyDb(self):
        '''
        Destroy database file
        '''
        pass


if __name__ == "__main__":
    pass