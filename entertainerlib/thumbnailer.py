# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Thumbnailer classes for image and video.'''
# pylint: disable-msg=C0301

import os
from threading import Event
import hashlib

import gobject
import gst
import Image
import ImageStat

from entertainerlib.exceptions import (ImageThumbnailerException,
    ThumbnailerException, VideoThumbnailerException)
from entertainerlib.configuration import Configuration


class Thumbnailer(object):
    '''Thumbnailer base class for video and image thumbnailers.'''

    MAX_SIZE = 512
    THUMB_QUALITY = 85

    def __init__(self, filename, thumb_type):

        self.config = Configuration()
        thumb_dir = os.path.join(self.config.THUMB_DIR, thumb_type)
        self.filename = filename
        filehash = hashlib.md5()
        filehash.update(self.filename)
        self.filename_hash = filehash.hexdigest()

        if not os.path.exists(self.filename):
            raise ThumbnailerException(
                'File to thumbnail does not exist : %s' % self.filename)

        if os.path.exists(thumb_dir):
            if os.path.isfile(filename):
                self._thumb_file =  os.path.join(thumb_dir,
                    self.filename_hash + '.jpg')
            else:
                raise ThumbnailerException(
                    'Thumbnailer filename is a folder : %s' % self.filename)
        else:
            raise ThumbnailerException('Unknown thumbnail type : %s' % (
                thumb_type))

    def get_hash(self):
        '''Get the hash of the filename'''
        return self.filename_hash

    def create_thumbnail(self):
        """
        Implement this method in deriving classes.

        Method should create a new thumbnail and save it to the Entertainer's
        thumbnail directory in JPEG format. Thumbnail filename should be a MD5
        hash of the absolute path of the original file.
        """
        raise NotImplementedError


class ImageThumbnailer(Thumbnailer):
    """Thumbnailer for image files."""

    def __init__(self, filename):
        """Create a new Image thumbnailer"""
        Thumbnailer.__init__(self, filename, 'image')
        try:
            self.im = Image.open(self.filename)
        except:
            raise ImageThumbnailerException(
                'Error while opening file : %s' % self.filename)


    def create_thumbnail(self):
        """
        Method creates a new thumbnail and saves it to the Entertainer's
        thumbnail directory in PNG format. Thumbnail filename is a MD5
        hash of the given filename.
        """

        # Calculate new size here
        original_width = self.im.size[0]
        original_height = self.im.size[1]
        if original_width <= self.MAX_SIZE and (
            original_height <= self.MAX_SIZE):
            try:
                self.im.save(self._thumb_file, "JPEG",
                    quality=self.THUMB_QUALITY)
            except:
                raise ImageThumbnailerException('Error saving thumbnail')

        else:
            if original_width > original_height:
                width = self.MAX_SIZE
                height = (width * original_height) / original_width
            else:
                height = self.MAX_SIZE
                width = (height * original_width) / original_height
            try:
                self.im.thumbnail((width, height), Image.ANTIALIAS)
                self.im.save(self._thumb_file, "JPEG",
                    quality=self.THUMB_QUALITY)
            except:
                raise ImageThumbnailerException('Error saving thumbnail')


