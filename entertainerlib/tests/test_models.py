# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests for all models'''

from storm.locals import Store

from entertainerlib.db import models
from entertainerlib.tests import EntertainerTestWithDatabase


class ModelTestCase(EntertainerTestWithDatabase):
    '''Abstract Model Test Case

    The parent class of all model test classes.
    '''

    def setUp(self):
        EntertainerTestWithDatabase.setUp(self)


class TestBaseModel(ModelTestCase):
    '''BaseModel test case.'''


class TestPhotoAlbum(ModelTestCase):
    '''PhotoAlbum test case'''

    def testCreate(self):
        '''Test creation of new PhotoAlbum'''

        store = Store(self.db)
        photoalbum = models.PhotoAlbum()
        photoalbum.title = u'Photo Album Title'
        photoalbum.description = u'This is a photo description'
        store.add(photoalbum)
        store.commit()

        self.assertTrue(Store.of(photoalbum) is store)

        photoalbum_from_database = store.find(models.PhotoAlbum,
            models.PhotoAlbum.title == u'Photo Album Title').one()
        self.assertTrue(photoalbum is photoalbum_from_database)


class TestPhotoImage(ModelTestCase):
    '''PhotoImage test case'''

    def testCreate(self):
        '''Test creation of new PhotoImage'''

        store = Store(self.db)
        photoimage = models.PhotoImage()
        photoimage.filename = u'/home/user/photo.jpg'
        store.add(photoimage)
        store.commit()

        self.assertTrue(Store.of(photoimage) is store)

        photoimage_from_database = store.find(models.PhotoImage,
            models.PhotoImage.filename == u'/home/user/photo.jpg').one()
        self.assertTrue(photoimage is photoimage_from_database)


class TestMusicAlbum(ModelTestCase):
    '''MusicAlbum test case'''

    def testCreate(self):
        '''Test creation of new MusicAlbum'''

        store = Store(self.db)
        musicalbum = models.MusicAlbum()
        musicalbum.title = u'The Lady Dance'
        store.add(musicalbum)
        store.commit()

        self.assertTrue(Store.of(musicalbum) is store)

        musicalbum_from_database = store.find(models.MusicAlbum,
            models.MusicAlbum.title == u'The Lady Dance').one()
        self.assertTrue(musicalbum is musicalbum_from_database)


class TestMusicTrack(ModelTestCase):
    '''MusicTrack test case'''

    def testCreate(self):
        '''Test creation of new MusicTrack'''

        store = Store(self.db)
        musictrack = models.MusicTrack()
        musictrack.title = u'The Beautiful Ones'
        store.add(musictrack)
        store.commit()

        self.assertTrue(Store.of(musictrack) is store)

        musictrack_from_database = store.find(models.MusicTrack,
            models.MusicTrack.title == u'The Beautiful Ones').one()
        self.assertTrue(musictrack is musictrack_from_database)


class TestMusicPlaylist(ModelTestCase):
    '''MusicPlaylist test case'''

    def testCreate(self):
        '''Test creation of new MusicPlaylist'''

        store = Store(self.db)
        musicplaylist = models.MusicPlaylist()
        musicplaylist.title = u'The Ultimate Heavy Metal Goth Emo'
        store.add(musicplaylist)
        store.commit()

        self.assertTrue(Store.of(musicplaylist) is store)

        musicplaylist_from_database = store.find(models.MusicPlaylist,
            models.MusicPlaylist.title == \
                u'The Ultimate Heavy Metal Goth Emo').one()
        self.assertTrue(musicplaylist is musicplaylist_from_database)


class TestVideoFile(ModelTestCase):
    '''VideoFile test case'''

    def testCreate(self):
        '''Test creation of new VideoFile'''

        store = Store(self.db)
        videofile = models.VideoFile()
        videofile.filename = u'/home/user/foo.mpg'
        store.add(videofile)
        store.commit()

        self.assertTrue(Store.of(videofile) is store)

        videofile_from_database = store.find(models.VideoFile,
            models.VideoFile.filename == u'/home/user/foo.mpg').one()
        self.assertTrue(videofile is videofile_from_database)


