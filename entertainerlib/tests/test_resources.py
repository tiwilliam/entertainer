# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests Resources'''

import os
import shutil

from xdg import BaseDirectory

from entertainerlib.tests import EntertainerTest
from entertainerlib.configuration import Resources

class ResourcesTest(EntertainerTest):
    '''Test for configuration.Resources'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.test_resource = self.test_cfg_dir.replace('/', '')
        self.resources = Resources(resource=self.test_resource)

    def tearDown(self):
        '''Clean up after the test. Resources creates the directories if they
        are missing. But since it uses XDG to do it, there is no way to write
        the directories to /tmp so we must clean up after each test.'''
        shutil.rmtree(self.resources.cache_dir)
        shutil.rmtree(self.resources.config_dir)
        shutil.rmtree(self.resources.data_dir)

    def test_create(self):
        '''Test correct Resources initialization.'''
        self.assertTrue(isinstance(self.resources, Resources))
        self.assertEqual(self.resources.cache_dir, os.path.join(
            BaseDirectory.xdg_cache_home, self.test_resource))
        self.assertEqual(self.resources.config_dir, os.path.join(
            BaseDirectory.xdg_config_home, self.test_resource))
        self.assertEqual(self.resources.data_dir, os.path.join(
            BaseDirectory.xdg_data_home, self.test_resource))

