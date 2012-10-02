# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Artist - Screen allows user to browse music of one specific artist'''

import pango

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.tabs.albums_tab import AlbumsTab
from entertainerlib.gui.tabs.tracks_tab import TracksTab
from entertainerlib.gui.widgets.label import Label
from entertainerlib.client.medialibrary.playlist import Playlist

class Artist(Screen):
    '''Screen that allows user to browse music by artist.'''

    def __init__(self, media_player, music_library, artist,
        move_to_new_screen_callback):
        Screen.__init__(self, 'Artist', move_to_new_screen_callback,
            has_tabs=True)
        self.media_player = media_player

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, artist)
        screen_title.set_ellipsize(pango.ELLIPSIZE_END)
        screen_title.width = 1
        self.add(screen_title)

        # Tabs
        albums = music_library.get_albums_by_artist(artist)
        if albums:
            tab1 = AlbumsTab(albums, move_to_new_screen_callback)
            self.add_tab(tab1)

        tracks = music_library.get_tracks_by_artist(artist)
        if tracks:
            tab2 = TracksTab(tracks, move_to_new_screen_callback)
            self.add_tab(tab2)

    def is_interested_in_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        """
        if self.tab_group.tab("albums").active:
            return True
        else:
            return False

    def execute_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        """
        album = self.tab_group.tab("albums").selected_album
        self.media_player.set_playlist(Playlist(album.tracks))
        self.media_player.play()

