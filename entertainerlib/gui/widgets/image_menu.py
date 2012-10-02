# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Implements a grid menu that contains images'''

import clutter
import gtk
import gobject

from entertainerlib.gui.widgets.grid_menu import GridMenu
from entertainerlib.gui.widgets.menu_item import MenuItem
from entertainerlib.gui.widgets.rounded_texture import RoundedTexture
from entertainerlib.gui.widgets.texture import Texture

class ImageMenuItem(MenuItem):
    """A menuitem widget that contains a Texture."""

    def __init__(self, width, height, texture):
        MenuItem.__init__(self)

        item_width = self.get_abs_x(width)
        item_height = self.get_abs_y(height)

        self.original_ratio = float(texture.get_width())
        self.original_ratio /= texture.get_height()
        item_ratio = float(item_width) / float(item_height)

        margin = 0.95

        if item_ratio >= self.original_ratio:
            texture_width = self.original_ratio * item_height
            texture_height = item_height
            texture_width *= margin
            texture_height *= margin
            delta_width = item_width - texture_width
            delta_height = item_height - texture_height
        else:
            texture_width = item_width
            texture_height = item_width / self.original_ratio
            texture_width *= margin
            texture_height *= margin
            delta_width = item_width - texture_width
            delta_height = item_height - texture_height

        item_x = delta_width / 2.0
        item_y = delta_height / 2.0

        texture.set_position(int(item_x), int(item_y))
        texture.set_size(int(texture_width), int(texture_height))

        self.add(texture)


class ImageMenu(GridMenu):
    """A grid menu that contains images."""
    __gsignals__ = {
        'filled' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
    }

    def __init__(self, x=0, y=0, item_width=0.2, item_height=0.1):
        GridMenu.__init__(self, x, y, item_width, item_height)

        self.cursor_below = False
        self.horizontal = True
        self.items_per_col = 4
        self.visible_rows = 3
        self.visible_cols = 5

        c = clutter.Rectangle()
        c.set_size(100, 100)
        c.set_color((255, 255, 255, 128))
        self.cursor = c

        pix_buffer = gtk.gdk.pixbuf_new_from_file(
            self.config.theme.getImage("default_movie_art"))
        self.movie_default = RoundedTexture(0.0, 0.0, 0.1, 0.25, pix_buffer)
        self.movie_default.hide()
        self.add(self.movie_default)

        self.album_default = Texture(
            self.config.theme.getImage("default_album_art"))
        self.album_default.hide()
        self.add(self.album_default)

    def add_item(self, texture, data):
        """Add a ImageMenuItem from a Texture."""
        item = ImageMenuItem(self._item_width, self._item_height, texture)
        item.userdata = data

        self.raw_add_item(item)

    def async_add(self, items):
        """
        Add asynchronously ImageMenuItem using a list.

        The list should be : [[texture1, data1], [texture2, data2], etc]

        texture1, texture2 : are Texture objects.
        data1, data2: are the data that will be accessible from the menu item.
        (see MenuItem Class)
        """
        if len(items) > 0:
            item = items[0]
            self.add_item(item[0], item[1])

            # Recursive call, remove first element from the list
            gobject.timeout_add(15, self.async_add, items[1:])
        else:
            self.emit("filled")

        return False

    # XXX: This needs to be changed. An ImageMenu should know nothing about
    # special video items.
    def async_add_videos(self, items):
        """
        Add asynchronously ImageMenuItem using a list.
        The created ImageMenuItem fits movies and series requirements.
        See also async_add comments.
        """
        if len(items) > 0:
            item = items[0]
            if item[1].has_cover_art():
                pix_buffer = gtk.gdk.pixbuf_new_from_file(item[0])
                texture = RoundedTexture(0.0, 0.0, 0.1, 0.25, pix_buffer)
            else:
                texture = clutter.Clone(self.movie_default)

            self.add_item(texture, item[1])

            # Recursive call, remove first element from the list
            gobject.timeout_add(10, self.async_add_videos, items[1:])
        else:
            self.emit("filled")

        return False

    # XXX: This needs to be changed. An ImageMenu should know nothing about
    # special album items.
    def async_add_albums(self, items):
        """
        Add asynchronously ImageMenuItem using a list.
        The created ImageMenuItem fits albums requirements.
        See also async_add comments.
        """
        if len(items) > 0:
            item = items[0]
            if item[1].has_album_art():
                texture = Texture(item[0])
            else:
                texture = clutter.Clone(self.album_default)

            self.add_item(texture, item[1])

            # Recursive call, remove first element from the list
            gobject.timeout_add(10, self.async_add_albums, items[1:])
        else:
            self.emit("filled")

        return False

    # XXX: This needs to be changed. An ImageMenu should know nothing about
    # special clip items.
    def async_add_clips(self, items):
        """
        Add asynchronously ImageMenuItem using a list.
        The created ImageMenuItem fits clips requirements.
        See also async_add comments.
        """
        if len(items) > 0:
            item = items[0]
            pix_buffer = gtk.gdk.pixbuf_new_from_file(item[0])
            texture = RoundedTexture(0.0, 0.0, 0.23, self.y_for_x(0.23) * 0.7,
                pix_buffer)

            self.add_item(texture, item[1])

            # Recursive call, remove first element from the list
            gobject.timeout_add(10, self.async_add_clips, items[1:])
        else:
            self.emit("filled")

        return False

