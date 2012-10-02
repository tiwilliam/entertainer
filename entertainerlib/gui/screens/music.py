# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Music - Screen allows user to select music he/she wants to listen'''

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.tabs.albums_tab import AlbumsTab
from entertainerlib.gui.tabs.artists_tab import ArtistsTab
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.client.medialibrary.playlist import Playlist


class Music(Screen):
    '''Screen that allows user to browse music library content.'''

    def __init__(self, media_player, music_library,
        move_to_new_screen_callback):
        Screen.__init__(self, 'Music', move_to_new_screen_callback,
            has_tabs=True)

        self.media_player = media_player
        self.theme = self.config.theme
        self.music_library = music_library

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, _("Music"))
        self.add(screen_title)

        if self.music_library.number_of_tracks() == 0:
            self._create_no_music_information()
        else:
            tab1 = ArtistsTab(music_library, music_library.get_all_artists(),
                move_to_new_screen_callback)
            tab2 = AlbumsTab(music_library.get_all_albums(),
                move_to_new_screen_callback)

            self.add_tab(tab1)
            self.add_tab(tab2)

    def _create_no_music_information(self):
        """
        Create textures and labels for information screen. This is displayed
        instead of artist list if there are no tracks available and it helps
        users to add new music to the system.
        """
        # Create warning icon
        warning_icon = Texture(self.theme.getImage("warning_icon"), 0.28, 0.27)
        self.add(warning_icon)

        # Create warning title
        info_title = Label(0.0625, "title", 0.3367, 0.2709,
            _("No music available!"))
        self.add(info_title)

        # Create warning help text
        message = _(
            "There are no indexed artists in the Entertainer media "
            "library. To add music, start the Content management tool "
            "and open the 'Music' tab. Now click on the 'Add' button and "
            "select some folders which contain music files.")
        info = Label(0.0417, "menuitem_inactive", 0.2804, 0.45, message)
        info.width = 0.5
        self.add(info)

    def is_interested_in_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        @return: Boolean
        """
        if self.tab_group.tab("artists").active or \
            self.tab_group.tab("albums").active:
            return True
        else:
            return False

    def execute_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        """
        if self.tab_group.tab("artists").active:
            artist = self.tab_group.tab("artists").selected_artist
            self.media_player.set_playlist(Playlist(
                self.music_library.get_tracks_by_artist(artist)))
            self.media_player.play()
        elif self.tab_group.tab("albums").active:
            album = self.tab_group.tab("albums").selected_album
            self.media_player.set_playlist(Playlist(album.tracks))
            self.media_player.play()

    def handle_user_event(self, event):
        '''Handle screen specific user events unless the library is empty.'''
        if self.music_library.number_of_tracks() == 0:
            return
        else:
            Screen.handle_user_event(self, event)

