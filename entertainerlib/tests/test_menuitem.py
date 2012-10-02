# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests MenuItem"""

from entertainerlib.gui.widgets.menu_item import MenuItem
from entertainerlib.tests import EntertainerTest

class MenuItemTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.menu_item"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.item = MenuItem()

    def test_create(self):
        '''Test correct MenuItem initialization.'''
        self.assertTrue(isinstance(self.item, MenuItem))

    def test_userdata(self):
        '''Test the use of the userdata property.'''
        self.item.userdata = "This is data."
        self.assertEqual(self.item.userdata, "This is data.")

    def test_animatein(self):
        '''Test the use of the animate_in method.'''
        self.assertTrue(self.item.animate_in is not None)

    def test_animateout(self):
        '''Test the use of the animate_out method.'''
        self.assertTrue(self.item.animate_out is not None)

