# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Logger object tests'''

import logging

from entertainerlib.tests import EntertainerTest
from entertainerlib.logger import Logger

class TestLogger(EntertainerTest):
    '''Logger test case'''

    def setUp(self):
        '''See unittest.TestCase'''
        EntertainerTest.setUp(self)

        self.logger = Logger()

    def tearDown(self):
        '''See unittest.TestCase'''
        EntertainerTest.tearDown(self)

    def testGetLogger(self):
        '''Tests logger.getLogger without a name'''
        self.lowlogger = self.logger.getLogger()

        self.assertTrue(isinstance(self.lowlogger, logging.Logger))

    def testNamedLogger(self):
        '''Tests logger.getLogger with a name'''
        self.lowlogger = self.logger.getLogger('test')
        self.lowlogger.debug('Logger test for named logger test')
        # test this log for its name

    def testNoParams(self):
        '''Tests multiple logging mechanism'''
        # No way to test now because logging will only permit the creation of
        # one log file per module. Commented out until I can determine a way
        # to test this.
        #self.default_path = os.path.join(
        #    os.path.abspath('.'), 'data/entertainerdefault.log')
        #try:
        #    os.remove(self.default_path)
        #except OSError:
        #    pass

        #self.logger = Logger()
        #self.lowlogger = self.logger.getLogger()

        #self.assertTrue(os.path.exists(self.default_path))

