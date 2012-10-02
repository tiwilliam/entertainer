# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''AudioPlay - Screen displays information of currently playing audio'''
# pylint: disable-msg=W0221

import gtk
import clutter

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.tabs.lyrics_tab import LyricsTab
from entertainerlib.gui.tabs.playing_tab import PlayingTab
from entertainerlib.gui.widgets.eyecandy_texture import (
    EyeCandyTexture)

class AudioPlay(Screen):
    '''Screen that displays information of currently playing audio track.'''

    def __init__(self, media_player, music_library, track):
        Screen.__init__(self, 'AudioPlay', has_tabs=True)

        self.theme = self.config.theme
        album = track.album

        # Create album art (this is displayed on all tab pages
        if(album.has_album_art()):
            pixbuf = gtk.gdk.pixbuf_new_from_file(album.album_art_url)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(
                self.theme.getImage("default_album_art"))
        self.art = EyeCandyTexture(0.1, 0.22, 0.3148, 0.5599, pixbuf)
        self.art.set_rotation(clutter.Y_AXIS, 25, 0, 0, 0)
        self.add(self.art)

        media_player.set_media(track)
        media_player.play()

        # Tabs
        tab1 = PlayingTab(media_player, track)
        tab2 = LyricsTab(music_library, track)
        self.add_tab(tab1)
        self.add_tab(tab2)

    def update(self, track, event=None):
        '''Called when currently playing changes tracks. The provided track
        is used to update all the necessary labels'''
        self.tab_group.tab("playing").update(track)

