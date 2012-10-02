# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Test mock objects'''
# pylint: disable-msg=W0231

import os

import gobject

from entertainerlib.client.medialibrary.images import Image, ImageLibrary
from entertainerlib.client.medialibrary.music import MusicLibrary
from entertainerlib.client.medialibrary.videos import (Movie, TVEpisode,
    TVSeries, VideoLibrary)

THIS_DIR = os.path.dirname(__file__)

class MockClutterKeyboardEvent(object):
    '''Mock clutter keyboard events'''

    def __init__(self, key_value):
        # Must match binding property name
        self._keyval = key_value

    @property
    def keyval(self):
        '''Simulate the key value stored in a clutter keyboard event.'''
        return self._keyval


class MockImage(Image):
    '''Mock entertainerlib.client.medialibrary.images.Image'''

    def __init__(self, filename=None, album_path=None, title=None,
        description=None, date=None, time=None, width=None, height=None,
        filesize=None, thumb_hash=None):
        self._Image__description = 'What a terrible image'
        self._Image__filename = filename
        self._Image__title = 'A title'

    def get_thumbnail_url(self):
        '''See `Image.get_thumbnail_url`.'''
        return THIS_DIR + '/data/ImageThumbnailer/test.jpg'


class MockImageLibrary(ImageLibrary):
    '''Mock entertainerlib.client.medialibrary.images.ImageLibrary'''

    def __init__(self):
        '''Override the intial behavior.'''

    def get_number_of_albums(self):
        '''See `ImageLibrary.get_number_of_albums`.'''
        return 0


class MockMediaPlayer(gobject.GObject, object):
    '''Mock entertainerlib.client.media_player.MediaPlayer'''
    __gsignals__ = {
        'play' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'pause' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'stop' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'skip-forward' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'skip-backward' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'position-changed' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'refresh' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        }

    def __init__(self, stage=None, width=None, height=None):
        '''Override any actual media player set up.'''
        gobject.GObject.__init__(self)
        self.is_playing = False

    def has_media(self):
        '''See `MediaPlayer.has_media`.'''
        return False

    def play(self):
        '''See `MediaPlayer.play`.'''

    def set_media(self, playable=None, internal_call=False):
        '''See `MediaPlayer.set_media`.'''


class MockMovie(Movie):
    '''Mock entertainerlib.client.medialibrary.videos.Movie'''

    def __init__(self, filename=None):
        self.actors = ['Tim Robbins']
        self.directors = ['Frank Darabont']
        self.genres = ['Drama']
        self.plot = 'An innocent man is sent to prison'
        self.rating = 5
        self.runtime = ''
        self.title = 'The Shawshank Redemption'
        self.writers = ['Frank Darabont']
        self.year = 1994

    def has_cover_art(self):
        '''See `Movie.has_cover_art`.'''
        return False

class MockMusicLibrary(MusicLibrary):
    '''Mock entertainerlib.client.medialibrary.music.MusicLibrary'''

    def __init__(self):
        '''Override the intial behavior.'''

    def get_albums_by_artist(self, artist=None):
        '''See `MusicLibrary.get_albums_by_artist`.'''
        return []

    def get_compact_disc_information(self):
        '''See `MusicLibrary.get_compact_disc_information`.
        Raise an exception to simulate no disc.'''
        raise Exception('No disc in drive')

    def get_tracks_by_artist(self, artist=None):
        '''See `MusicLibrary.get_tracks_by_artist`.'''
        return []

    def number_of_tracks(self):
        '''See `MusicLibrary.number_of_tracks`.'''
        return 0

    def __del__(self):
        '''See `MusicLibrary.__del__`.'''


class MockTVEpisode(TVEpisode):
    '''Mock entertainerlib.client.medialibrary.videos.TVEpisode'''

    def __init__(self, title=None):
        '''Override init to prevent a database connection'''
        self.number = 1
        self.title = 'Something clever'
        self.plot = 'Dr. House continues to be a jerk'

    @property
    def thumbnail_url(self):
        '''Thumbnail URL getter.'''
        return None

class MockTVSeries(TVSeries):
    '''Mock entertainerlib.client.medialibrary.videos.TVSeries'''

    def __init__(self, title=None):
        '''Override init to prevent a database connection'''
        self.seasons = []
        self.title = 'House'

    def has_cover_art(self):
        '''See `TVSeries.has_cover_art`.'''
        return False

class MockVideoLibrary(VideoLibrary):
    '''Mock entertainerlib.client.medialibrary.videos.VideoLibrary'''

    def __init__(self):
        '''Override the intial behavior.'''

    def __del__(self):
        '''Override the delete behavior.'''

    def get_number_of_movies(self):
        '''See `VideoLibrary.get_number_of_movies`.'''
        return 0

    def get_number_of_tv_series(self):
        '''See `VideoLibrary.get_number_of_tv_series`.'''
        return 0

    def get_number_of_video_clips(self):
        '''See `VideoLibrary.get_number_of_video_clips`.'''
        return 0


class MockPointerEvent(object):
    '''Mock a pointer event like those generated by Clutter'''

    def __init__(self):
        self.x = 0
        self.y = 0
        self.time = 0

