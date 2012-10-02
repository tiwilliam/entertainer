# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests LoadingAnimation.'''

from entertainerlib.gui.widgets.loading_animation import LoadingAnimation
from entertainerlib.tests import EntertainerTest


class LoadingAnimationTest(EntertainerTest):
    '''Test for entertainerlib.gui.widgets.loading_animation.'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.animation = LoadingAnimation(0.5, 0.5)

    def test_create(self):
        '''Test correct LoadingAnimation initialization.'''
        self.assertTrue(isinstance(self.animation, LoadingAnimation))

    def test_hide(self):
        '''Test the hide method.'''
        self.assertTrue(self.animation.hide)

    def test_show(self):
        '''Test the show method.'''
        self.assertTrue(self.animation.show)

