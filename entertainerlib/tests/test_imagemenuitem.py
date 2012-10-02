# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests ImageMenuItem"""
# pylint: disable-msg=W0212

import os

from entertainerlib.gui.widgets.image_menu import ImageMenuItem
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.tests import EntertainerTest

THIS_DIR = os.path.dirname(__file__)

class ImageMenuItemTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.image_menu_item"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.filename = os.path.join(THIS_DIR, 'data/ImageThumbnailer/test.jpg')
        self.texture = Texture(self.filename)
        self.original_ratio = float(self.texture.get_width()) / \
            self.texture.get_height()

        self.item = ImageMenuItem(0.2, 0.1, self.texture)

    def test_create(self):
        '''Test correct ImageMenuItem initialization.'''
        self.assertTrue(isinstance(self.item, ImageMenuItem))

    def test_width(self):
        '''Test correct width setting.'''
        self.assertTrue(self.texture.get_width() <= self.item.get_abs_x(0.2))

    def test_height(self):
        '''Test correct height setting.'''
        self.assertTrue(self.texture.get_height() <= self.item.get_abs_y(0.1))

    def test_ratio(self):
        '''Test that ratio correctly calculates the expected heights.'''
        self.assertTrue(self.original_ratio > self.item.original_ratio * 0.98)
        self.assertTrue(self.original_ratio < self.item.original_ratio * 1.02)

