# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Texture with rounded corners and reflection below'''

import clutter

from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.rounded_texture import RoundedTexture
from entertainerlib.gui.widgets.reflection_texture import (
    ReflectionTexture)

class EyeCandyTexture(Base, clutter.Group):
    """
    Just a simple wrapper class for RoundedTexture and ReflectionTexture.

    EyeCandyTexture is a texture with rounded corners and reflection below.
    """

    def __init__(self, x, y, width, height, pixbuf):
        Base.__init__(self)
        clutter.Group.__init__(self)

        rounded = RoundedTexture(0.0, 0.0, width, height, pixbuf)
        reflection = ReflectionTexture(0.0, 0.0, width, height, pixbuf,
            round_corners=True)

        reflection.set_position(0, rounded.get_height())
        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

        self.add(rounded)
        self.add(reflection)

