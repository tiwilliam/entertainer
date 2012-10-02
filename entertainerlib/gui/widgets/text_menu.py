# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Implements a grid menu that contains one or two labels.'''

import clutter
import gobject
import pango

from entertainerlib.gui.widgets.grid_menu import GridMenu
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.menu_item import MenuItem
from entertainerlib.gui.widgets.selector import Selector
from entertainerlib.gui.widgets.special_behaviours import FontSizeBehaviour

class TextMenuItem(MenuItem):
    """A menuitem widget that contains one or two labels."""

    def __init__(self, width, height, text, extra_text=None):
        MenuItem.__init__(self)

        self.width = width
        self.height = height
        self.theme = self.config.theme

        self.text = text
        self.extra_text = extra_text
        self.color = "menuitem_inactive"
        self.font_size = 0.03

        self.label = Label(self.font_size, self.color, 0, 0, "",
            "text_label")
        self.add(self.label)

        # Set extra text
        self.extra_label = None
        if extra_text is not None:
            self.extra_label = Label(self.font_size, self.color, 0, 0,
                "", "text_label")
            self.add(self.extra_label)

        self.update(text, extra_text)

    def animate_in(self):
        """Set labels font-size and color when an item gets selected."""
        self.font_size = 0.037
        self.color = "menuitem_active"
        self.update()

    def animate_out(self):
        """Set labels font-size and color when an item gets unselected."""
        self.font_size = 0.03
        self.color = "menuitem_inactive"
        self.update()

    def update(self, text=None, extra_text=None):
        """Updates text and dimensions of a TextMenuItem."""
        if text is None:
            text = self.text
        else:
            self.text = text

        if extra_text is None:
            extra_text = self.extra_text
        else:
            self.extra_text = extra_text

        try:
            first_line = text[:text.index('\n')]
        except ValueError:
            first_line = text

        self.label.font_size = self.font_size
        self.label.set_text(first_line)
        self.label.position = (0.01, (self.height - self.label.height) / 2)
        self.label.set_line_wrap(False)
        self.label.set_ellipsize(pango.ELLIPSIZE_END)

        # Set extra text
        if extra_text is not None:
            self.extra_label.font_size = self.font_size
            self.extra_label.set_text(extra_text)
            self.extra_label.position = (
                self.width * 0.98 - self.extra_label.width,
                (self.height - self.extra_label.height) / 2)

            self.label.width = (self.width - self.extra_label.width) * 0.9
        else:
            self.label.width = self.width * 0.95

        self.label.color = self.color
        if self.extra_label:
            self.extra_label.color = self.color


class AnimatingMenuItem(TextMenuItem):
    """A TextMenuItem implementing animate_in and animate_out."""

    def __init__(self, width, height, text, extra_text=None):
        TextMenuItem.__init__(self, width, height, text, extra_text)

        self.move_anchor_point_from_gravity(clutter.GRAVITY_WEST)
        self.font_size = 0.03
        self.update()

        self.timeline = clutter.Timeline(200)
        alpha = clutter.Alpha(self.timeline, clutter.EASE_IN_OUT_SINE)
        self.behaviour = FontSizeBehaviour(alpha)
        self.behaviour.apply(self)

    def animate_in(self):
        """Set labels font-size and color when an item gets selected."""
        self.behaviour.start_size = 0.03
        self.behaviour.end_size = 0.05
        self.color = "menuitem_active"
        self.timeline.start()
        self.update()

    def animate_out(self):
        """Set labels font-size and color when an item gets unselected."""
        self.color = "menuitem_inactive"
        self.update()
        self.behaviour.start_size = 0.05
        self.behaviour.end_size = 0.03
        self.timeline.start()


class TextMenu(GridMenu):
    """A grid menu that contains labels."""
    __gsignals__ = {
        'filled' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
    }

    def __init__(self, x=0, y=0, item_width=0.2, item_height=0.1):
        GridMenu.__init__(self, x, y, item_width, item_height)

        self.items_per_row = 1
        self.visible_rows = 8
        self.visible_cols = 1

        self.cursor = Selector(self.config.theme)

    def add_item(self, text, extra_text=None, data=None):
        """Add a TextMenuItem."""
        item = TextMenuItem(self._item_width, self._item_height, text,
            extra_text)
        item.userdata = data

        self.raw_add_item(item)

    def async_add(self, items):
        """
        Add asynchronously TextMenuItem using a list.

        The list should be : [[text1, extra_text1, data1], etc]

        texture1, and extra_text1 : are strings use to create a Label.
        data1: is the data that will be accessible from the menu item.
        (see MenuItem Class)
        """
        if len(items) > 0:
            item = items[0]
            self.add_item(item[0], item[1], item[2])

            # Recursive call, remove first element from the list
            gobject.timeout_add(10, self.async_add, items[1:])
        else:
            self.emit("filled")

        return False


    # XXX: This needs to be changed. A TextMenu should know nothing about
    # special artist items.
    def async_add_artists(self, items):
        """
        Add asynchronously AnimatingMenuItem using a list.
        The created AnimatingMenuItem fits artists requirements.
        See also async_add comments.
        """
        if len(items) > 0:
            item = items[0]
            menu_item = AnimatingMenuItem(self._item_width, self._item_height,
                item[0], item[1])
            menu_item.userdata = item[2]
            self.raw_add_item(menu_item)

            # Recursive call, remove first element from the list
            gobject.timeout_add(10, self.async_add_artists, items[1:])
        else:
            self.emit("filled")

        return False

