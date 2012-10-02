# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests ArrowTexture.'''

import os

import gtk

from entertainerlib.gui.widgets.eyecandy_texture import EyeCandyTexture
from entertainerlib.tests import EntertainerTest

THIS_DIR = os.path.dirname(__file__)


class EyeCandyTextureTest(EntertainerTest):
    '''Test for entertainerlib.gui.widgets.eyecandy_texture.'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        filename = os.path.join(THIS_DIR, 'data/ImageThumbnailer/test.jpg')
        pix_buffer = gtk.gdk.pixbuf_new_from_file(filename)
        self.eyecandy = EyeCandyTexture(0.5, 0.9, 0.40, 0.4, pix_buffer)

    def test_create(self):
        '''Test correct EyeCandyTexture initialization.'''
        self.assertTrue(isinstance(self.eyecandy, EyeCandyTexture))
