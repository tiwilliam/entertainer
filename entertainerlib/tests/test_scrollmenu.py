# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests ScrollMenu"""

import time

from entertainerlib.gui.widgets.scroll_menu import ScrollMenu
from entertainerlib.tests import EntertainerTest

class ScrollMenuTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.scroll_menu"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.menu = ScrollMenu(10, 60, 0.045, "menuitem_active")
        self.menu.set_name("mainmenu")

        self.menu.add_item(_("Play CD"), "disc")
        self.menu.add_item(_("Videos"), "videos")
        self.menu.add_item(_("Music"), "music")
        self.menu.add_item(_("Photographs"), "photo")
        self.menu.add_item(_("Headlines"), "rss")

    def tearDown(self):
        '''Clean up after the test.'''
        EntertainerTest.tearDown(self)

    def test_create(self):
        '''Test correct ScrollMenu initialization.'''
        self.assertTrue(isinstance(self.menu, ScrollMenu))

    def test_selected_index(self):
        '''Test the use of the selected_index property.'''
        self.menu.selected_index = 2
        self.assertEqual(self.menu.selected_index, self.menu.get_index("music"))

    def test_get_index(self):
        '''Test the use of the get_index method.'''
        self.assertEqual(self.menu.get_index("photo"), 3)

    def test_scroll_up(self):
        '''Test the use of the scroll_up method.'''
        self.menu.selected_index = 2
        self.menu.stop_animation()
        self.menu.scroll_up()
        time.sleep(1)
        self.assertEqual(self.menu.selected_index, 1)

    def test_scroll_down(self):
        '''Test the use of the scroll_up method.'''
        self.menu.selected_index = 2
        self.menu.stop_animation()
        self.menu.scroll_down()
        time.sleep(1)
        self.assertEqual(self.menu.selected_index, 3)

