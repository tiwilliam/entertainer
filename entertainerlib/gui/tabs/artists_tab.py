# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Artists tab for the music screen'''
# pylint: disable-msg=W1001

import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation
from entertainerlib.gui.widgets.text_menu import TextMenu

class ArtistsTab(Tab):
    '''Tab for the music screen to show artist listings'''

    def __init__(self, music_library, artists, move_to_new_screen_callback,
        name="artists", tab_title=_("Artists")):
        Tab.__init__(self, name, tab_title, move_to_new_screen_callback)
        self.library = music_library

        # Start the loading animation while the menu is loading
        self.throbber = LoadingAnimation(0.1, 0.1)
        self.throbber.show()
        self.add(self.throbber)

        self.menu = TextMenu(0.057, 0.208, 0.293, 0.078)
        self.menu.items_per_row = 3
        self.menu.visible_rows = 7
        self.menu.visible_cols = 3
        self.menu.active = False
        self.menu.cursor = None
        self.add(self.menu)

        artists_list = [[artist, None, artist] for artist in artists]
        self.menu.async_add_artists(artists_list)

        # Create artist label
        self.artist_title = Label(0.0416, "title", 0.22, 0.794, "")
        self.artist_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.artist_title.set_line_wrap(False)
        self.artist_title.width = 0.366
        self.add(self.artist_title)

        self.artist_albums = Label(0.0365, "subtitle", 0.22, 0.86, "")
        self.add(self.artist_albums)

        self.artist_tracks = Label(0.0365, "subtitle", 0.22, 0.911, "")
        self.add(self.artist_tracks)

        # Create artist menu list indicator
        self.li = ListIndicator(0.77, 0.8, 0.18, 0.045,
            ListIndicator.VERTICAL)
        self.li.set_maximum(len(artists))
        self.add(self.li)

        self.connect('activated', self._on_activated)
        self.connect('deactivated', self._on_deactivated)
        self.menu.connect("moved", self._update_artist_info)
        self.menu.connect("selected", self._handle_select)
        self.menu.connect("activated", self._on_activated)
        self.menu.connect("filled", self._on_menu_filled)

    def can_activate(self):
        '''Albums tab will always be created from an existing artist with at
        least one album.'''
        return True

    def _update_artist_info(self, event=None):
        '''Update the artist information labels'''
        if self.active:
            artist = self.menu.selected_userdata
            self.artist_title.set_text(artist)
            self.artist_albums.set_text(_("%(albums)d albums") %
                {'albums': self.library.number_of_albums_by_artist(artist)})
            self.artist_tracks.set_text(_("%(tracks)d tracks") %
                {'tracks': self.library.number_of_tracks_by_artist(artist)})
            self.li.show()
            self.li.set_current(self.menu.selected_index + 1)
        else:
            self.artist_title.set_text("")
            self.artist_albums.set_text("")
            self.artist_tracks.set_text("")
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
        artist = self.menu.selected_userdata
        kwargs = { 'artist' : artist }
        self.callback("artist", kwargs)
        return False

    def _on_activated(self, event=None):
        '''Tab activated.'''
        if self.tab_group is not None:
            self.tab_group.active = False
        self.menu.active = True
        self.active = True
        self._update_artist_info()
        return False

    def _on_deactivated(self, event=None):
        '''Tab deactivated.'''
        self.active = False
        self.menu.active = False
        self._update_artist_info()

    def _on_menu_filled(self, event=None):
        '''Handles filled event.'''
        self.throbber.hide()

