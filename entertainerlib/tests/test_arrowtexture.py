# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests ArrowTexture.'''

from entertainerlib.gui.widgets.arrow_texture import ArrowTexture
from entertainerlib.tests import EntertainerTest


class ArrowTextureTest(EntertainerTest):
    '''Test for entertainerlib.gui.widgets.arrow_texture.'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.arrow = ArrowTexture(0.5, 0.9, 0.40, (21, 45, 83, 255),
            (255, 0, 0, 255), ArrowTexture.UP)

    def test_create(self):
        '''Test correct ArrowTexture initialization.'''
        self.assertTrue(isinstance(self.arrow, ArrowTexture))

    def test_bounce(self):
        '''Test the bounce method.'''
        self.arrow.bounce()
        self.assertTrue(self.arrow.score.is_playing())

