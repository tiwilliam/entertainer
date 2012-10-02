# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Displays currently selected item and length of the list'''

import clutter

from entertainerlib.gui.widgets.arrow_texture import ArrowTexture
from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.label import Label
from entertainerlib.configuration import Configuration


class ListIndicator(Base, clutter.Group):
    """
    ListIndicator displays 'current / maximum' value label and arrows.
    """

    # Direction
    # HORIZONTAL layout: ARROW_LEFT current / maximum ARROW_RIGHT
    # VERITCAL layout:   current / maximum ARROW_UP ARROW_DOWN
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, x, y, width, height, direction):
        Base.__init__(self)
        clutter.Group.__init__(self)

        self.config = Configuration()

        # Size
        self.width = self.get_abs_x(width)
        self.height = self.get_abs_y(height)

        self.direction = direction
        self.delimiter = " | "
        self.current = 1
        self.maximum = 1

        self.theme = self.config.theme
        self.fg = self.theme.get_color("arrow_foreground")
        self.bg = self.theme.get_color("arrow_background")

        if direction == ListIndicator.VERTICAL:
            text_x_pos = width / 3
        else:
            text_x_pos = width / 2

        self.text = Label(height * 0.8, "text", text_x_pos, height / 2,
            str(self.maximum) + self.delimiter + str(self.maximum))
        self.text.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        self.add(self.text)

        # Create arrows and calculate positions on screen
        if direction == ListIndicator.VERTICAL:
            self.arrow1 = ArrowTexture(5 * width / 7, height / 2, height / 2,
                self.fg, self.bg, ArrowTexture.UP)
            self.arrow2 = ArrowTexture(6 * width / 7, height / 2, height / 2,
                self.fg, self.bg, ArrowTexture.DOWN)

        elif direction == ListIndicator.HORIZONTAL:
            self.arrow1 = ArrowTexture(height / 2, height / 2, height / 2,
                self.fg, self.bg, ArrowTexture.LEFT)
            self.arrow2 = ArrowTexture(6 * width / 7, height / 2, height / 2,
                self.fg, self.bg, ArrowTexture.RIGHT)

        self.add(self.arrow1)
        self.add(self.arrow2)

        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

    def set_current(self, value):
        """
        Set current value
        @param number: Current value (between 1 - maximum)
        """
        if value > 0 and value <= self.maximum:
            self.current = value
            self._update_text()

            # Bounce arrow if user has reached the limit
            if self.current == 1:
                self.arrow1.bounce()
            elif self.current == self.maximum:
                self.arrow2.bounce()

    def get_current(self):
        """
        Get current value
        @return Current value (integer)
        """
        return self.current

    def set_maximum(self, value):
        """
        Set maximum value of the indicator
        @param number: Set maximum value
        """
        self.maximum = value
        self._update_text()

    def get_maximum(self):
        """
        Get maximum value.
        @return Max value (integer)
        """
        return self.maximum

    def set_delimiter(self, delimiter):
        """
        Set delimiter text that is displayed between current and maximum value.
        Default delimiter text is ' / ' spaces included.
        @param delimiter: delimiter text
        """
        self.delimiter = delimiter
        self._update_text()

    def show_position(self):
        """
        Show position text that indicates the current position of the content.
        """
        self.text.show()

    def hide_position(self):
        """
        Hide position text that indicates the current position of the content.
        If this is called then indicator shows only arrows.
        """
        self.text.hide()

    def _update_text(self):
        """Update the text label"""

        self.text.set_text(
            str(self.current) + self.delimiter + str(self.maximum))