class VideoThumbnailer(Thumbnailer):
    '''Create thumbnails from videos.'''
    # I think it's important to note that the methodology of this code (and
    # some actual EXACT snippets of code) were based on Elisa
    # (http://elisa.fluendo.com/)


    class VideoSinkBin(gst.Bin):
        '''A gstreamer sink bin'''

        def __init__(self, needed_caps):
            self.reset()
            gst.Bin.__init__(self)
            self._capsfilter = gst.element_factory_make(
                'capsfilter', 'capsfilter')

            self.set_caps(needed_caps)
            self.add(self._capsfilter)

            fakesink = gst.element_factory_make('fakesink', 'fakesink')
            fakesink.set_property("sync", False)
            self.add(fakesink)
            self._capsfilter.link(fakesink)

            pad = self._capsfilter.get_pad("sink")
            ghostpad = gst.GhostPad("sink", pad)

            pad2probe = fakesink.get_pad("sink")
            pad2probe.add_buffer_probe(self.buffer_probe)

            self.add_pad(ghostpad)
            self.sink = self._capsfilter

        def set_current_frame(self, value):
            '''Set the current frame'''
            self._current_frame = value

        def set_caps(self, caps):
            '''Set the bin caps'''
            gst_caps = gst.caps_from_string(caps)
            self._capsfilter.set_property("caps", gst_caps)

        def get_current_frame(self):
            '''Gets the current frame'''
            frame = self._current_frame
            self._current_frame = None
            return frame

        def buffer_probe(self, pad, buff):
            '''Buffer the probe'''
            caps = buff.caps
            if caps != None:
                s = caps[0]
                self.width = s['width']
                self.height = s['height']
            if self.width != None and self.height != None and buff != None:
                self.set_current_frame(buff.data)
            return True

        def reset(self):
            '''Reset the bin'''
            self.width = None
            self.height = None
            self.set_current_frame(None)


    def __init__(self, filename, src="video"):

        Thumbnailer.__init__(self, filename, src)
        self._fileuri = 'file://%s' % (self.filename)

        #Initialize and use the gstreamer pipeline
        self._pipeline = gst.element_factory_make('playbin', 'playbin')
        self._sink = self.VideoSinkBin('video/x-raw-rgb,bpp=24,depth=24')
        self._blocker = Event()
        self._pipeline.set_property('video-sink', self._sink)
        self._pipeline.set_property('volume', 0)


        self.BORING_THRESHOLD = 2000
        self.HOLES_SIZE = (9, 35)
        self.HOLES_DATA = '\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x9a\x9a\x9a\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x91\x91\x91\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x9a\x9a\x9a\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x91\x91\x91\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x9a\x9a\x9a\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x91\x91\x91\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x9a\x9a\x9a\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x91\x91\x91\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x9a\x9a\x9a\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x91\x91\x91\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\xff\xff\xff\xa6\x91\x91\x91\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6\x00\x00\x00\xa6'

    def add_holes(self, img):
        '''Add the holes image'''
        holes = Image.fromstring('RGBA', self.HOLES_SIZE, self.HOLES_DATA)
        holes_h = holes.size[1]
        remain = img.size[1] % holes_h

        i = 0
        nbands = 0
        while i < (img.size[1] - remain):
            left_box = (0, i, holes.size[0], (nbands+1) * holes.size[1])
            img.paste(holes, left_box)

            right_box = (img.size[0] - holes.size[0], i,
                         img.size[0], (nbands+1) * holes.size[1])
            img.paste(holes, right_box)

            i += holes_h
            nbands += 1

        remain_holes = holes.crop((0, 0, holes.size[0], remain))
        remain_holes.load()
        img.paste(remain_holes, (0, i, holes.size[0], img.size[1]))
        img.paste(remain_holes, (img.size[0] - holes.size[0], i,
                                 img.size[0], img.size[1]))
        return img

    def interesting_image(self, img):
        '''
        Checks an image to see if it has the characteristics of an
        'interesting' image, i.e. whether or not the image is worth
        examining for thumbnailing
        '''
        stat = ImageStat.Stat(img)
        return True in [ i > self.BORING_THRESHOLD for i in stat.var ]

    def set_pipeline_state(self, pipeline, state):
        '''
        Does exactly what it claims : sets the state of the pipeline, and
        returns the boolean value of whether or not is successfully changed
        state
        '''
        status = pipeline.set_state(state)
        if status == gst.STATE_CHANGE_ASYNC:

            result = [False]
            max_try = 100
            nb_try = 0
            while not result[0] == gst.STATE_CHANGE_SUCCESS:
                if nb_try > max_try:
                    #State change failed
                    return False
                nb_try += 1
                result = pipeline.get_state(50*gst.MSECOND)

            return True
        elif status == gst.STATE_CHANGE_SUCCESS:
            return True
        else:
            return False


    def create_thumbnail(self):
        '''
        Creates the new thumbnail based on the information provided through the
        gstreamer API.  The file is an md5 of the video's file name, followed
        by the .jpg extension
        '''

        if os.path.exists(self._thumb_file):
            return

        self.set_pipeline_state(self._pipeline, gst.STATE_NULL)
        self._pipeline.set_property('uri', self._fileuri)

        if not self.set_pipeline_state(self._pipeline, gst.STATE_PAUSED):
            self.set_pipeline_state(self._pipeline, gst.STATE_NULL)
            raise VideoThumbnailerException('Cannot start the pipeline')

        if self._sink.width == None or self._sink.height == None:
            self.set_pipeline_state(self._pipeline, gst.STATE_NULL)
            raise VideoThumbnailerException('Unable to determine media size')
        sink_size = (self._sink.width, self._sink.height)

        try:
            duration = self._pipeline.query_duration(gst.FORMAT_TIME)[0]
        except AssertionError:
            #Gstreamer cannot determine the media duration using
            #playing-thumbnailing for file
            self.set_pipeline_state(self._pipeline, gst.STATE_NULL)

            img = self._play_for_thumb(sink_size, 0)
            if img:
                img.save(self._thumb_file)
                return
        else:
            duration /= gst.NSECOND
            try:
                img = self._seek_for_thumb(duration, sink_size)
                #Seek found image
                if img:
                    img.save(self._thumb_file)
                    return
            except VideoThumbnailerException:
                #Fallback: No Image found in seek_for, falling back to
                #play_for_thumb
                self.set_pipeline_state(self._pipeline, gst.STATE_NULL)
                img = self._play_for_thumb(sink_size, duration)
                #Fallback-Play found img
                if img:
                    img.save(self._thumb_file)
                    return

        self.set_pipeline_state(self._pipeline, gst.STATE_NULL)
        raise VideoThumbnailerException(
            'Unable to create thumbnail.  Please file a bug')


    def _play_for_thumb(self, sink_size, duration=0):
        '''
        Plays the video file to gather information for generating a thumbnail
        '''
        self._img = None

        if duration >= 250000:
            self._every = 25
        elif duration >= 200000:
            self._every = 15
        elif duration >= 10000:
            self._every = 10
        elif duration >= 5000:
            self._every = 5
        else:
            self._every = 1

        #Setting every-frame to self._every

        self._every_co = self._every

        ## How often Proceed?
        self._counter = 5

        self.set_state_blocking(self._pipeline, gst.STATE_PLAYING)

        self._blocker.wait()
        self._pipeline.set_state(gst.STATE_NULL)
        return self._img

    def _seek_for_thumb(self, duration, sink_size):
        '''
        Seeks through the video file to gather information for generating a
        thumbnail
        '''
        frame_locations = [ 1.0 / 3.0, 2.0 / 3.0, 0.1, 0.9, 0.5 ]

        for location in frame_locations:
            abs_location = int(location * duration)

            if abs_location == 0:
                raise VideoThumbnailerException(
                    self.filename, 'Video has a size of zero')

            event = self._pipeline.seek(1.0, gst.FORMAT_TIME,
                gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT,
                gst.SEEK_TYPE_SET, abs_location,
                gst.SEEK_TYPE_NONE, 0)
            if not event:
                raise VideoThumbnailerException(self.filename,
                    'Unable to seek through video')

            if not self.set_pipeline_state(self._pipeline, gst.STATE_PAUSED):
                raise VideoThumbnailerException(self.filename,
                    'Unable to pause video')

            frame = self._sink.get_current_frame()

            img = Image.frombuffer(
                "RGB", sink_size, frame, "raw", "RGB", 0, 1)

            if self.interesting_image(img):
                break
            else:
                pass

        self._sink.reset()

        if img:
            img.thumbnail((self.MAX_SIZE, self.MAX_SIZE), Image.BILINEAR)
            if img.mode != 'RGBA':
                img = img.convert(mode='RGBA')
            self.set_pipeline_state(self._pipeline, gst.STATE_NULL)
            return img

gobject.type_register(VideoThumbnailer.VideoSinkBin)
