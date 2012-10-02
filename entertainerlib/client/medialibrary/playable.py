# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Playable - Interface for playable streams. MediaPlayer plays Playables'''

class Playable(object):
    '''An interface for all objects that can be played with the MediaPlayer.
    MediaPlayer playes only files that implement this interface.'''

    VIDEO_STREAM = 0
    AUDIO_STREAM = 1

    def get_uri(self):
        '''Get the URI.'''
        return None

    def get_type(self):
        '''Get the type (as defined by the Playable constants.'''
        return None

    def get_title(self):
        '''Get the title.'''
        return None

