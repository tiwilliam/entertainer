# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Texture widget"""

import clutter

from entertainerlib.gui.widgets.base import Base
from entertainerlib.logger import Logger

class Texture(Base, clutter.Texture):
    """Wrapper of a clutter texture to encapsulate position settings and have
    knowledge of the stage size. Since most actors are shown by default when
    added to a group, Texture is shown by default."""

    def __init__(self, filename, x_pos_percent=0, y_pos_percent=0):
        """Initialize the Texture object"""

        Base.__init__(self)
        clutter.Texture.__init__(self, filename)
        self.logger = Logger().getLogger('gui.widgets.Texture')

        self._position = None
        self._set_position((x_pos_percent, y_pos_percent))

    def _get_position(self):
        """Return the position as a tuple of percents of the stage size"""
        return self._position

    def _set_position(self, position_pair):
        """Translate a tuple of x and y percentages into an absolute position
        within the display area"""
        self._position = position_pair

        (x_pos_percent, y_pos_percent) = position_pair

        clutter.Texture.set_position(self,
            self.get_abs_x(x_pos_percent),
            self.get_abs_y(y_pos_percent))

    position = property(_get_position, _set_position)

