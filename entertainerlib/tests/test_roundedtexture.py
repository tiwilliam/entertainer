# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests RoundedTexture.'''

import os

import gtk

from entertainerlib.gui.widgets.rounded_texture import RoundedTexture
from entertainerlib.tests import EntertainerTest

THIS_DIR = os.path.dirname(__file__)


class RoundedTextureTest(EntertainerTest):
    '''Test for entertainerlib.gui.widgets.rounded_texture.'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        filename = os.path.join(THIS_DIR, 'data/ImageThumbnailer/test.jpg')
        pix_buffer = gtk.gdk.pixbuf_new_from_file(filename)
        self.texture = RoundedTexture(0.5, 0.9, 0.40, 0.4, pix_buffer)

    def test_create(self):
        '''Test correct RoundedTexture initialization.'''
        self.assertTrue(isinstance(self.texture, RoundedTexture))

