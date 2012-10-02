# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Test for backend.core.db.connection'''

import os

from storm.locals import Store

from entertainerlib.db.connection import Database, SCHEMA
from entertainerlib.tests import EntertainerTestWithDatabase

class DatabaseTest(EntertainerTestWithDatabase):
    '''Test for backend.core.db.connection'''

    def setUp(self):
        EntertainerTestWithDatabase.setUp(self)

    def _checkValidDatabase(self, storage):
        '''Checks the Store to make sure it has a valid database'''

        store = Store(storage)
        for table in SCHEMA.iterkeys():
            result = store.execute('SELECT * FROM `%s`' % table.lower())
            self.assertEqual(result.get_all(), [])
        return True

    def testCreate(self):
        '''Test the creation of a new database'''

        filename = self.get_temp_file()
        storage = Database(filename)

        self.assertTrue(os.path.exists(filename))
        self.assertTrue(self._checkValidDatabase(storage))

    def testUseExisting(self):
        '''Test the connection to an existing database'''

        storage_file = self.data_dir + '/media'
        self.assertTrue(os.path.exists(storage_file))
        storage = Database(storage_file)
        self.assertTrue(self._checkValidDatabase(storage))

