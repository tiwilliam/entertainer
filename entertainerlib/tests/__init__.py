# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''The Entertainer test suite'''

import os

from storm.locals import Store
import testtools

from entertainerlib.db.connection import Database
from entertainerlib.client.translation_setup import TranslationSetup
from entertainerlib.configuration import Configuration

TranslationSetup()


class EntertainerTest(testtools.TestCase):
    '''Test for use in the Entertainer test suite.'''

    def setUp(self):
        '''Set up the basic file I/O requirements.'''
        self.test_dir = self.get_temp_file()
        os.mkdir(self.test_dir)
        self.test_cfg_dir = self.get_temp_file()
        self.config = Configuration(self.test_cfg_dir)
        self.data_dir = os.path.dirname(__file__) + '/data'

    def get_temp_file(self):
        '''Get a file (or folder) in a temp directory to use.'''

        def create_new_filename():
            '''Create a random filename.'''
            try:
                return os.path.join(self.test_dir, self.getUniqueString())
            except AttributeError:
                return '/tmp/%(filename)s' % {
                    'filename': self.getUniqueString()}

        filename = create_new_filename()
        while os.path.exists(filename):
            filename = create_new_filename()
        return filename


class EntertainerTestWithDatabase(EntertainerTest):
    '''Test that requires a database'''

    def setUp(self):
        EntertainerTest.setUp(self)
        self.db = Database(self.get_temp_file())

    def create_database_and_store(self, filename):
        '''Create and return a Database and a storm Store.'''
        db = Database(self.get_temp_file())
        store = Store(db)
        return db, store


