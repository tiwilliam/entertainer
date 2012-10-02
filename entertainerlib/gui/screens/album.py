# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Album - Screen allows user to browse and play tracks of the album'''

import gtk
import clutter
import pango

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.eyecandy_texture import EyeCandyTexture
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.text_menu import TextMenu

class Album(Screen):
    '''Screen that allows user to browse and play tracks of the music album.'''

    def __init__(self, media_player, music_library, move_to_new_screen_callback,
        album):
        Screen.__init__(self, 'Album', move_to_new_screen_callback)

        self.media_player = media_player
        self.theme = self.config.theme
        self.library = music_library
        self.album = album
        self.art = None
        self.track_menu = None

        # Create and initialize screen items
        self.track_menu = self._create_track_menu()
        self.add(self.track_menu)
        self._create_album_cover_texture()
        self._create_album_info()

        self.screen_title = Label(0.13, "screentitle", 0, 0.87, "")
        self.screen_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.screen_title.width = 0.8
        self.add(self.screen_title)

        #List indicator
        self.li = ListIndicator(0.74, 0.85, 0.2, 0.045, ListIndicator.VERTICAL)
        self.li.set_maximum(len(self.album.tracks))
        self.add(self.li)

        self.track_menu.active = True
        self.track_menu.connect('selected', self._on_menu_selected)
        self.track_menu.connect('moved', self._display_selected_track)

    def _create_album_cover_texture(self):
        """
        Create a texture that is displayed next to track list. This texture
        displays album cover art.
        """
        if(self.album.has_album_art()):
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.album.album_art_url)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(
                self.theme.getImage("default_album_art"))
        self.art = EyeCandyTexture(0.1, 0.13, 0.3148, 0.5599, pixbuf)
        self.art.set_rotation(clutter.Y_AXIS, 25, 0, 0, 0)
        self.add(self.art)

    def _create_album_info(self):
        """
        Create album info labels.
        """
        if self.album.year != 0:
            album_text = self.album.title + ", " + str(self.album.year)
        else:
            album_text = self.album.title
        album = Label(0.0416, "text", 0.5, 0.13, album_text, font_weight="bold")
        album.set_ellipsize(pango.ELLIPSIZE_END)
        album.set_line_wrap(False)
        album.width = 0.45
        self.add(album)

        length = str(self.album.length / 60)
        num_of_tracks_text = _("%(total)s tracks, %(time)s minutes") % \
            {'total': len(self.album.tracks), 'time': length}
        num_of_tracks = Label(0.028, "subtitle", 0.5, 0.18,
            num_of_tracks_text, font_weight="bold")
        self.add(num_of_tracks)

    def _create_track_menu(self):
        """
        Create track menu. This menu contains list of all tracks on album.
        """
        menu = TextMenu(0.4978, 0.2344, 0.4393, 0.0781)

        tracks = self.album.tracks
        tracks_list = [[track.title, track.length_string, track] \
            for track in tracks]
        menu.async_add(tracks_list)

        return menu

    def is_interested_in_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        """
        return True

    def execute_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        """
        track = self.track_menu.selected_userdata
        self.media_player.set_media(track)
        self.media_player.play()

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        self.track_menu.up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        self.track_menu.down()

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        track = self.track_menu.selected_userdata
        kwargs = { 'track' : track }
        self.callback("audio_play", kwargs)

    def _on_menu_selected(self, actor=None):
        '''Handle a *select command* if an item was selected.'''
        self._handle_select()

    def _display_selected_track(self, actor=None):
        '''Update of the list indicator and the screen's title'''
        self.li.set_current(self.track_menu.selected_index + 1)
        track = self.track_menu.selected_userdata
        self.screen_title.set_text(track.artist)
        self.screen_title.show()

