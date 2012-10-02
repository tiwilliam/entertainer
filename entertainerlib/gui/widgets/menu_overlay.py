# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Texture that is displayed over video when menu is active.'''

import clutter

from entertainerlib.gui.widgets.texture import Texture

class MenuOverlay(Texture):
    """
    Menu overlay widget

    Simple texture that is displayed over video when menu and video are active
    at the same time. Only difference to normal texture is that this texture
    provides methods fade_in() and fade_out().
    """

    def __init__(self, theme):
        """Initialize overlay texture."""
        Texture.__init__(self, filename = theme.getImage("menu_overlay"))
        self.timeline = clutter.Timeline(500)
        self.alpha = clutter.Alpha(self.timeline, clutter.EASE_IN_OUT_SINE)
        self.behaviour = clutter.BehaviourOpacity(255, 0, self.alpha)
        self.behaviour.apply(self)

    def fade_in(self):
        """Fade texture in."""
        self.behaviour.set_bounds(0, 255)
        self.timeline.start()

    def fade_out(self):
        """Fade texture out."""
        self.behaviour.set_bounds(255, 0)
        self.timeline.start()

