# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Thumbnailer tests.'''
# pylint: disable-msg=W0212

import os

from entertainerlib.exceptions import ThumbnailerException
from entertainerlib.tests import EntertainerTest
from entertainerlib.thumbnailer import (ImageThumbnailer, Thumbnailer,
    VideoThumbnailer)

THIS_DIR = os.path.dirname(__file__)


class ThumbnailerTest(EntertainerTest):
    '''Test the thumbnailer abstract class'''

    def setUp(self):
        '''See unittest.TestCase'''
        EntertainerTest.setUp(self)
        self.debug = False

    def tearDown(self):
        """Clean up after the test"""
        EntertainerTest.tearDown(self)

    def testValidThumbnailType(self):
        '''Test creating thumbnails with a valid type'''
        thumbnailer_image = Thumbnailer(
            THIS_DIR + '/data/ImageThumbnailer/test.jpg', 'image')
        self.assertTrue(isinstance(thumbnailer_image, Thumbnailer))

        thumbnailer_video = Thumbnailer(
            THIS_DIR + '/data/VideoThumbnailer/test.avi', 'video')
        self.assertTrue(isinstance(thumbnailer_video, Thumbnailer))

    def testInvalidThumbnailType(self):
        '''Test creating thumbnails with an invalid type'''
        self.assertRaises(ThumbnailerException, Thumbnailer,
            THIS_DIR + '/data/ImageoThumbnailer/test.jpg', 'alskdjfhg')

    def testValidFileToThumbnail(self):
        '''Test image file thumbnailing'''
        thumbnailer_image = Thumbnailer(
            THIS_DIR + '/data/ImageThumbnailer/test.jpg', 'image')
        self.assertTrue(isinstance(thumbnailer_image, Thumbnailer))

    def testInvalidFileToThumbnail(self):
        '''Test thumbnailing of a non-existent file'''
        self.assertRaises(ThumbnailerException, Thumbnailer,
            THIS_DIR + '/data/ImageThumbnailer/alskdjfhg.jpg',
            'image')

    def testAbstractCreateThumbnailer(self):
        '''Tests trying to create the abstract thumbnailer'''
        thumbnailer_test = Thumbnailer(
            THIS_DIR + '/data/ImageThumbnailer/test.jpg', 'image')
        self.assertRaises(Exception, thumbnailer_test.create_thumbnail)


class ImageThumbnailerTest(EntertainerTest):
    '''Test ImageThumbnailer'''

    def setUp(self):
        """See unittest.TestCase"""
        EntertainerTest.setUp(self)
        self.debug = False
        self.filename = (
            THIS_DIR + '/data/ImageThumbnailer/test.jpg')

    def tearDown(self):
        """Clean up after the test"""
        EntertainerTest.tearDown(self)

    def testThumbnailer(self):
        '''Tests the creation a file'''
        thumbnailer = ImageThumbnailer(self.filename)
        thumbnailer.create_thumbnail()
        if self.debug:
            print 'Expecting thumbnail : %s' % thumbnailer._thumb_file
        self.assertTrue(os.path.exists(thumbnailer._thumb_file))


class VideoThumbnailerTest(EntertainerTest):
    '''Tests VideoThumbnailer'''

    def setUp(self):
        """See unittest.TestCase"""
        EntertainerTest.setUp(self)
        self.debug = False

    def tearDown(self):
        """Clean up after the test"""
        EntertainerTest.tearDown(self)

    def testThumbnailerConstructor(self):
        '''Tests instantiation of thumbnailer class'''
        self.thumbnailer = VideoThumbnailer(
            THIS_DIR + '/data/VideoThumbnailer/test.avi', src='video')
        self.assertTrue(isinstance(self.thumbnailer, VideoThumbnailer))

    def testThumbnailerConstructorFilenameIsFolder(self):
        '''Tests proper handling of folders instead of files'''
        self.assertRaises(ThumbnailerException,
            VideoThumbnailer, os.path.abspath('.'))

    def testThumbnailerConstructorFilenameExists(self):
        '''Tests existence of file to thumbnail'''
        self.assertRaises(ThumbnailerException,
            VideoThumbnailer, os.path.abspath('foo-bar-baz'))

    def testThumbnailerConstructorSrc(self):
        '''Tests valid source types'''
        self.assertRaises(ThumbnailerException,
            VideoThumbnailer, os.path.abspath('.') +
            '/data/VideoThumbnailer/test.avi', src="foo")

    def testThumbnailAvi(self):
        '''Tests thumbnailing of Avi file'''
        thumbnailer = VideoThumbnailer(
            THIS_DIR + '/data/VideoThumbnailer/test.avi', src='video')
        if os.path.exists(thumbnailer._thumb_file):
            os.remove(thumbnailer._thumb_file)
        thumbnailer.create_thumbnail()
        if self.debug:
            print 'Expecting thumbnail : %s' % (self.thumbnailer._thumb_file)
        self.assertTrue(os.path.exists(thumbnailer._thumb_file))

    def testThumbnailFlv(self):
        '''Tests thumbnailing of a flash file'''
        thumbnailer = VideoThumbnailer(
            THIS_DIR + '/data/VideoThumbnailer/test.avi', src='video')
        if os.path.exists(thumbnailer._thumb_file):
            os.remove(thumbnailer._thumb_file)
        thumbnailer.create_thumbnail()
        if self.debug:
            print 'Expecting thumbnail : %s' % (self.thumbnailer._thumb_file)
        self.assertTrue(os.path.exists(thumbnailer._thumb_file))

