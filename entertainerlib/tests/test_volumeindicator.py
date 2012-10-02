# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests VolumeIndicator"""

import clutter

from entertainerlib.gui.widgets.volume_indicator import VolumeIndicator
from entertainerlib.tests import EntertainerTest


class VolumeIndicatorTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.volume_indicator"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.indicator = VolumeIndicator()
        clutter.Stage().add(self.indicator)

    def test_create(self):
        '''Test correct VolumeIndicator initialization.'''
        self.assertTrue(isinstance(self.indicator, VolumeIndicator))

    def test_show_volume(self):
        '''Test the use of the show_volume method.'''
        self.indicator.show_volume(5)
        self.assertTrue(self.indicator.visible)

