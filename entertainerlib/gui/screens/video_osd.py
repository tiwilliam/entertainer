# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''VideoOSD - Screen is used for video playback On Screen Display.'''

import gobject
import clutter

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.widgets.progress_bar import ProgressBar
from entertainerlib.gui.widgets.texture import Texture


class VideoOSD(Screen):
    '''Screen is displayed when video is being watched.

    Usually this screen doesn't have any visible elements. User actions such
    as pause and rewind are displayed as on-screen-graphics.'''

    def __init__(self, media_player):
        Screen.__init__(self, 'VideoOSD', kind=Screen.OSD)

        self.theme = self.config.theme
        self.media_player = media_player
        self.media_player.connect('play', self._handle_play_pause)
        self.media_player.connect('pause', self._handle_play_pause)
        self.media_player.connect('skip-forward', self._handle_skip_forward)
        self.media_player.connect('skip-backward', self._handle_skip_backward)

        self._progress_bar = self._create_progress_bar()
        self.add(self._progress_bar)
        self.aspect_textures = None
        self.pause_texture = None
        self.seekbackward_texture = None
        self.seekforward_texture = None

        self.timeout_key = None
        self.progress_bar_timeout_key = None

        self.event_handlers.update({
            UserEvent.PLAYER_PLAY_PAUSE : self._handle_play_pause,
            UserEvent.PLAYER_SKIP_BACKWARD : self._handle_skip_backward,
            UserEvent.PLAYER_SKIP_FORWARD : self._handle_skip_forward,
            UserEvent.PLAYER_STOP : self._handle_stop,
            UserEvent.USE_ASPECT_RATIO_1 : self._handle_ratio_1,
            UserEvent.USE_ASPECT_RATIO_2 : self._handle_ratio_2,
            UserEvent.USE_ASPECT_RATIO_3 : self._handle_ratio_3,
            UserEvent.USE_ASPECT_RATIO_4 : self._handle_ratio_4
        })

        self._create_aspect_ratio_textures()

        self._create_navigation_textures()

    def _create_navigation_textures(self):
        '''Create the pause, seek-backward & seek-forward textures.'''
        self.pause_texture = Texture(
            self.theme.getImage("media-playback-pause"), 0.5, 0.5)
        self.pause_texture.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        self.pause_texture.hide()
        self.add(self.pause_texture)

        pause_in_time = clutter.Timeline(1000)
        in_alpha_pause = clutter.Alpha(pause_in_time, clutter.EASE_IN_OUT_SINE)

        self.pause_in_opacity = clutter.BehaviourOpacity(alpha=in_alpha_pause,
            opacity_start=100, opacity_end=255)
        self.pause_in_scale = clutter.BehaviourScale(1.0, 1.0, 1.4, 1.4,
            in_alpha_pause)

        self.pause_in_opacity.apply(self.pause_texture)
        self.pause_in_scale.apply(self.pause_texture)

        pause_out_time = clutter.Timeline(1000)
        out_alpha_pause = clutter.Alpha(pause_out_time,
            clutter.EASE_IN_OUT_SINE)

        self.pause_out_opacity = clutter.BehaviourOpacity(alpha=out_alpha_pause,
            opacity_start=255, opacity_end=100)
        self.pause_out_scale = clutter.BehaviourScale(1.4, 1.4, 1.0, 1.0,
            out_alpha_pause)

        self.pause_out_opacity.apply(self.pause_texture)
        self.pause_out_scale.apply(self.pause_texture)

        self.score = clutter.Score()
        self.score.set_loop(True)
        self.score.append(timeline=pause_in_time)
        self.score.append(timeline=pause_out_time, parent=pause_in_time)
        self.score.start()

        self.seekbackward_texture = Texture(
            self.theme.getImage("media-seek-backward"), 0.1, 0.5)
        self.seekbackward_texture.set_anchor_point_from_gravity(
            clutter.GRAVITY_CENTER)
        self.seekbackward_texture.set_opacity(0)
        self.add(self.seekbackward_texture)

        self.seekbackward_timeline = clutter.Timeline(1000)
        alpha_seekbackward = clutter.Alpha(self.seekbackward_timeline,
            clutter.EASE_IN_OUT_SINE)

        self.seekbackward_opacity = clutter.BehaviourOpacity(
            alpha=alpha_seekbackward, opacity_start=255, opacity_end=0)
        self.seekbackward_opacity.apply(self.seekbackward_texture)

        self.seekforward_texture = Texture(
            self.theme.getImage("media-seek-forward"), 0.9, 0.5)
        self.seekforward_texture.set_anchor_point_from_gravity(
            clutter.GRAVITY_CENTER)
        self.seekforward_texture.set_opacity(0)
        self.add(self.seekforward_texture)

        self.seekforward_timeline = clutter.Timeline(1000)
        alpha_seekforward = clutter.Alpha(self.seekforward_timeline,
            clutter.EASE_IN_OUT_SINE)

        self.seekforward_opacity = clutter.BehaviourOpacity(
            alpha=alpha_seekforward, opacity_start=255, opacity_end=0)
        self.seekforward_opacity.apply(self.seekforward_texture)

    def _create_progress_bar(self):
        '''Create the progress bar.'''
        progress_bar = ProgressBar(0.5, 0.9, 0.40, 0.04)
        progress_bar.auto_display = True
        progress_bar.media_player = self.media_player
        progress_bar.visible = True
        return progress_bar

    def _create_aspect_ratio_textures(self):
        '''
        Create textures that which are displayed when user changes aspect ratio.
        '''
        texture_1 = Texture(self.theme.getImage("native_aspect_ratio"))
        texture_1.hide()
        self.add(texture_1)
        texture_2 = Texture(self.theme.getImage("widescreen_aspect_ratio"))
        texture_2.hide()
        self.add(texture_2)
        texture_3 = Texture(self.theme.getImage("zoom_aspect_ratio"))
        texture_3.hide()
        self.add(texture_3)
        texture_4 = Texture(self.theme.getImage("compromise_aspect_ratio"))
        texture_4.hide()
        self.add(texture_4)
        self.aspect_textures = [texture_1, texture_2, texture_3, texture_4]
        self.timeout_key = None # This is used when canceling timeouts
        for texture in self.aspect_textures:
            texture.position = (
                float(self.config.stage_width - texture.get_width()) /
                (self.config.stage_width * 2), 0.67)

    def _hide_aspect_ratio_logo(self, number):
        '''
        Hide aspect ratio texture. This is a callback function and
        shouldn't be called directly.
        '''
        self.aspect_textures[number].hide()
        self.timeout_key = None
        return False

    def _display_aspect_ratio_logo(self, number):
        '''Display aspect ratio logo on screen when ratio is changed.'''
        if self.timeout_key is not None:
            gobject.source_remove(self.timeout_key)
        for texture in self.aspect_textures:
            texture.hide()
        self.aspect_textures[number].show()
        self.timeout_key = gobject.timeout_add(2000,
            self._hide_aspect_ratio_logo, number)

    def _handle_play_pause(self, event=None):
        '''Handle UserEvent.PLAYER_PLAY_PAUSE.'''
        if self.media_player.is_playing:
            self.pause_texture.hide()
        else:
            self.pause_texture.show()
        self._progress_bar.visible = True

    def _handle_skip_backward(self, event=None):
        '''Handle UserEvent.PLAYER_SKIP_BACKWARD.'''
        self._progress_bar.visible = True
        self.seekbackward_timeline.start()

    def _handle_skip_forward(self, event=None):
        '''Handle UserEvent.PLAYER_SKIP_FORWARD.'''
        self._progress_bar.visible = True
        self.seekforward_timeline.start()

    def _handle_stop(self):
        '''Handle UserEvent.PLAYER_STOP.'''
        self._progress_bar.visible = True
        self.pause_texture.hide()

    def _handle_ratio_1(self):
        '''Handle UserEvent.USE_ASPECT_RATIO_1.'''
        self._display_aspect_ratio_logo(0)

    def _handle_ratio_2(self):
        '''Handle UserEvent.USE_ASPECT_RATIO_2.'''
        self._display_aspect_ratio_logo(1)

    def _handle_ratio_3(self):
        '''Handle UserEvent.USE_ASPECT_RATIO_3.'''
        self._display_aspect_ratio_logo(2)

    def _handle_ratio_4(self):
        '''Handle UserEvent.USE_ASPECT_RATIO_4.'''
        self._display_aspect_ratio_logo(3)

