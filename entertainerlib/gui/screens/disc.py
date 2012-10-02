# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Disc - Screen allows user to browse and play tracks from CD album.'''

import os

import cdrom
import gtk
import gobject
import pango
import clutter

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.eyecandy_texture import EyeCandyTexture
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.gui.widgets.text_menu import TextMenu
from entertainerlib.client.medialibrary.playlist import Playlist
from entertainerlib.download import AlbumArtDownloader

class Disc(Screen):
    '''Screen allows user to play tracks from the current Audio CD.'''

    def __init__(self, music_library, media_player):
        Screen.__init__(self, 'Disc')

        self.theme = self.config.theme
        self.music_library = music_library
        self.media_player = media_player
        # When album info is loaded we create Playlist object
        self.playlist = None

        self.art = None
        self.art2 = None
        self.in_behaviour = None
        self.out_behaviour = None
        self.li = None
        self.track_menu = None

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, _("Audio Disc"),
            "screen_title")
        self.add(screen_title)

        # Display throbber animation while loading CD metadata
        self.throbber = LoadingAnimation(0.5, 0.5, 0.1)
        self.throbber.show()
        self.add(self.throbber)

        # Create and initialize screen items
        self.has_disc = True
        gobject.timeout_add(500, self._get_disc_information)

    def _get_disc_information(self):
        """
        Fetch album information from the Internet and create widgets based
        on received data.
        """
        try:
            disc = self.music_library.get_compact_disc_information()

            title = disc.title
            artist = disc.artist
            tracks = disc.tracks

            self.playlist = Playlist(tracks)
            self._create_album_info(title, artist, tracks, disc.length)
            self.track_menu = self._create_track_menu(tracks)
            self.add(self.track_menu)
            self._create_album_cover_texture(artist, title)

            self.li = ListIndicator(0.75, 0.8, 0.2, 0.045,
                ListIndicator.VERTICAL)
            self.li.set_maximum(len(tracks))
            self.add(self.li)

            art_file = os.path.join(self.config.ALBUM_ART_DIR,
                artist + " - " + title + ".jpg")
            if artist != "Unknown artist" and not os.path.exists(art_file):
                art_search = AlbumArtDownloader(title, artist,
                    self.config.ALBUM_ART_DIR, self._update_albumart)
                art_search.start()

        except cdrom.error:
            # No disc in drive
            self.has_disc = False
            no_disc = Label(0.05, "title", 0.5, 0.5,
                _("No audio disc in drive"))
            no_disc.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            self.add(no_disc)

        # Remove loading animation
        self.throbber.hide()
        self.remove(self.throbber)
        del self.throbber

        # This function should be called only once (gobject timeout)
        return False

    def _update_albumart(self, artist, title):
        """
        Search album art for current audio disc. This function is called only
        if album art doesn't exist already. If album art is found then we
        replace current disc icon with the new album art.
        @param artist: Artist name
        @param title: Album title
        """
        art_file = os.path.join(self.config.ALBUM_ART_DIR,
            artist + " - " + title + ".jpg")

        if os.path.exists(art_file):
            clutter.threads_enter()
            self.art2 = Texture(art_file, 0.1, 0.165)
            clutter.threads_leave()

            self.art2.set_size(self.get_abs_x(0.3148), self.get_abs_y(0.5599))
            self.art2.set_opacity(0)
            self.add(self.art2)

            timeline_in = clutter.Timeline(35, 26)
            alpha_in = clutter.Alpha(timeline_in, clutter.smoothstep_inc_func)
            self.in_behaviour = clutter.BehaviourOpacity(0, 255, alpha_in)
            self.in_behaviour.apply(self.art2)

            timeline_out = clutter.Timeline(35, 26)
            alpha_out = clutter.Alpha(timeline_out, clutter.smoothstep_inc_func)
            self.out_behaviour = clutter.BehaviourOpacity(255, 0, alpha_out)
            self.out_behaviour.apply(self.art)

            timeline_out.start()
            timeline_in.start()

    def _create_album_cover_texture(self, artist, title):
        """
        Create a texture that is displayed next to track list. This texture
        displays album cover art.
        @param artist: Artist
        @param title: Title of the album
        """
        coverfile = os.path.join(self.config.ALBUM_ART_DIR,
            artist + " - " + title + ".jpg")

        if(os.path.exists(coverfile)):
            pixbuf = gtk.gdk.pixbuf_new_from_file(coverfile)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.theme.getImage("disc"))
        self.art = EyeCandyTexture(0.1, 0.13, 0.3148, 0.5599, pixbuf)
        self.art.set_rotation(clutter.Y_AXIS, 25, 0, 0, 0)
        self.add(self.art)

    def _create_album_info(self, title, artist_name, tracks, length):
        """
        Create album info labels.
        @param title: Album title
        @param artist_name: Artist
        @param tracks: List of CompactDisc objects
        """
        album = Label(0.04167, "text", 0.50146, 0.13,
           artist_name + " - " + title, font_weight="bold")
        album.set_size(0.4393, 0.06510)
        album.set_ellipsize(pango.ELLIPSIZE_END)
        self.add(album)

        minutes = str(length / 60)

        num_of_tracks = Label(0.02604, "subtitle", 0.50146, 0.18,
            _("%(total)s tracks, %(time)s minutes") % \
            {'total': len(tracks), 'time': minutes}, font_weight="bold")
        self.add(num_of_tracks)

    def _create_track_menu(self, tracks):
        """
        Create a track menu. This menu contains list of all tracks on album.
        @param tracks: List of CompactDisc objects
        """
        menu = TextMenu(0.4978, 0.2344, 0.4393, 0.0781)
        menu.visible_rows = 7

        tracks_list = [[track.title, track.length_string, index] \
            for index, track in enumerate(tracks)]
        menu.async_add(tracks_list)

        menu.active = True
        menu.connect('selected', self._handle_select)
        menu.connect('moved', self._display_selected_track)

        return menu

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        self.track_menu.up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        self.track_menu.down()

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        track_index = self.track_menu.selected_userdata
        self.playlist.set_current(track_index)
        self.media_player.set_playlist(self.playlist)
        self.media_player.play()

    def handle_user_event(self, event):
        '''Handle user events unless there is no disc.'''
        if self.has_disc:
            Screen.handle_user_event(self, event)

    def _display_selected_track(self, event=None):
        '''Update of the list indicator.'''
        self.li.set_current(self.track_menu.selected_index + 1)

