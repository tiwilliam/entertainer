# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''ScreenFactory - Create correct screen based on the type provided.'''

from entertainerlib.gui.screens.artist import Artist
from entertainerlib.gui.screens.album import Album
from entertainerlib.gui.screens.audio_play import AudioPlay
from entertainerlib.gui.screens.disc import Disc
from entertainerlib.gui.screens.main import Main
from entertainerlib.gui.screens.movie import Movie
from entertainerlib.gui.screens.music import Music
from entertainerlib.gui.screens.photo import Photo
from entertainerlib.gui.screens.photo_albums import PhotoAlbums
from entertainerlib.gui.screens.photographs import Photographs
from entertainerlib.gui.screens.question import Question
from entertainerlib.gui.screens.tv_episodes import TvEpisodes
from entertainerlib.gui.screens.tv_series import TvSeries
from entertainerlib.gui.screens.video import Video
from entertainerlib.gui.screens.video_osd import VideoOSD
from entertainerlib.gui.screens.weather import WeatherScreen


class ScreenFactory(object):
    '''Generate a screen based on the type provided.'''

    def __init__(self, image_library, music_library, video_library,
        media_player, move_to_new_screen_callback,
        move_to_previous_screen_callback):
        '''All the possible common things that a screen could use to initialize
        are factory instance variables. Any additional specific information
        needed for a screen will be provided in a dictionary that is received
        by the generate_screen method.'''

        self.image_library = image_library
        self.music_library = music_library
        self.video_library = video_library
        self.media_player = media_player
        self.move_to_new_screen_callback = move_to_new_screen_callback
        self.move_to_previous_screen_callback = move_to_previous_screen_callback

    def generate_screen(self, screen_type, kwargs=None):
        '''Generate the proper screen by delegating to the proper generator.'''

        # The generate methods will add new key value pairs to kwargs to create
        # screens so ensure that it is a dictionary
        if kwargs is None:
            kwargs = {}

        generator_methods = {
            'album' : self._generate_album,
            'artist' : self._generate_artist,
            'audio_cd' : self._generate_disc,
            'audio_play' : self._generate_audio_play,
            'main' : self._generate_main,
            'movie' : self._generate_movie,
            'music' : self._generate_music,
            'photo' : self._generate_photo,
            'photo_albums' : self._generate_photo_albums,
            'photographs' : self._generate_photographs,
            'question' : self._generate_question,
            'tv_episodes' : self._generate_tv_episodes,
            'tv_series' : self._generate_tv_series,
            'video' : self._generate_video,
            'video_osd' : self._generate_video_osd,
            'weather' : self._generate_weather
        }

        return generator_methods[screen_type](kwargs)

    def _generate_album(self, kwargs):
        '''Generate an Album screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        kwargs['music_library'] = self.music_library
        return Album(**kwargs)

    def _generate_artist(self, kwargs):
        '''Generate an Artist screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        kwargs['music_library'] = self.music_library
        return Artist(**kwargs)

    def _generate_audio_play(self, kwargs):
        '''Generate an AudioPlay screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['music_library'] = self.music_library
        return AudioPlay(**kwargs)

    def _generate_disc(self, kwargs):
        '''Generate a Disc screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['music_library'] = self.music_library
        return Disc(**kwargs)

    def _generate_main(self, kwargs):
        '''Generate a Main screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        return Main(**kwargs)

    def _generate_movie(self, kwargs):
        '''Generate a Movie screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        return Movie(**kwargs)

    def _generate_music(self, kwargs):
        '''Generate a Music screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        kwargs['music_library'] = self.music_library
        return Music(**kwargs)

    def _generate_photo_albums(self, kwargs):
        '''Generate a PhotoAlbums screen.'''
        kwargs['image_library'] = self.image_library
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        return PhotoAlbums(**kwargs)

    def _generate_photo(self, kwargs):
        '''Generate a Photo screen.'''
        return Photo(**kwargs)

    def _generate_photographs(self, kwargs):
        '''Generate a Photographs screen.'''
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        return Photographs(**kwargs)

    def _generate_question(self, kwargs):
        '''Generate a Question screen.'''
        kwargs['move_to_previous_screen_callback'] = \
            self.move_to_previous_screen_callback
        return Question(**kwargs)

    def _generate_tv_series(self, kwargs):
        '''Generate a TvSeries screen.'''
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        kwargs['video_library'] = self.video_library
        return TvSeries(**kwargs)

    def _generate_tv_episodes(self, kwargs):
        '''Generate a TvEpisodes screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        return TvEpisodes(**kwargs)

    def _generate_video(self, kwargs):
        '''Generate a Video screen.'''
        kwargs['media_player'] = self.media_player
        kwargs['move_to_new_screen_callback'] = self.move_to_new_screen_callback
        kwargs['video_library'] = self.video_library
        return Video(**kwargs)

    def _generate_video_osd(self, kwargs):
        '''Generate a VideoOSD screen.'''
        kwargs['media_player'] = self.media_player
        return VideoOSD(**kwargs)

    def _generate_weather(self, kwargs):
        '''Generate a WeatherScreen screen.'''
        return WeatherScreen(**kwargs)

