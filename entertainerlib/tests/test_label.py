# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests Label"""
# pylint: disable-msg=W0212

import clutter

from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.label import Label
from entertainerlib.tests import EntertainerTest

class LabelTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.label"""

    def setUp(self):
        """Set up the test"""
        EntertainerTest.setUp(self)

        self.label = Label(0.1, "screentitle", 0.1, 0.2, "Test Label text",
            "test_name")

    def test_create(self):
        """Test correct Label initialization."""
        self.assertTrue(isinstance(self.label, (Base, clutter.Label)))

    def test_set_size(self):
        """Test correct size setting."""
        self.label.set_size(.75, .8)
        self.assertEqual(self.label.get_size(), (1024, 614))
        self.assertTrue(self.label.width > 0.75 * 0.99)
        self.assertTrue(self.label.width < 0.75 * 1.01)

    def test_width(self):
        """Test the width property."""
        self.label.width = 0.5
        self.assertEqual(self.label.width, 0.5)

        self.label._set_width(0.4)
        self.assertTrue(self.label._get_width() > 0.4 * 0.99)
        self.assertTrue(self.label._get_width() < 0.4 * 1.01)

    def test_font_size(self):
        """Test the font_size property."""
        self.label.font_size = 0.2
        self.assertEqual(self.label.font_size, 0.2)

        self.label._set_font_size(0.3)
        self.assertEqual(self.label._get_font_size(), 0.3)

    def testHeight(self):
        """Test the height property"""
        self.label.height = 0.5
        self.assertEqual(self.label.height, 0.5)

        self.label._set_height(0.4)
        self.assertTrue(self.label._get_height() > 0.4 * 0.99)
        self.assertTrue(self.label._get_height() < 0.4 * 1.01)

    def test_position(self):
        """Test the position property."""
        self.assertEqual(self.label.position, (0.1, 0.2))

        self.label.position = (0.4, 0.5)
        self.assertEqual(self.label.position, (0.4, 0.5))

        self.label._set_position((0.3, 0.6))
        self.assertEqual(self.label._get_position(), (0.3, 0.6))

    def test_color(self):
        """Test the color property."""
        self.label.color = "screentitle"
        self.assertEqual(self.label.color, "screentitle")
        self.assertEqual(self.label.get_color().red, 255)
        self.assertEqual(self.label.get_color().green, 255)
        self.assertEqual(self.label.get_color().blue, 255)
        self.assertEqual(self.label.get_color().alpha, 16)

        self.label.color = "background"
        self.assertEqual(self.label.color, "background")
        self.assertEqual(self.label.get_color().red, 21)
        self.assertEqual(self.label.get_color().green, 45)
        self.assertEqual(self.label.get_color().blue, 83)
        self.assertEqual(self.label.get_color().alpha, 255)

