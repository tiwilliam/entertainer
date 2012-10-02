# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tracks tab for the artist screen'''

import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation
from entertainerlib.gui.widgets.text_menu import TextMenu

class TracksTab(Tab):
    '''Tab for the artist screen to show track listings'''

    def __init__(self, tracks, move_to_new_screen_callback, name="tracks",
        tab_title=_("Tracks")):
        Tab.__init__(self, name, tab_title, move_to_new_screen_callback)

        # Start the loading animation while the menu is loading
        self.throbber = LoadingAnimation(0.1, 0.1)
        self.throbber.show()
        self.add(self.throbber)

        self.menu = TextMenu(0.0586, 0.2083, 0.2928, 0.0781)
        self.menu.items_per_row = 3
        self.menu.visible_rows = 7
        self.menu.visible_cols = 3
        self.menu.active = False
        self.menu.cursor = None
        self.add(self.menu)

        tracks_list = [[track.title, None, track] for track in tracks]
        self.menu.async_add_artists(tracks_list)

        self.track_title = Label(0.045, "title", 0.22, 0.79, "")
        self.track_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.track_title.set_line_wrap(False)
        self.track_title.width = 0.366
        self.add(self.track_title)

        self.track_number = Label(0.037, "subtitle", 0.22, 0.86, "")
        self.track_number.set_ellipsize(pango.ELLIPSIZE_END)
        self.track_number.set_line_wrap(False)
        self.track_number.width = 0.366
        self.add(self.track_number)

        self.track_length = Label(0.037, "subtitle", 0.22, 0.91, "")
        self.add(self.track_length)

        self.li = ListIndicator(0.77, 0.8, 0.18, 0.045,
            ListIndicator.VERTICAL)
        self.li.set_maximum(len(tracks))
        self.li.show()
        self.add(self.li)

        self.connect('activated', self._on_activated)
        self.connect('deactivated', self._on_deactivated)
        self.menu.connect("moved", self._update_track_info)
        self.menu.connect("selected", self._handle_select)
        self.menu.connect("activated", self._on_activated)
        self.menu.connect("filled", self._on_menu_filled)

    def can_activate(self):
        '''Tracks tab will always be created from an existing artist with at
        least one track.'''
        return True

    def _update_track_info(self, event=None):
        '''Update the track information labels'''
        if self.active:
            track = self.menu.selected_userdata
            self.track_title.set_text(track.title)
            self.track_length.set_text(track.length_string)
            self.track_number.set_text(_("Track %(track)d from %(album)s") % \
                {'track': track.number, 'album': track.album.title})
            self.li.show()
            self.li.set_current(self.menu.selected_index + 1)
        else:
            self.track_title.set_text("")
            self.track_length.set_text("")
            self.track_number.set_text("")
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
        track = self.menu.selected_userdata
        kwargs = { 'track' : track }
        self.callback("audio_play", kwargs)
        return False

    def _on_activated(self, event=None):
        '''Tab activated.'''
        if self.tab_group is not None:
            self.tab_group.active = False
        self.menu.active = True
        self.active = True
        self._update_track_info()
        return False

    def _on_deactivated(self, event=None):
        '''Tab deactivated.'''
        self.active = False
        self.menu.active = False
        self._update_track_info()
        return False

    def _on_menu_filled(self, event=None):
        '''Handles filled event.'''
        self.throbber.hide()

