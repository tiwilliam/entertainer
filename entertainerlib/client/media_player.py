# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''MediaPlayer - MediaPlayer that plays audio and video streams.'''

# import order is important here since Clutter 0.8,
# see the pyclutter README for details

import cluttergst
import clutter
import gobject
import gst

from entertainerlib.gui.widgets.motion_buffer import MotionBuffer
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.client.medialibrary.playable import Playable
from entertainerlib.logger import Logger

class MediaPlayer(gobject.GObject, object):
    '''MediaPlayer uses Gstreamer to play all video and audio files. Entertainer
    has only one MediaPlayer object at runtime. MediaPlayer can play objects
    that implement Playable interface.'''

    __gsignals__ = {
        'play' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'pause' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'stop' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'skip-forward' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'skip-backward' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'volume_changed' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'position-changed' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'refresh' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        }

    # Ratio constants
    NATIVE = 0
    WIDESCREEN = 1
    NORMAL = 2
    LETTER_BOX = 3
    ZOOM = 4
    INTELLIGENT = 5

    MODE_NONE = 0
    MODE_PLAYPAUSE = 1
    MODE_SEEK = 2

    def __init__(self, stage, width, height):
        gobject.GObject.__init__(self)

        self._motion_buffer = MotionBuffer()
        self._event_mode = self.MODE_NONE
        self._motion_handler = 0

        self.stage = stage               # Stage that displays textures
        # Stage background color when not playing
        self.bgcolor = stage.get_color()
        self.stage_width = width         # Stage width used for video resizing
        self.stage_height = height       # Stage height used for video resizing
        self.ratio = MediaPlayer.NATIVE  # Video texture ratio

        self.audio_skip_step = 10        # Audio skip step in seconds
        self.video_skip_step = 60        # Video skip step in seconds
        self.playlist = None             # Current play list
        self.media = None                # Current media (Playable object)
        self.shuffle = False             # Shuffle mode
        self.repeat = False              # Repeat mode
        self.is_playing = False          # Is media player currently playing
        self.is_reactive_allowed = False # Is the video_texture reactive

        self.logger = Logger().getLogger('client.MediaPlayer')

        self._internal_callback_timeout_key = None

        self.video_texture = cluttergst.VideoTexture()
        self.pipeline = self.video_texture.get_pipeline()
        self.pipeline.set_property("volume", 0.5)
        self._volume = 10
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self._on_gst_message)

        self.video_texture.set_reactive(True)
        self.video_texture.connect('size-change', self._on_size_change)
        self.video_texture.connect('scroll-event', self._on_scroll_event)
        self.video_texture.connect('button-press-event',
            self._on_button_press_event)
        self.video_texture.connect('button-release-event',
            self._on_button_release_event)

    def _on_gst_message(self, bus, message):
        '''
        Callback function that is called every time when message occurs on
        Gstreamer messagebus.
        '''
        if message.type == gst.MESSAGE_EOS:
            if self.media.get_type() == Playable.VIDEO_STREAM \
                or self.playlist is None:
                self.stop()
            else:
                self.next()
        elif message.type == gst.MESSAGE_ERROR:
            self.video_texture.set_playing(False)
            # XXX: laymansterms - I don't know the implications of removing the
            # position property.
            #self.video_texture.set_property("position", 0)
            err, debug = message.parse_error()
            self.logger.error("Error: %(err)s, %(debug)s" % \
                {'err': err, 'debug': debug})

    def _get_volume(self):
        """volume property getter."""
        return self._volume

    def _set_volume(self, volume):
        """volume property setter."""
        self._volume = volume
        if self._volume > 20:
            self._volume = 20
        if self._volume < 0:
            self._volume = 0
        self.pipeline.set_property("volume", self._volume / 20.0)
        self.emit('volume-changed')

    volume = property(_get_volume, _set_volume)

    def volume_up(self):
        """Increase player's volume level."""
        self.volume = self._volume + 1

    def volume_down(self):
        """Decrease player's volume level."""
        self.volume = self._volume - 1

    def set_playlist(self, playlist):
        '''Set new playlist to MediaPlayer.'''
        if len(playlist) == 0:
            raise Exception("Empty playlist is not allowed!")
        self.playlist = playlist
        self.set_media(self.playlist.get_current(), True)

    def get_playlist(self):
        '''Get current playlist.'''
        return self.playlist

    def set_media(self, playable, internal_call = False):
        '''
        Set media to media player. Media is an object that implements
        Playable interface. This media is played back when play() is called.
        '''
        # If this function is called from this object we don't set playlist
        # to None
        if not internal_call:
            self.playlist = None

        # If player is currently playing then we stop it
        if self.is_playing:
            self.stop()

        # Update media information
        self.media = playable

        # Set up media player for media
        if self.media.get_type() == Playable.AUDIO_STREAM \
            or self.media.get_type() == Playable.VIDEO_STREAM:
            self.video_texture.set_playing(False)
            self.video_texture.set_uri(playable.get_uri())
            # XXX: laymansterms - I don't know the implications of removing the
            # position property.
            #self.video_texture.set_property("position", 0)

    def get_media(self):
        '''Get URI of the current media stream.'''
        return self.media

    def has_media(self):
        '''
        Has media been set to this player. == has set_media() been called 
        before.
        '''
        if self.media is None:
            return False
        else:
            return True

    def get_media_type(self):
        '''Get the type of the current media.'''
        return self.media.get_type()

    def set_shuffle(self, boolean):
        '''
        Enable or disable shuffle play. When shuffle is enabled MediaPlayer picks
        a random Playable from the current playlist.
        '''
        self.shuffle = boolean

    def is_shuffle_enabled(self):
        '''Is shuffle enabled?'''
        return self.shuffle

    def set_repeat(self, boolean):
        '''
        Enable or disable repeat mode. When repeat is enabled the current
        playable is repeated forever.
        '''
        self.repeat = boolean

    def is_repeat_enabled(self):
        '''Is repeat enabled?'''
        return self.repeat

    def play(self):
        '''Play current media.'''
        # If current media is an audio file
        if not self.has_media():
            return

        if self.media.get_type() == Playable.AUDIO_STREAM:
            self.is_playing = True
            self.video_texture.set_playing(True)
            self.emit('play')

        # If current media is a video file
        elif self.media.get_type() == Playable.VIDEO_STREAM:
            if (self.video_texture.get_parent() == None):
                self.stage.add(self.video_texture)
            self.video_texture.lower_bottom()
            self.is_playing = True
            self.stage.set_color((0, 0, 0, 0))
            self.video_texture.set_playing(True)
            self.emit('play')

        if self._internal_callback_timeout_key is not None:
            gobject.source_remove(self._internal_callback_timeout_key)
        self._internal_callback_timeout_key = \
            gobject.timeout_add(200, self._internal_timer_callback)

    def pause(self):
        '''Pause media player.'''
        self.is_playing = False
        self.video_texture.set_playing(False)
        self.emit('pause')

    def stop(self):
        '''Stop media player.'''
        self.is_playing = False
        if self.media.get_type() == Playable.VIDEO_STREAM:
            self.stage.set_color(self.bgcolor)
            self.stage.remove(self.video_texture)
        self.video_texture.set_playing(False)
        # XXX: laymansterms - I don't know the implications of removing the
        # position property.
        #self.video_texture.set_property("position", 0)
        self.emit('stop')

        if self._internal_callback_timeout_key is not None:
            gobject.source_remove(self._internal_callback_timeout_key)

    def next(self):
        '''Play next track / video from current playlist.'''
        if self.playlist is not None:
            if self.shuffle:
                self.set_media(self.playlist.get_random(), True)
            elif self.playlist.has_next():
                self.set_media(self.playlist.get_next(), True)
            self.play()

    def previous(self):
        '''Play previous track / video from current playlist.'''
        if self.playlist is not None:
            if self.shuffle:
                self.set_media(self.playlist.get_random(), True)
            elif self.playlist.has_previous():
                self.set_media(self.playlist.get_previous(), True)
            self.play()

    def skip_forward(self):
        '''Skip media stream forward.'''
        if (self.media.get_type() == Playable.AUDIO_STREAM) or \
            (self.media.get_type() == Playable.VIDEO_STREAM):
            pos_int = self.pipeline.query_position(gst.FORMAT_TIME, None)[0]
            dur = self.pipeline.query_duration(gst.FORMAT_TIME, None)[0]
            seek_ns = pos_int + (self.audio_skip_step * 1000000000)
            if seek_ns > dur:
                seek_ns = dur
            self.pipeline.seek_simple(gst.FORMAT_TIME,
                                     gst.SEEK_FLAG_FLUSH,
                                     seek_ns)
            self.emit('skip-forward')

    def skip_backward(self):
        '''Skip media stream backward.'''
        if (self.media.get_type() == Playable.AUDIO_STREAM) or \
            (self.media.get_type() == Playable.VIDEO_STREAM):
            pos_int = self.pipeline.query_position(gst.FORMAT_TIME, None)[0]
            seek_ns = pos_int - (self.audio_skip_step * 1000000000)
            if seek_ns < 0:
                seek_ns = 0
            self.pipeline.seek_simple(gst.FORMAT_TIME,
                                     gst.SEEK_FLAG_FLUSH,
                                     seek_ns)
            self.emit('skip-backward')

    def get_media_position(self):
        '''Get current position of the play back.'''
        try:
            pos = self.pipeline.query_position(gst.FORMAT_TIME, None)[0]
            dur = self.pipeline.query_duration(gst.FORMAT_TIME, None)[0]
        except gst.QueryError:
            # This normally means that the MediaPlayer object is querying
            # before the media is playing.
            return 0
        dur_sec = dur / 1000000000.0
        pos_sec = pos / 1000000000.0
        return pos_sec / dur_sec

    def get_media_position_string(self):
        '''Get current position of the play back as human readable string.'''
        try:
            nanoseconds = self.pipeline.query_position(gst.FORMAT_TIME, None)[0]
            return self._convert_ns_to_human_readable(nanoseconds)
        except gst.QueryError:
            # This normally means that the MediaPlayer object is querying
            # before the media is playing.
            return "00:00"

    def set_media_position(self, position):
        '''Set position of the current media.'''
        if position < 0.0:
            position = 0.0

        if position > 1.0:
            position = 1.0

        if (self.media.get_type() == Playable.AUDIO_STREAM) or \
            (self.media.get_type() == Playable.VIDEO_STREAM):
            dur = self.pipeline.query_duration(gst.FORMAT_TIME, None)[0]
            seek_ns = (position * dur)
            if seek_ns > dur:
                seek_ns = dur
            self.pipeline.seek_simple(gst.FORMAT_TIME,
                                     gst.SEEK_FLAG_FLUSH,
                                     seek_ns)

    def get_media_duration_string(self):
        '''
        Return media duration in string format. Example 04:20
        This code is borrowed from gStreamer python tutorial.
        '''
        try:
            nanoseconds = self.pipeline.query_duration(gst.FORMAT_TIME, None)[0]
            return self._convert_ns_to_human_readable(nanoseconds)
        except gst.QueryError:
            # This normally means that the MediaPlayer object is querying
            # before the media is playing.
            return "00:00"

    def get_media_title(self):
        '''Returns the title of the playing media.'''
        return self.media.get_title()

    def _convert_ns_to_human_readable(self, time_int):
        '''
        Convert nano seconds to human readable time string.
        This code is borrowed from gStreamer python tutorial.
        '''
        time_int = time_int / 1000000000
        time_str = ""
        if time_int >= 3600:
            _hours = time_int / 3600
            time_int = time_int - (_hours * 3600)
            time_str = str(_hours) + ":"
        if time_int >= 600:
            _mins = time_int / 60
            time_int = time_int - (_mins * 60)
            time_str = time_str + str(_mins) + ":"
        elif time_int >= 60:
            _mins = time_int / 60
            time_int = time_int - (_mins * 60)
            time_str = time_str + "0" + str(_mins) + ":"
        else:
            time_str = time_str + "00:"
        if time_int > 9:
            time_str = time_str + str(time_int)
        else:
            time_str = time_str + "0" + str(time_int)
        return time_str

    def _on_size_change(self, texture, width, height):
        '''
        Callback for changing video texture's aspect ratio. This is called when
        video texture size changes.
        IMPORTANT NOTE FOR PYLINTers
        The texture parameter is unused, however it cannot be removed because
        this method is called as a callback by cluttergst.VideoTexture.connect()
        '''
        if self.ratio == MediaPlayer.NATIVE:
            self.set_native_ratio(width, height)
        elif self.ratio == MediaPlayer.WIDESCREEN:
            self.set_widescreen_ratio(width, height)
        elif self.ratio == MediaPlayer.ZOOM:
            self.set_zoom_ratio(width, height)
        elif self.ratio == MediaPlayer.INTELLIGENT:
            self.set_intelligent_ratio(width, height)

    def set_native_ratio(self, width=None, height=None):
        '''
        Do not stretch video. Use native ratio, but scale video such a way
        that it fits in the window.
        '''
        self.ratio = MediaPlayer.NATIVE
        if self.has_media() and self.media.get_type() == Playable.VIDEO_STREAM:
            if width is None and height is None:
                texture_width, texture_height = self.video_texture.get_size()
            else:
                texture_width = width
                texture_height = height
            x_ratio = self.stage_width / float(texture_width)
            y_ratio = self.stage_height / float(texture_height)

            if x_ratio > y_ratio:
                self.video_texture.set_scale(
                    self.stage_height / float(texture_height),
                    self.stage_height / float(texture_height))
                new_width = int(texture_width * \
                    (self.stage_height / float(texture_height)))
                new_x = int((self.stage_width - new_width) / float(2))
                self.video_texture.set_position(new_x, 0)
            else:
                self.video_texture.set_scale(
                    self.stage_width / float(texture_width),
                    self.stage_width / float(texture_width))
                new_height = int(texture_height * \
                    (self.stage_width / float(texture_width)))
                new_y = int((self.stage_height - new_height) / float(2))
                self.video_texture.set_position(0, new_y)

    def set_widescreen_ratio(self, width=None, height=None):
        ''''Stretch video to 16:9 ratio.'''
        self.ratio = MediaPlayer.WIDESCREEN
        if self.has_media() and self.media.get_type() == Playable.VIDEO_STREAM:
            if width is None and height is None:
                texture_width, texture_height = self.video_texture.get_size()
            else:
                texture_width = width
                texture_height = height
            self.video_texture.set_scale(
                self.stage_width / float(texture_width),
                self.stage_height / float(texture_height))
            self.video_texture.set_position(0, 0)

    def set_letter_box_ratio(self, width=None, height=None):
        '''Set video playback into letter box mode.'''
        self.ratio = MediaPlayer.LETTER_BOX
        raise Exception("width=", width, "height=", height,
            "set_letter_box_ratio() is NOT implemented!")

    def set_zoom_ratio(self, width=None, height=None):
        '''
        Stretch video to screen such a way that video covers most of the
        screen.
        '''
        self.ratio = MediaPlayer.ZOOM
        if self.has_media() and self.media.get_type() == Playable.VIDEO_STREAM:
            if width is None and height is None:
                texture_width, texture_height = self.video_texture.get_size()
            else:
                texture_width = width
                texture_height  = height
            x_ratio = self.stage_width / float(texture_width)
            y_ratio = self.stage_height / float(texture_height)

            if x_ratio < y_ratio:
                self.video_texture.set_scale(
                    self.stage_height / float(texture_height),
                    self.stage_height / float(texture_height))
                new_width = int(texture_width * \
                    (self.stage_height / float(texture_height)))
                new_x = int((self.stage_width - new_width) / float(2))
                self.video_texture.set_position(new_x, 0)
            else:
                self.video_texture.set_scale(
                    self.stage_width / float(texture_width),
                    self.stage_width / float(texture_width))
                new_height = int(texture_height * \
                    (self.stage_width / float(texture_width)))
                new_y = int((self.stage_height - new_height) / float(2))
                self.video_texture.set_position(0, new_y)

    def set_intelligent_ratio(self, width=None, height=None):
        '''
        This aspect ratio tries to display 4:3 on 16:9 in such a way that
        it looks good and still uses the whole screen space. It crops some of
        the image and does some stretching, but not as much as
        set_widescreen_ratio() method.
        '''
        self.ratio = MediaPlayer.INTELLIGENT
        if self.has_media() and self.media.get_type() == Playable.VIDEO_STREAM:
            ratio = 1.555555555 # 14:9 Aspect ratio
            if width is None and height is None:
                texture_width, texture_height = self.video_texture.get_size()
            else:
                texture_width = width
                texture_height = height
            fake_height = self.stage_width / ratio # Fake stage aspect ratio
            self.video_texture.set_scale(
                self.stage_width / float(texture_width),
                fake_height / float(texture_height))
            y_offset = -int((fake_height - self.stage_height) / 2)
            self.video_texture.set_position(0, y_offset)

    def get_texture(self):
        '''Get media's texture. This is a video texture or album art texture.'''
        if self.media.get_type() == Playable.VIDEO_STREAM:
            return clutter.Clone(self.video_texture)

        elif self.media.get_type() == Playable.AUDIO_STREAM:
            url = self.media.get_album_art_url()
            if url is not None:
                texture = Texture(url)
                return texture
            else:
                return None

    def _internal_timer_callback(self):
        '''
        A `refresh` event is regulary emited if media is playing.
        And update of the media's' position if a MODE_SEEK has been started
        with the pointer.
        '''
        if self.is_playing:
            self.emit('refresh')

        if self._event_mode == self.MODE_SEEK:
            position = self.get_media_position()
            position += self._seek_step
            self.set_media_position(position)
            self.emit('position-changed')

        return True

    def _on_button_press_event(self, actor, event):
        """`button-press` event handler."""
        if not self.is_reactive_allowed:
            return

        clutter.grab_pointer(self.video_texture)
        if not self.video_texture.handler_is_connected(self._motion_handler):
            self._motion_handler = self.video_texture.connect('motion-event',
            self._on_motion_event)

        self._motion_buffer.start(event)
        self._event_mode = self.MODE_PLAYPAUSE

    def _on_button_release_event(self, actor, event):
        """`button-press` event handler."""
        if not self.is_reactive_allowed:
            return

        clutter.ungrab_pointer()
        if self.video_texture.handler_is_connected(self._motion_handler):
            self.video_texture.disconnect_by_func(self._on_motion_event)

        if self._event_mode == self.MODE_PLAYPAUSE:
            if self.is_playing:
                self.pause()
            else:
                self.play()

        self._event_mode = self.MODE_NONE

    def _on_motion_event(self, actor, event):
        """`motion-event` event handler."""
        # threshold in pixels = the minimum distance we have to move before we
        # consider a motion has started
        motion_threshold = 20

        self._motion_buffer.compute_from_start(event)
        if self._motion_buffer.distance_from_start > motion_threshold:
            self._motion_buffer.take_new_motion_event(event)
            self._event_mode = self.MODE_SEEK
            self._seek_step = float(self._motion_buffer.dx_from_start)
            self._seek_step /= self.video_texture.get_width()
            self._seek_step *= 0.01

        return False

    def _on_scroll_event(self, actor, event):
        '''`scroll-event` event handler (mouse's wheel).'''
        # +/- 2% per scroll event on the position of the media stream.
        scroll_progress_ratio = 0.02

        position = self.get_media_position()

        if event.direction == clutter.SCROLL_DOWN:
            position -= scroll_progress_ratio
        else:
            position += scroll_progress_ratio

        self.set_media_position(position)
        self.emit('position-changed')

