# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Animation widget indicates that Entertainer is loading'''

import math
import cairo
import clutter
import gobject

from entertainerlib.gui.widgets.base import Base


class LoadingAnimation(Base, clutter.CairoTexture):
    """
    Loading animation widget

    This widget is used when we want to tell user that Entertainer is loading.
    """

    def __init__(self, x, y, size=0.03, inner_radius=0.25, outter_radius=0.45,
            thickness=0.08):
        Base.__init__(self)

        abs_size = self.get_abs_x(size)

        clutter.CairoTexture.__init__(self, abs_size, abs_size)

        self.set_anchor_point(abs_size / 2, abs_size / 2)

        c = self._clutterColorToCairoColor(clutter.Color(255, 255, 255, 255))
        bg = self._clutterColorToCairoColor(clutter.Color(128, 128, 128, 128))

        context = self.cairo_create()
        context.scale(abs_size, abs_size)
        context.set_line_width (thickness)
        context.set_line_cap(cairo.LINE_CAP_ROUND)

        # Draw the 12 lines
        for i in range(12):
            self._draw_line(context, bg, c, outter_radius, inner_radius, i)

        del(context) # Updates texture

        self.keep_going = False

        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

    def _draw_line(self, context, bg_col, fg_col, radius, in_radius, number):
        """Draw one line"""
        if number < 2:
            context.set_source_rgba(bg_col[0], bg_col[1], bg_col[2], bg_col[3])
        else:
            context.set_source_rgba(fg_col[0], fg_col[1], fg_col[2], fg_col[3] \
                - (1 -(number - 1) * 0.1))

        # radius = radius of larger circle
        # in_radius = radius of smaller circle
        angle =  number * 30 * (math.pi / 180.0)
        context.arc(0.5, 0.5, in_radius, angle, angle)
        (x, y) = context.get_current_point()
        context.new_path()
        context.arc(0.5, 0.5, radius, angle, angle)
        context.line_to(x, y)
        context.stroke()

    def _clutterColorToCairoColor(self, color):
        """
        Transform from 0-255 to 0-1.
        @param color: clutter.Color
        """
        r = float(color.red) / 255.0
        g = float(color.green) / 255.0
        b = float(color.blue) / 255.0
        a = float(color.alpha) / 255.0
        return [r, g, b, a]

    def _rotate_throbber(self):
        """
        Update texture.
        """
        r = self.get_rotation(clutter.Z_AXIS)
        self.set_rotation(clutter.Z_AXIS, 30 + int(r[0]), 0, 0, 0)
        return self.keep_going

    def hide(self):
        '''Hide throbber smoothly and stop animation.'''
        timeline = clutter.Timeline(2000)
        alpha = clutter.Alpha(timeline, clutter.EASE_IN_OUT_SINE)
        self.behaviour = clutter.BehaviourOpacity(255, 0, alpha)
        self.behaviour.apply(self)
        timeline.start()

        gobject.timeout_add(5, self._stop_rotating, timeline)

    def _stop_rotating(self, timeline):
        '''Rotate throbber will be stopped when the hide timeline finishes'''
        if timeline.is_playing():
            return True
        else:
            self.keep_going = False
            clutter.CairoTexture.hide(self)
            return False

    def show(self):
        '''Show throbber and activate animation.'''
        self.keep_going = True
        gobject.timeout_add(50, self._rotate_throbber)
        clutter.CairoTexture.show(self)

