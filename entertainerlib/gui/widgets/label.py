# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Label widget"""

import clutter

from entertainerlib.gui.widgets.base import Base

class Label(Base, clutter.Text):
    """Wrapper of a clutter text to encapsulate some label settings and have
    knowledge of the stage size"""

    def __init__(self, font_size, color_name, x_pos_percent, y_pos_percent,
        text=None, name=None, font_weight=""):
        """Initialize the Label object"""

        Base.__init__(self)
        clutter.Text.__init__(self)

        self.theme = self.config.theme

        self._font_weight = font_weight
        self._font_size = font_size
        self._set_font_size(font_size)

        self.color = color_name

        self._position = None
        self._set_position((x_pos_percent, y_pos_percent))

        if text:
            self.set_text(text)
        if name:
            self.set_name(name)

        self.set_line_wrap(True)

    def _get_color(self):
        """color property getter."""
        return self._color

    def _set_color(self, color_name):
        """color property setter."""
        self._color = color_name
        self.set_color(self.theme.get_color(self._color))

    color = property(_get_color, _set_color)

    def set_size(self, x_percent, y_percent):
        """Override clutter label set_size to calculate absolute size from a
        percentage"""
        clutter.Text.set_size(self,
            self.get_abs_x(x_percent),
            self.get_abs_y(y_percent))

    def _get_width(self):
        """Return the width as a percent of the stage size"""
        return float(self.get_width()) / self.config.stage_width

    def _set_width(self, x_percent):
        """Set the width based on a hozirontal percent of the stage size.
        Provide clutter label set_width the absolute size from the percentage"""
        clutter.Text.set_width(self, self.get_abs_x(x_percent))

    width = property(_get_width, _set_width)

    def _get_position(self):
        """Return the position as a tuple of percents of the stage size"""
        return self._position

    def _set_position(self, position_pair):
        """Translate a tuple of x and y percentages into an absolute position
        within the display area"""
        self._position = position_pair

        (x_pos_percent, y_pos_percent) = position_pair

        clutter.Text.set_position(self,
            self.get_abs_x(x_pos_percent),
            self.get_abs_y(y_pos_percent))

    position = property(_get_position, _set_position)

    def _get_height(self):
        """Return the height as a percent of the stage size"""
        return float(self.get_height()) / self.config.stage_height

    def _set_height(self, y_percent):
        """Set the height based on a vertical percent of the stage size.
        Provide clutter label set_height the absolute size from the percentage
        """
        clutter.Text.set_height(self, self.get_abs_y(y_percent))

    height = property(_get_height, _set_height)

    def _get_font_size(self):
        """Return the font size as a percent of the stage size"""
        return self._font_size

    def _set_font_size(self, y_percent):
        """Set the font size based on a vertical percent of the screen size"""
        self._font_size = y_percent
        self.set_font_name(self.theme.font + ", " + self._font_weight +
            " " + str(self.get_abs_y(y_percent)) + "px")

    font_size = property(_get_font_size, _set_font_size)

