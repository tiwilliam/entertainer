# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Albums tab which displays albums and allows users to select them'''
# pylint: disable-msg=W1001

import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.image_menu import ImageMenu
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation

class AlbumsTab(Tab):
    '''Tab to show album listings'''

    def __init__(self, albums, move_to_new_screen_callback, name="albums",
        tab_title=_("Albums")):
        Tab.__init__(self, name, tab_title, move_to_new_screen_callback)

        # Start the loading animation while the menu is loading
        self.throbber = LoadingAnimation(0.6, 0.1)
        self.throbber.show()
        self.add(self.throbber)

        if len(albums) < 4:
            x_percent = 0.2928
            visible_rows = 1
            visible_cols = 3
        elif len(albums) < 13:
            x_percent = 0.1464
            visible_rows = 2
            visible_cols = 6
        else:
            x_percent = 0.1098
            visible_rows = 3
            visible_cols = 8

        # Create albums menu
        self.menu = ImageMenu(0.07, 0.16, x_percent, self.y_for_x(x_percent))
        self.menu.visible_rows = visible_rows
        self.menu.visible_cols = visible_cols
        self.menu.items_per_col = self.menu.visible_rows
        self.add(self.menu)

        albums_list = [[album.album_art_url, album] for album in albums]
        self.menu.async_add_albums(albums_list)

        self.li = ListIndicator(0.77, 0.8, 0.18, 0.045,
            ListIndicator.HORIZONTAL)
        self.li.set_maximum(len(albums))
        self.li.show()
        self.add(self.li)

        # Create album information (displays current menuitem information)
        self.album_title = Label(0.045, "title", 0.22, 0.79, "")
        self.album_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.album_title.set_line_wrap(False)
        self.album_title.width = 0.366
        self.add(self.album_title)

        self.album_artist = Label(0.037, "subtitle", 0.22, 0.86, "")
        self.album_artist.set_ellipsize(pango.ELLIPSIZE_END)
        self.album_artist.set_line_wrap(False)
        self.album_artist.width = 0.366
        self.add(self.album_artist)

        self.album_tracks = Label(0.037, "subtitle", 0.22, 0.91, "")
        self.add(self.album_tracks)

        self.connect('activated', self._on_activated)
        self.connect('deactivated', self._on_deactivated)
        self.menu.connect("moved", self._update_album_info)
        self.menu.connect("selected", self._handle_select)
        self.menu.connect("activated", self._on_activated)
        self.menu.connect("filled", self._on_menu_filled)

    def can_activate(self):
        '''Albums tab will always be created from an existing artist with at
        least one album.'''
        return True

    def _update_album_info(self, event=None):
        '''Update the album information labels.'''
        if self.active:
            album = self.menu.selected_userdata
            self.album_title.set_text(album.title)
            self.album_artist.set_text(album.artist)
            self.album_tracks.set_text(_("%(total)s tracks") % \
                {'total': len(album.tracks)})
            self.li.show()
            self.li.set_current(self.menu.selected_index + 1)
        else:
            self.album_title.set_text("")
            self.album_artist.set_text("")
            self.album_tracks.set_text("")
            self.li.hide()

    def _handle_up(self):
        '''Handle the up user event.'''
        if self.menu.on_top:
            return True # Move control back to tab bar
        else:
            self.menu.up()
            return False

    def _handle_down(self):
        '''Handle the down user event.'''
        self.menu.down()
        return False

    def _handle_left(self):
        '''Handle the left user event.'''
        self.menu.left()
        return False

    def _handle_right(self):
        '''Handle the right user event.'''
        self.menu.right()
        return False

    def _handle_select(self, event=None):
        '''Handle the select user event.'''
        album = self.menu.selected_userdata
        kwargs = { 'album' : album }
        self.callback("album", kwargs)
        return False

    def _on_activated(self, event=None):
        '''Tab activated.'''
        if self.tab_group is not None:
            self.tab_group.active = False
        self.menu.active = True
        self.active = True
        self._update_album_info()
        return False

    def _on_deactivated(self, event=None):
        '''Tab deactivated.'''
        self.active = False
        self.menu.active = False
        self._update_album_info()
        return False

    def _on_menu_filled(self, event=None):
        '''Handles filled event.'''
        self.throbber.hide()

