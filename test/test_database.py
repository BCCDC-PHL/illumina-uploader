import unittest

import os

from configparser import ConfigParser
from illumina_uploader.database import Database
from illumina_uploader.utils import setupLogger

class DbTests(unittest.TestCase):
    '''
    TODO Database tests
    '''
    def setUp(self):
        folder_regex = ''
        input_dirs = '.'
        logger = setupLogger('test.log')
        self.db_info = {
            'location': 'test.db',
            'backupfolder': '.',
            'foldertable': 'folderinfo',
        }
        self.queries = {
            'createtable': "CREATE TABLE {} (folder text, status text, querylastrun text);",
            'checkfolderpresence': "SELECT * FROM {} WHERE folder='{}';",
            'insertfolder': "INSERT INTO {} VALUES ('{}','{}','{}');",
            'getfolderstoupload': "SELECT {} FROM {} WHERE status<>'{}';",
            'markfileindb':  "UPDATE {} SET status='{}' WHERE folder='{}';",
            'selectallfolders': "SELECT * FROM {};",
        }
        self.db = Database(self.db_info, self.queries, logger, input_dirs, folder_regex)
        self.conn = self.db.initConnection()

    def tearDown(self):
        self.db.closeConnection()
        try:
            os.remove(self.db_info['location'])
        except OSError as e:
            pass
                    

    def test_create_db(self):
        self.db.createDb()
        folder_list = self.db.getFolderList()
        print(folder_list)
        self.assertTrue(False)

    def test_correct_folder_permissions(self):
        self.assertTrue(False)


   
if __name__ == "__main__":
    unittest.main()
