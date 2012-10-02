# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests ImageMenu"""

import os

from entertainerlib.gui.widgets.image_menu import ImageMenu
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.tests import EntertainerTest

THIS_DIR = os.path.dirname(__file__)

class ImageMenuTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.image_menu"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.menu = ImageMenu(0, 0)

        self.texture = Texture(os.path.join(
            THIS_DIR, 'data/ImageThumbnailer/test.jpg'))

    def test_create(self):
        '''Test correct ImageMenu initialization.'''
        self.assertTrue(isinstance(self.menu, ImageMenu))

    def test_add_item(self):
        '''Test the add_item method.'''
        items = self.menu.count
        self.menu.add_item(self.texture, "data")
        self.assertEqual(self.menu.count, items + 1)

