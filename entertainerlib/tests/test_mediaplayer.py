# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests MediaPlayer"""

import clutter
import os

from entertainerlib.client.media_player import MediaPlayer
from entertainerlib.client.medialibrary.videos import VideoItem
from entertainerlib.tests import EntertainerTest

THIS_DIR = os.path.dirname(__file__)

class MediaPlayerTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.media_player"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.player = MediaPlayer(clutter.Stage(), 100, 100)
        self.video_item = VideoItem()
        self.video_item.filename = THIS_DIR + '/data/VideoThumbnailer/test.avi'
        self.player.set_media(self.video_item)

    def test_create(self):
        '''Test correct MediaPlayer initialization.'''
        self.assertTrue(isinstance(self.player, MediaPlayer))

    def test_volume(self):
        '''Test the use of the volume property.'''
        self.player.volume = 10
        self.assertEqual(self.player.volume, 10)
        self.player.volume = 99
        self.assertEqual(self.player.volume, 20)
        self.player.volume = -10
        self.assertEqual(self.player.volume, 0)

    def test_volume_down(self):
        '''Test the use of the volume_down method.'''
        self.player.volume = 10
        self.player.volume_down()
        self.assertEqual(self.player.volume, 9)

    def test_volume_up(self):
        '''Test the use of the volume_up method.'''
        self.player.volume = 10
        self.player.volume_up()
        self.assertEqual(self.player.volume, 11)

    def test_set_media(self):
        '''Test the use of the set_media method.'''
        # The method is called during setUp.
        self.assertTrue(self.player.media is not None)

    def test_get_media(self):
        '''Test the use of the get_media method.'''
        self.assertEqual(self.player.get_media(), self.video_item)

    def test_has_media(self):
        '''Test the use of the has_media method.'''
        self.assertTrue(self.player.has_media())

    def test_getmediatype(self):
        '''Test the use of the get_media_type method.'''
        self.assertEqual(self.player.get_media_type(),
            self.video_item.get_type())

    def test_play_stop(self):
        '''Test the use of the play and stop methods.'''
        self.player.play()
        self.assertTrue(self.player.is_playing)
        self.player.stop()
        self.assertFalse(self.player.is_playing)

    def test_get_media_title(self):
        '''Test the use of the get_media_title method.'''
        self.assertEqual(self.player.get_media_title(),
            THIS_DIR + '/data/VideoThumbnailer/test.avi')

    def test_get_media_duration_string(self):
        '''Test the use of the get_media_title method.'''
        self.assertEqual(self.player.get_media_duration_string(), "00:00")

