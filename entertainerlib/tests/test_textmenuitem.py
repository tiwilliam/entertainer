# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests MenuItem"""

from entertainerlib.gui.widgets.text_menu import (
    TextMenuItem, AnimatingMenuItem)
from entertainerlib.tests import EntertainerTest

class TextMenuItemTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.menu_item"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.item1 = TextMenuItem(0.3807, 0.2604, "Text 1")
        self.item2 = TextMenuItem(0.3807, 0.2604, "Text 2", "Extra text 2")
        self.item3 = AnimatingMenuItem(0.3807, 0.2604, "Text 3", "Extra text 3")

    def test_create(self):
        '''Test correct MenuItem initialization.'''
        self.assertTrue(isinstance(self.item1, TextMenuItem))
        self.assertTrue(isinstance(self.item2, TextMenuItem))
        self.assertTrue(isinstance(self.item3, AnimatingMenuItem))

    def test_animatein(self):
        '''Test the use of the animate_in method.'''
        self.assertTrue(self.item1.animate_in is not None)
        self.assertTrue(self.item3.animate_in is not None)

    def test_animateout(self):
        '''Test the use of the animate_out method.'''
        self.assertTrue(self.item1.animate_out is not None)
        self.assertTrue(self.item3.animate_out is not None)

    def test_update(self):
        '''Test the use of the update method.'''
        self.item2.font_size = 1
        self.item2.color = "fake color"
        self.item2.update("new text", "new extra text")

        self.assertEqual(self.item2.text, "new text")
        self.assertEqual(self.item2.extra_text, "new extra text")
        self.assertEqual(self.item2.label.font_size, 1)
        self.assertEqual(self.item2.extra_label.font_size, 1)
        self.assertEqual(self.item2.label.color, "fake color")
        self.assertEqual(self.item2.extra_label.color, "fake color")

