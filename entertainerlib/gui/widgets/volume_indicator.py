# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""A volume indicator widgets."""

import clutter
import gobject

from entertainerlib.gui.widgets.base import Base

class VolumeIndicator(Base, clutter.Group):
    """Volume Indicator displaying player's volume level."""
    __gsignals__ = {
        'hiding' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        }

    def __init__(self):
        Base.__init__(self)
        clutter.Group.__init__(self)

        theme = self.config.theme
        filled = clutter.Texture(theme.getImage("volume_filled"))
        filled.hide()
        self.add(filled)
        unfilled = clutter.Texture(theme.getImage("volume_unfilled"))
        unfilled.hide()
        self.add(unfilled)
        volume = clutter.Texture(theme.getImage("volume"))
        self.add(volume)

        self._bars = []

        bar_width = filled.get_width()

        for i in range(20):
            bar_filled = clutter.Clone(filled)
            bar_unfilled = clutter.Clone(unfilled)
            bar_filled.set_position(volume.get_width() + i * bar_width, 0)
            bar_unfilled.set_position(volume.get_width() + i * bar_width, 0)
            self.add(bar_filled)
            self.add(bar_unfilled)
            self._bars.append([bar_filled, bar_unfilled])

        self._hide_timeout_key = None
        self.visible = False
        self.set_opacity(0)

        self.timeline = clutter.Timeline(200)
        self.alpha = clutter.Alpha(self.timeline, clutter.EASE_IN_OUT_SINE)
        self.behaviour = clutter.BehaviourOpacity(255, 0, self.alpha)
        self.behaviour.apply(self)

        self.set_position(self.get_abs_x(0.35), self.get_abs_y(0.1))

    def show_volume(self, volume):
        """Displays volume level using filled and unfilled bars."""
        self.raise_top()

        if self._hide_timeout_key is not None:
            gobject.source_remove(self._hide_timeout_key)
        self._hide_timeout_key = gobject.timeout_add(2000,
            self.animate_out)

        for index, bars in enumerate(self._bars):
            if index >= volume:
                bars[0].set_opacity(0)
                bars[1].set_opacity(255)
            else:
                bars[0].set_opacity(255)
                bars[1].set_opacity(0)

        if self.visible == True:
            return

        self.visible = True
        self.behaviour.set_bounds(0, 255)
        self.timeline.start()

    def animate_out(self):
        """Fades out."""
        self.behaviour.set_bounds(255, 0)
        self.timeline.start()
        self.visible = False
        self.emit("hiding")
        return False

