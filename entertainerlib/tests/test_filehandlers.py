'''Tests for entertainerlib.indexing.handlers.'''
# pylint: disable-msg=W0212
import os

from storm.locals import Store

from entertainerlib.configuration import Configuration
from entertainerlib.db import models
from entertainerlib.indexing import handlers
from entertainerlib.tests import EntertainerTest


class TestFileHandler(EntertainerTest):

    handler = handlers.FileHandler
    filename = '/foo/bar'

    def setUp(self):
        EntertainerTest.setUp(self)
        self.filename = unicode(os.path.join(self.data_dir, self.filename))

    def test_constructor(self):
        '''Test the file handler constructor.'''
        handler = self.handler()
        self.assertTrue(isinstance(handler.configuration, Configuration))
        self.assertTrue(isinstance(handler._store, Store))

    def test_callable(self):
        '''Test that the handler is correctly callable.'''
        handler = self.handler()
        self.assertRaises(NotImplementedError, handler, self.filename)


class TestAviHandler(TestFileHandler):
    '''Tests for the AviHandler.'''

    handler = handlers.AviHandler
    filename = 'VideoThumbnailer/test.avi'

    def test_callable(self):
        '''See `TestFileHandler.test_callable`.'''
        handler = self.handler()
        video = handler(self.filename)
        self.assertTrue(os.path.exists(
            os.path.join(
                handler.configuration.THUMB_DIR,
                video.thumbnail)))
        self.assertEqual(video.filename, self.filename)

    def test_update_existing_record(self):
        '''Existing records should be updated.'''
        handler = self.handler()
        _video = handler(self.filename)
        videos = Store.of(_video).find(models.VideoFile,
            models.VideoFile.filename == self.filename)
        self.assertEqual(videos.count(), 1)

        _video = handler(self.filename)
        videos = Store.of(_video).find(models.VideoFile,
            models.VideoFile.filename == self.filename)
        self.assertEqual(videos.count(), 1)

    def test_query(self):
        '''Test that the file can be queried for.'''
        handler = self.handler()
        _video = handler(self.filename)
        video = Store.of(_video).find(models.VideoFile,
            models.VideoFile.filename == self.filename).one()
        self.assertTrue(os.path.exists(
            os.path.join(
                handler.configuration.THUMB_DIR,
                video.thumbnail)))
        self.assertEqual(video.filename, self.filename)


class TestJpegHandler(TestFileHandler):
    '''Tests for the JpegHandler.'''

    handler = handlers.JpegHandler
    filename = 'ImageThumbnailer/test.jpg'

    def test_callable(self):
        '''See `TestFileHandler.test_callable`.'''
        handler = self.handler()
        image = handler(self.filename)
        self.assertTrue(os.path.exists(
            os.path.join(
                handler.configuration.THUMB_DIR,
                image.thumbnail)))
        self.assertEqual(image.filename, self.filename)

    def test_update_existing_record(self):
        '''Existing records should be updated.'''
        handler = self.handler()
        _image = handler(self.filename)
        images = Store.of(_image).find(models.PhotoImage,
            models.PhotoImage.filename == self.filename)
        self.assertEqual(images.count(), 1)

        _image = handler(self.filename)
        images = Store.of(_image).find(models.PhotoImage,
            models.PhotoImage.filename == self.filename)
        self.assertEqual(images.count(), 1)

    def test_query(self):
        '''Test that the file can be queried for.'''
        handler = self.handler()
        _image = handler(self.filename)
        image = Store.of(_image).find(models.PhotoImage,
            models.PhotoImage.filename == self.filename).one()
        self.assertTrue(os.path.exists(
            os.path.join(
                handler.configuration.THUMB_DIR,
                image.thumbnail)))
        self.assertEqual(image.filename, self.filename)


class TestMp3Handler(TestFileHandler):
    '''Tests for the JpegHandler.'''

    handler = handlers.Mp3Handler
    filename = 'test.mp3'

    def test_callable(self):
        '''See `TestFileHandler.test_callable`.'''
        handler = self.handler()
        mp3 = handler(self.filename)
        self.assertEqual(mp3.filename, self.filename)
        self.assertEqual(mp3.comment, u'This is a comment')
        self.assertEqual(mp3.lyrics, u'')
        self.assertEqual(mp3.title, u'Flightless Bird, American Mouth')
        self.assertEqual(mp3.tracknumber, 12)
        self.assertEqual(mp3.album.title, u'The Shephard\'s Dog')
        self.assertEqual(mp3.album.artist, u'Iron and Wine')
        self.assertEqual(mp3.album.genre, u'Gangster Rap')

    def test_update_existing_record(self):
        '''The same file should not be indexed twice, but updated.'''
        handler = self.handler()
        _mp3 = handler(self.filename)
        mp3 = Store.of(_mp3).find(models.MusicTrack,
            models.MusicTrack.filename == self.filename).one()
        mp3.comment = u'Foo bar baz'
        Store.of(mp3).commit()

        _mp3 = handler(self.filename)
        files = Store.of(_mp3).find(models.MusicTrack,
            models.MusicTrack.filename == self.filename)
        self.assertEqual(files.count(), 1)
        self.assertEqual(files.one().comment, u'This is a comment')

    def test_query(self):
        '''Test that the file can be queried for.'''
        handler = self.handler()
        _mp3 = handler(self.filename)
        mp3 = Store.of(_mp3).find(models.MusicTrack,
            models.MusicTrack.filename == self.filename).one()
        self.assertEqual(mp3.filename, self.filename)
        self.assertEqual(mp3.comment, u'This is a comment')
        self.assertEqual(mp3.lyrics, u'')
        self.assertEqual(mp3.title, u'Flightless Bird, American Mouth')
        self.assertEqual(mp3.tracknumber, 12)
        self.assertEqual(mp3.album.title, u'The Shephard\'s Dog')
        self.assertEqual(mp3.album.artist, u'Iron and Wine')
        self.assertEqual(mp3.album.genre, u'Gangster Rap')

