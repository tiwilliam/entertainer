# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Lyrics tab for the audio play screen'''

import clutter
import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.loading_animation import (
    LoadingAnimation)
from entertainerlib.gui.widgets.scroll_area import ScrollArea

class LyricsTab(Tab):
    '''Tab for the audio play screen to show lyrics'''

    def __init__(self, music_library, track, name="lyrics",
        tab_title=_("Lyrics")):
        Tab.__init__(self, name, tab_title)
        self.track = track
        self.lyrics_area = None
        self.library = music_library
        self.lyrics_text = ""

        if self.track.has_lyrics():
            self.lyrics_text = self.track.lyrics
            lyrics = Label(0.037, "subtitle", 0, 0, self.lyrics_text)
            lyrics.set_line_wrap_mode(pango.WRAP_WORD)
            lyrics.width = 0.366

            self.lyrics_area = ScrollArea(0.5, 0.23, 0.4, 0.57, lyrics)
            self.lyrics_area.connect("activated", self._on_activated)
            self.add(self.lyrics_area)

            self.connect('activated', self._on_activated)
            self.connect('deactivated', self._on_deactivated)
        else:
            # Display throbber animation while searching for lyrics
            self.throbber = LoadingAnimation(0.7, 0.5, 0.1)
            self.throbber.show()
            self.add(self.throbber)
            self.track.fetch_lyrics(self._lyrics_search_callback)

    def _lyrics_search_callback(self, lyrics_text):
        '''This function is called when lyrics search is over.'''
        self.throbber.hide()

        # Save the results to help determine if the tab can activate.
        self.lyrics_text = lyrics_text

        if lyrics_text == "":
            no_lyrics = Label(0.037, "title", 0.7, 0.5,
                _("No lyrics found for this track"))
            no_lyrics.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            self.add(no_lyrics)
        else:
            lyrics = Label(0.037, "subtitle", 0, 0, lyrics_text)
            lyrics.set_line_wrap_mode(pango.WRAP_WORD)
            lyrics.width = 0.366

            self.lyrics_area = ScrollArea(0.5, 0.23, 0.4, 0.57, lyrics)
            self.lyrics_area.connect("activated", self._on_activated)
            self.add(self.lyrics_area)
            self.library.save_lyrics(self.track, lyrics_text)

    def can_activate(self):
        '''
        Lyrics tab can scroll the lyrics listing only if lyrics were found.
        '''
        if self.lyrics_text == "":
            return False
        else:
            return True

    def _handle_up(self):
        '''Handle the up user event.'''
        if self.lyrics_area.on_top:
            return True # Move control back to tab bar
        else:
            return self.lyrics_area.scroll_up()

    def _handle_down(self):
        '''Handle the down user event.'''
        return self.lyrics_area.scroll_down()

    def _on_activated(self, event=None):
        '''Tab activated.'''
        if self.tab_group is not None:
            self.tab_group.active = False
        self.lyrics_area.active = True
        self.active = True
        return False

    def _on_deactivated(self, event=None):
        '''Tab deactivated.'''
        self.active = False
        self.lyrics_area.active = False
        return False

