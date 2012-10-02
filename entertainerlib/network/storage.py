# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Base class for a Storage implementation.'''


class Storage(object):
    '''Base Storage class.'''

    @property
    def music_tracks(self):
        '''Return a list of all music tracks.'''
        raise NotImplementedError

    @property
    def music_albums(self):
        '''Return a list of all music tracks.'''
        raise NotImplementedError

    @property
    def photo_albums(self):
        '''Return a list of all music tracks.'''
        raise NotImplementedError

    @property
    def photo_images(self):
        '''Return a list of all music tracks.'''
        raise NotImplementedError

    @property
    def video_files(self):
        '''Return a list of all music tracks.'''
        raise NotImplementedError

    @property
    def video_series(self):
        '''Return a list of all music tracks.'''
        raise NotImplementedError


