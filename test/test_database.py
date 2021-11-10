import unittest
import unittest.mock as mock
import pytest

import glob
import os

from sqlite3 import ProgrammingError

from configparser import ConfigParser
from illumina_uploader.database import Database
from illumina_uploader.utils import setupLogger

class DbTests(unittest.TestCase):
    '''
    TODO Database tests
    '''
    def setUp(self):
        folder_regex = ''
        input_dirs = ['.']        
        self.db_info = {
            'location': 'test.db',
            'backupfolder': 'test/data',
            'foldertable': 'folderinfo',
        }
        logger = setupLogger(os.path.join(self.db_info['backupfolder'], 'test.log'))
        queries = {
            'createtable': "CREATE TABLE {} (folder text, status text, querylastrun text);",
            'checkfolderpresence': "SELECT * FROM {} WHERE folder='{}';",
            'insertfolder': "INSERT INTO {} VALUES ('{}','{}','{}');",
            'getfolderstoupload': "SELECT {} FROM {} WHERE status<>'{}';",
            'markfileindb':  "UPDATE {} SET status='{}' WHERE folder='{}';",
            'selectallfolders': "SELECT * FROM {};",
        }
        self.db = Database(self.db_info, queries, logger, input_dirs, folder_regex)
        

    def tearDown(self):
        self.db.closeConnection()
        try:
            os.remove(self.db_info['location'])
            os.remove(os.path.join(self.db_info['backupfolder'], 'test.log'))
            for db in glob.glob(os.path.join(self.db_info['backupfolder'], 'backup_*.db')):
                os.remove(db)
        except OSError as e:
            print(e)
            pass

    def test_createDb(self):
        """
        Test that Database.getFolderList() returns an empty list on a newly-created DB
        """
        self.db.createDb()
        self.db.connection = self.db.initConnection()
        folder_list = self.db.getFolderList()
        self.assertTrue(folder_list == [])

    def test_checkInputs(self):
        """
        Test that Database.checkInputs() raises SystemExit if one
        of the inputs does not exist
        """
        self.db.location = 'idontexist'
        with pytest.raises(SystemExit):
            self.db.checkInputs()

    def test_closeConnection(self):
        """
        Test that attempting to obtain cursor from the connection
        raises sqlite3.ProgrammingError after Database.closeConnection() is run.
        """
        self.db.connection = self.db.initConnection()
        self.db.closeConnection()
        with pytest.raises(ProgrammingError):
            conn = self.db.connection.cursor()

    def test_backupDb(self):
        """
        Test that Database.backupDb() creates backup file in the expected location
        """
        self.db.backupDb()
        if glob.glob(os.path.join(self.db_info['backupfolder'], 'backup_*.db')):
            backup_exists = True
        else:
            backup_exists = False
        
        self.assertTrue(backup_exists)


if __name__ == "__main__":
    unittest.main()
