# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests ScreenFactory'''
# pylint: disable-msg=W0212

import os

from entertainerlib.client.medialibrary import music
from entertainerlib.gui.screens.album import Album
from entertainerlib.gui.screens.artist import Artist
from entertainerlib.gui.screens.audio_play import AudioPlay
from entertainerlib.gui.screens.disc import Disc
from entertainerlib.gui.screens.factory import ScreenFactory
from entertainerlib.gui.screens.main import Main
from entertainerlib.gui.screens.movie import Movie
from entertainerlib.gui.screens.music import Music
from entertainerlib.gui.screens.photo import Photo
from entertainerlib.gui.screens.photo_albums import PhotoAlbums
from entertainerlib.gui.screens.photographs import Photographs
from entertainerlib.gui.screens.question import Question
from entertainerlib.gui.screens.tv_episodes import TvEpisodes
from entertainerlib.gui.screens.tv_series import TvSeries
from entertainerlib.gui.screens.video_osd import VideoOSD
from entertainerlib.gui.screens.video import Video
from entertainerlib.gui.screens.weather import WeatherScreen
from entertainerlib.tests import EntertainerTest
from entertainerlib.tests.mock import MockImage
from entertainerlib.tests.mock import MockImageLibrary
from entertainerlib.tests.mock import MockMediaPlayer
from entertainerlib.tests.mock import MockMovie
from entertainerlib.tests.mock import MockMusicLibrary
from entertainerlib.tests.mock import MockTVEpisode
from entertainerlib.tests.mock import MockTVSeries
from entertainerlib.tests.mock import MockVideoLibrary


class ScreenFactoryTest(EntertainerTest):
    '''Test for entertainerlib.gui.screens.factory'''

    def setUp(self):
        EntertainerTest.setUp(self)

        image_libary = MockImageLibrary()
        music_library = MockMusicLibrary()
        media_player = MockMediaPlayer()
        video_library = MockVideoLibrary()
        self.factory = ScreenFactory(image_libary, music_library,
            video_library, media_player, None, None)

        self.kwargs = {}

    def test_create(self):
        '''Test correct ScreenFactory initialization'''
        self.assertTrue(isinstance(self.factory, ScreenFactory))

    def test__generate_album(self):
        '''Test _generate_album returns a Album screen'''
        self.kwargs['album'] = music.Album('', '', 240, 2010, '', [])
        screen = self.factory._generate_album(self.kwargs)
        self.assertTrue(isinstance(screen, Album))

    def test__generate_artist(self):
        '''Test _generate_artist returns a Artist screen'''
        self.kwargs['artist'] = 'Test'
        screen = self.factory._generate_artist(self.kwargs)
        self.assertTrue(isinstance(screen, Artist))

    def test__generate_audio_play(self):
        '''Test _generate_audio_play returns a AudioPlay screen'''
        album = music.Album('', '', 240, 2010, '', [])
        track = music.Track('', '', 1, '', album, 2010, 60, '', None)
        self.kwargs['track'] = track
        screen = self.factory._generate_audio_play(self.kwargs)
        self.assertTrue(isinstance(screen, AudioPlay))

    def test__generate_disc(self):
        '''Test _generate_disc returns a Disc screen'''
        screen = self.factory._generate_disc(self.kwargs)
        self.assertTrue(isinstance(screen, Disc))

    def test__generate_main(self):
        '''Test _generate_main returns a Main screen'''
        screen = self.factory._generate_main(self.kwargs)
        self.assertTrue(isinstance(screen, Main))

    def test__generate_movie(self):
        '''Test _generate_movie returns a Movie screen'''
        self.kwargs['movie'] = MockMovie()
        screen = self.factory._generate_movie(self.kwargs)
        self.assertTrue(isinstance(screen, Movie))

    def test__generate_music(self):
        '''Test _generate_music returns a Music screen'''
        screen = self.factory._generate_music(self.kwargs)
        self.assertTrue(isinstance(screen, Music))

    def test__generate_photo_albums(self):
        '''Test _generate_photo_albums returns a PhotoAlbums screen'''
        screen = self.factory._generate_photo_albums(self.kwargs)
        self.assertTrue(isinstance(screen, PhotoAlbums))

    def test__generate_photo(self):
        '''Test _generate_photo returns a Photo screen'''
        self.kwargs['current_photo_index'] = 0
        filename = os.path.join(self.data_dir, 'ImageThumbnailer', 'test.jpg')
        mock_image = MockImage(filename=filename)
        self.kwargs['images'] = [mock_image]
        screen = self.factory._generate_photo(self.kwargs)
        self.assertTrue(isinstance(screen, Photo))

    def test__generate_photographs(self):
        '''Test _generate_photographs returns a Photographs screen'''
        self.kwargs['title'] = 'Test title'
        mock_image = MockImage()
        self.kwargs['images'] = [mock_image]
        screen = self.factory._generate_photographs(self.kwargs)
        self.assertTrue(isinstance(screen, Photographs))

    def test__generate_question(self):
        '''Test _generate_question returns a Question screen'''
        self.kwargs['question'] = None
        self.kwargs['answers'] = []
        screen = self.factory._generate_question(self.kwargs)
        self.assertTrue(isinstance(screen, Question))

    def test__generate_tv_series(self):
        '''Test _generate_tv_series returns a TvSeries screen'''
        self.kwargs['tv_series'] = MockTVSeries()
        screen = self.factory._generate_tv_series(self.kwargs)
        self.assertTrue(isinstance(screen, TvSeries))

    def test__generate_tv_episodes(self):
        '''Test _generate_tv_episodes returns a TvEpisodes screen'''
        self.kwargs['episodes'] = [MockTVEpisode()]
        self.kwargs['tv_series'] = MockTVSeries()
        screen = self.factory._generate_tv_episodes(self.kwargs)
        self.assertTrue(isinstance(screen, TvEpisodes))

    def test__generate_video(self):
        '''Test _generate_video returns a Video screen'''
        screen = self.factory._generate_video(self.kwargs)
        self.assertTrue(isinstance(screen, Video))

    def test__generate_video_osd(self):
        '''Test _generate_video_osd returns a VideoOSD screen'''
        screen = self.factory._generate_video_osd(self.kwargs)
        self.assertTrue(isinstance(screen, VideoOSD))

    def test__generate_weather(self):
        '''Test _generate_weather returns a WeatherScreen screen'''
        screen = self.factory._generate_weather(self.kwargs)
        self.assertTrue(isinstance(screen, WeatherScreen))

    def test_generate_screen(self):
        '''Test generate_screen for a nominal path. All paths can't be tested
        because there is too much set up in kwargs and most methods are tested
        in the specific _generate_* methods'''
        screen = self.factory.generate_screen('audio_cd')
        self.assertTrue(isinstance(screen, Disc))

