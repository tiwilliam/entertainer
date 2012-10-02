# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Implements progress bar widget'''

import gobject
import math

import clutter

from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.label import Label

class ProgressBar(Base, clutter.Group):
    '''
    Progress bar widget.

    This widget implements simple progress bar.
    '''
    # Cursor's radius in % of the widget's height
    CURSOR_RADIUS = 0.3
    BAR_LENGTH = 0.5
    INFO_LENGTH = (1 - BAR_LENGTH) / 2.0

    def __init__(self, x, y, width, height, color="title"):
        Base.__init__(self)
        clutter.Group.__init__(self)

        self.width = self.get_abs_x(width)
        self.height = self.get_abs_y(height)
        self.bar_width = int(self.width * self.BAR_LENGTH)
        self.bar_x = int(self.width * self.INFO_LENGTH)
        self.media_length_x = (1 - self.INFO_LENGTH + 0.05) * width

        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

        self._color = self._color_to_cairo_color(
            self.config.theme.get_color(color))

        self._background = clutter.CairoTexture(self.bar_width, self.height)
        self._draw_background()
        self._background.set_position(self.bar_x, 0)
        self.add(self._background)

        self._foreground = clutter.CairoTexture(self.height, self.height)
        self._foreground.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        self._draw_foreground()
        self._foreground.set_position(self.bar_x, 0)
        self.add(self._foreground)

        self.media_position = Label(0.037, "title", 0, 0, "")
        self.add(self.media_position)

        self.media_length = Label(0.037, "title", self.media_length_x, 0, "")
        self.add(self.media_length)

        self._media_player = None
        self._progress_bar_moving = False

        self._hide_timeout_key = None
        self.auto_display = False
        self._visible = None
        self._timeline = clutter.Timeline(500)
        self._alpha = clutter.Alpha(self._timeline, clutter.EASE_IN_OUT_SINE)
        self._behaviour = clutter.BehaviourOpacity(0, 255, self._alpha)
        self._behaviour.apply(self)

        self._progress = None
        # Call the property setter to initialize the displayed position.
        self.progress = 0

        # Preparation to pointer events handling.
        self._motion_handler = 0
        self.set_reactive(True)
        self.connect('scroll-event', self._on_scroll_event)
        self.connect('button-press-event', self._on_button_press_event)
        self.connect('button-release-event', self._on_button_release_event)
        self.connect('enter-event', self._on_enter_event)
        self.connect('leave-event', self._on_leave_event)

    def _get_media_player(self):
        '''media_player property getter.'''
        return self._media_player

    def _set_media_player(self, media_player):
        '''media_player property setter.'''
        self._media_player = media_player
        self._media_player.connect('refresh', self._update_media_position)
        self._media_player.connect('stop', self._update_media_position)
        self._media_player.connect('position-changed',
            self._on_player_position_changed)

    media_player = property(_get_media_player, _set_media_player)

    def _get_progress(self):
        '''progress property getter.'''
        return self._progress

    def _set_progress(self, progress):
        '''progress property setter.'''
        if progress > 1:
            progress = 1
        if progress < 0:
            progress = 0
        self._progress = progress
        self._foreground.set_position(int(self.bar_x + (self.height / 2) +
            int(self.bar_width - self.height) * progress), int(self.height / 2))

    progress = property(_get_progress, _set_progress)

    def _get_visible(self):
        '''visible property getter.'''
        if self._visible == None:
            self._visible = True
        return self._visible

    def _set_visible(self, boolean):
        '''visible property setter.'''
        if self._visible == boolean:
            return

        self._visible = boolean

        if boolean:
            self._timeline.set_direction(clutter.TIMELINE_FORWARD)
            self._timeline.rewind()
            self._timeline.start()
            if self.auto_display:
                if self._hide_timeout_key is not None:
                    gobject.source_remove(self._hide_timeout_key)
                self._hide_timeout_key = gobject.timeout_add(3000,
                    self._hide_progress_bar)

        else:
            self._timeline.set_direction(clutter.TIMELINE_BACKWARD)
            self._timeline.start()

    visible = property(_get_visible, _set_visible)

    def _hide_progress_bar(self):
        '''Update the progress bar.'''
        self.visible = False
        return False

    def _reset_auto_display_timeout(self):
        '''Reset the timeout if auto_display = True.'''
        if self._hide_timeout_key is not None:
            gobject.source_remove(self._hide_timeout_key)
        self._hide_timeout_key = gobject.timeout_add(3000,
            self._hide_progress_bar)

    def _update_media_position(self, event=None):
        '''Update the media's position.'''
        if not self._progress_bar_moving:
            self.progress = self.media_player.get_media_position()
        self.media_position.set_text(
            self.media_player.get_media_position_string())
        self.media_length.set_text(
            self.media_player.get_media_duration_string())

    def _draw_background(self):
        '''Draw background graphics.'''
        context = self._background.cairo_create()
        context.set_line_width(self.height * 0.09)
        context.set_source_rgba(
            self._color[0], self._color[1], self._color[2], 0.7)

        context.arc(self.height / 2,
                    self.height / 2,
                    self.height / 2 -2,
                    math.pi / 2,
                    math.pi * 1.5)
        context.arc(self.bar_width - self.height / 2,
                    self.height / 2,
                    self.height / 2 -2,
                    math.pi * 1.5,
                    math.pi / 2)
        context.close_path()

        context.stroke()
        del context

    def _draw_foreground(self):
        '''Draw foreground graphics.'''
        context = self._foreground.cairo_create()
        context.scale(self.height, self.height)
        context.set_source_rgba(
            self._color[0], self._color[1], self._color[2], 1.0)
        context.arc(0.5, 0.5, self.CURSOR_RADIUS, 0, 2 * math.pi)
        context.fill()
        del context

    def _color_to_cairo_color(self, color):
        '''Transform color to cairo format (0-255 to 0-1).'''
        (int_r, int_g, int_b, int_a) = color
        r = float(int_r) / 255.0
        g = float(int_g) / 255.0
        b = float(int_b) / 255.0
        a = float(int_a) / 255.0
        return r, g, b, a

    def _on_button_press_event(self, actor, event):
        '''button-press-event handler.'''
        if not self.visible:
            self.visible = True
            return

        clutter.grab_pointer(self)

        x = event.x - self.get_x()
        y = event.y - self.get_y()

        dx = x - int(self.bar_x + (self.height / 2) + \
            (self.bar_width - self.height) * self._progress)
        dy = y - int(self.height / 2)

        # Calculation of the distance between our click and the middle of
        # the progress_bar cursor position.
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= (self.CURSOR_RADIUS * self.height):
            # Clicked around the cursor.
            if not self.handler_is_connected(self._motion_handler):
                self._motion_handler = self.connect('motion-event',
                    self._on_motion_event)
                self._progress_bar_moving = True
        else:
            # Clicked far from the cursor. Change to the pointed position.
            progress = (x - self.bar_x - (self.height / 2.0)) / \
                (self.bar_width - self.height)
            self.progress = progress
            self._progress_bar_moving = False
            self.media_player.set_media_position(self.progress)

        if self._hide_timeout_key is not None:
            gobject.source_remove(self._hide_timeout_key)

        return False

    def _on_button_release_event(self, actor, event):
        '''button-release-event handler.'''
        clutter.ungrab_pointer()

        if self.handler_is_connected(self._motion_handler):
            self.disconnect_by_func(self._on_motion_event)

        self._progress_bar_moving = False
        self.media_player.set_media_position(self.progress)

        if self.auto_display and self.visible:
            self._hide_timeout_key = gobject.timeout_add(3000,
                self._hide_progress_bar)

        return False

    def _on_motion_event(self, actor, event):
        '''motion-event handler.'''
        x_cursor = event.x - self.get_x()
        progress = (x_cursor - self.bar_x - (self.height / 2.0)) / \
            (self.bar_width - self.height)
        self.progress = progress
        self.media_player.set_media_position(self.progress)

        return False

    def _on_scroll_event(self, actor, event):
        '''scroll-event handler (mouse's wheel).'''
        # +/- 2% per scroll event on the position of the media stream.
        self.visible = True
        scroll_progress_ratio = 0.02

        if event.direction == clutter.SCROLL_DOWN:
            self.progress -= scroll_progress_ratio
        else:
            self.progress += scroll_progress_ratio

        self._progress_bar_moving = False
        self.media_player.set_media_position(self.progress)

        return False

    def _on_enter_event(self, stage, clutter_event):
        '''Shows the progress bar.'''
        if self.auto_display and not self._progress_bar_moving:
            self.visible = True

    def _on_leave_event(self, stage, clutter_event):
        '''Hides the progress bar.'''
        if self.auto_display and not self._progress_bar_moving:
            self.visible = False

    def _on_player_position_changed(self, event=None):
        '''Shows the progress bar.'''
        if self.auto_display and not self._progress_bar_moving:
            self.visible = True
            self._reset_auto_display_timeout()

