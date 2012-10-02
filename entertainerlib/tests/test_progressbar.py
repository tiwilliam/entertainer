# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests ProgressBar.'''

from entertainerlib.gui.widgets.progress_bar import ProgressBar
from entertainerlib.tests import EntertainerTest
from entertainerlib.tests.mock import MockMediaPlayer

class ProgressBarTest(EntertainerTest):
    '''Test for entertainerlib.gui.widgets.progress_bar.'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.progress_bar = ProgressBar(0.5, 0.9, 0.40, 0.04)
        self.media_player =  MockMediaPlayer()
        self.progress_bar.media_player = self.media_player

    def test_create(self):
        '''Test correct ProgressBar initialization.'''
        self.assertTrue(isinstance(self.progress_bar, ProgressBar))

    def test_media_player(self):
        '''Test the media_player property.'''
        self.assertEqual(self.progress_bar.media_player, self.media_player)

    def test_progress(self):
        '''Test the progress property.'''
        self.progress_bar.progress = 0.5
        self.assertEqual(self.progress_bar.progress, 0.5)

    def test_visible(self):
        '''Test the visible property.'''
        self.progress_bar.visible = True
        self.assertEqual(self.progress_bar.visible, True)
        self.progress_bar.visible = False
        self.assertEqual(self.progress_bar.visible, False)

