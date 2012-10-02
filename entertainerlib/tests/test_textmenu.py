# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests TextMenu"""

from entertainerlib.gui.widgets.text_menu import TextMenu
from entertainerlib.tests import EntertainerTest

class TextMenuTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.text_menu"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.menu = TextMenu()

    def test_create(self):
        '''Test correct TextMenu initialization.'''
        self.assertTrue(isinstance(self.menu, TextMenu))

    def test_add_item(self):
        '''Test the add_item method.'''
        items = self.menu.count
        self.menu.add_item("text", "extra_text", "data")
        self.assertEqual(self.menu.count, items + 1)

