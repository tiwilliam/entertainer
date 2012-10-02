# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests Theme"""

from entertainerlib.tests import EntertainerTest
from entertainerlib.gui.theme import Theme

class ThemeTest(EntertainerTest):
    """Test for entertainerlib.gui.theme"""

    def setUp(self):
        """Set up the test"""
        EntertainerTest.setUp(self)

        self.theme = Theme(self.config.theme_path)

    def tearDown(self):
        """Clean up after the test"""
        EntertainerTest.tearDown(self)

    def testCreate(self):
        """Test correct Theme initialization"""
        self.assertTrue(isinstance(self.theme, Theme))

    def testGetColor(self):
        """Test getting the color"""
        self.assertEqual(self.theme.get_color("background"), (21, 45, 83, 255))

    def testBadColor(self):
        """Test the output of color when it get a bad key element"""
        self.assertEqual(self.theme.get_color("junk"), (255, 0, 0, 255))
