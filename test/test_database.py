import unittest
import unittest.mock as mock
import pytest

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
        logger = setupLogger('test.log')
        self.db_info = {
            'location': 'test.db',
            'backupfolder': '.',
            'foldertable': 'folderinfo',
        }
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
        except OSError as e:
            pass

    def test_create_db(self):
        self.db.createDb()
        self.db.connection = self.db.initConnection()
        folder_list = self.db.getFolderList()
        self.assertTrue(folder_list == [])

    def test_checkInputs(self):
        self.db.location = 'idontexist'
        with pytest.raises(SystemExit):
            self.db.checkInputs()

if __name__ == "__main__":
    unittest.main()
