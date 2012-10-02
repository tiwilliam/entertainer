# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Simple Menuitem."""

import clutter

from entertainerlib.gui.widgets.base import Base

class MenuItem(Base, clutter.Group):
    """Simple menuitem widget."""

    def __init__(self):
        Base.__init__(self)
        clutter.Group.__init__(self)

        self._userdata = None

    def _get_userdata(self):
        """userdata property getter."""
        return self._userdata

    def _set_userdata(self, userdata):
        """userdata property getter."""
        self._userdata = userdata

    userdata = property (_get_userdata, _set_userdata)

    def animate_in(self):
        """Animation to be done when an item gets selected."""
        pass

    def animate_out(self):
        """Animation to be done when an item gets unselected."""
        pass

