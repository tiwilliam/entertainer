# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Test the Storage classes.'''
# pylint: disable-msg=W0704,W0612
from entertainerlib.network.storage import Storage
from entertainerlib.tests import EntertainerTest

class TestStorage(EntertainerTest):
    '''Test for entertainerlib.storage.base.Storage.'''

    def test_create(self):
        '''Test the instantiation of a Storage object.'''
        storage = Storage()
        self.assertTrue(isinstance(storage, Storage))

    def test_not_implemented(self):
        '''Test the calls to the various methods raise NotImplementedError.'''
        storage = Storage()

        # The try/except blocks are used instead of assertRaises because these
        # attributes are not callable.
        try:
            albums = storage.music_albums
            self.fail()
        except NotImplementedError:
            pass

        try:
            tracks = storage.music_tracks
            self.fail()
        except NotImplementedError:
            pass

        try:
            albums = storage.photo_albums
            self.fail()
        except NotImplementedError:
            pass

        try:
            images = storage.photo_images
            self.fail()
        except NotImplementedError:
            pass

        try:
            videos = storage.video_files
            self.fail()
        except NotImplementedError:
            pass

        try:
            series = storage.video_series
            self.fail()
        except NotImplementedError:
            pass

