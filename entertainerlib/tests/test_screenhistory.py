# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests ScreenHistory'''

from entertainerlib.gui.screen_history import ScreenHistory
from entertainerlib.gui.screens.screen import Screen
from entertainerlib.tests import EntertainerTest

class ScreenHistoryTest(EntertainerTest):
    '''Test for entertainerlib.gui.screen_history'''

    def setUp(self):
        EntertainerTest.setUp(self)

        self.screen_history = ScreenHistory(None)

    def test_create(self):
        '''Test correct ScreenHistory initialization.'''
        self.assertTrue(isinstance(self.screen_history, ScreenHistory))

    def test_is_empty(self):
        '''Test the is_empty property.'''
        self.assertTrue(self.screen_history.is_empty)
        screen = Screen()
        self.screen_history.add_screen(screen)
        self.assertFalse(self.screen_history.is_empty)

