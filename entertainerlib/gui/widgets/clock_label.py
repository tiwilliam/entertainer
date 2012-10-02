# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''ClockLabel widget'''

import time
import gobject

from entertainerlib.gui.widgets.label import Label

class ClockLabel(Label):
    """Label that displays current time."""

    def __init__(self, font_size, color_name, x_pos_percent, y_pos_percent,
        name=None, font_weight=""):
        """Initialize Clock label"""
        Label.__init__(self, font_size, color_name, x_pos_percent,
            y_pos_percent, name = None, font_weight = font_weight)

        self._24_hour_clock = True
        self.update_clock_label()
        gobject.timeout_add(1000 * 60, self.update_clock_label)

    def set_use_24_hour_clock(self, boolean):
        """
        This method is used to determine time format of the clock. If paramter
        is set True, then we show time like "23:40" and if False then "11:40PM"
        @param boolean: Should we use 24h format
        """
        self._24_hour_clock = boolean

    def update_clock_label(self):
        """
        Callback function that updates Label's text to display current time.
        """
        # Get current time
        t = time.localtime()
        hours = str(t.tm_hour)
        minutes = str(t.tm_min)

        # Add padding if needed: 14:2 -> 14:02
        if len(minutes) == 1:
            minutes = "0" + minutes
        if len(hours) == 1:
            hours = "0" + hours

        # Convert hours if needed
        if not self._24_hour_clock:
            if int(hours) > 12:
                hours = str(int(hours) - 12)
                suffix = "PM"
            else:
                suffix = "AM"
            label = hours + ":" + minutes + suffix
        else:
            label = hours + ":" + minutes

        self.set_text(label)
        return True

