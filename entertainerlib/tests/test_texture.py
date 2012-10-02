# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests Texture"""
# pylint: disable-msg=W0212

import os

import clutter

from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.tests import EntertainerTest

THIS_DIR = os.path.dirname(__file__)

class TextureTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.texture"""

    def setUp(self):
        """Set up the test"""
        EntertainerTest.setUp(self)

        self.filename = os.path.join(THIS_DIR, 'data/ImageThumbnailer/test.jpg')

        self.texture = Texture(self.filename, 0.1, 0.2)

    def tearDown(self):
        """Clean up after the test"""
        EntertainerTest.tearDown(self)

    def testCreate(self):
        """Test correct Texture initialization"""
        self.assertTrue(isinstance(self.texture, (Base, clutter.Texture)))

    def testPosition(self):
        """Test the position property"""
        self.assertEqual(self.texture.position, (0.1, 0.2))

        self.texture.position = (0.4, 0.5)
        self.assertEqual(self.texture.position, (0.4, 0.5))

        self.texture._set_position((0.3, 0.6))
        self.assertEqual(self.texture._get_position(), (0.3, 0.6))

    def testNoInitPosition(self):
        """Test that a texture will be displayed at the origin of the display
        area if no initial position is given"""
        no_pos_texture = Texture(self.filename)
        self.assertEqual(no_pos_texture.position, (0, 0))

