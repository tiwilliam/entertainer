# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Currently playing tab for the audio screen.'''

import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.progress_bar import ProgressBar

class PlayingTab(Tab):
    '''Tab for the audio play screen to show currently playing audio.'''

    def __init__(self, media_player, track, name="playing",
            tab_title=_("Currently playing")):
        Tab.__init__(self, name, tab_title)

        album = track.album

        # Track name
        if track.number == 0:
            track_label_text = track.title
        else:
            track_label_text =  _("From %(number)d. %(title)s") % \
                {'number': track.number, 'title': track.title}

        self.track_label = Label(0.05, "text", 0.5, 0.33, track_label_text)
        self.track_label.set_ellipsize(pango.ELLIPSIZE_END)
        self.track_label.width = 0.4
        self.add(self.track_label)

        # Album name
        if album.year == 0:
            album_label_text = _("From %(title)s") % {'title': album.title}
        else:
            album_label_text = _("From %(title)s, %(year)s") % \
                {'title': album.title, 'year': album.year}

        self.album_label = Label(0.042, "subtitle", 0.5, 0.43, album_label_text)
        self.album_label.set_ellipsize(pango.ELLIPSIZE_END)
        self.album_label.width = 0.4
        self.add(self.album_label)

        # Artist name
        artist_text = _("By %(artist)s") % {'artist': track.artist}
        self.artist_label = Label(0.042, "subtitle", 0.5, 0.53, artist_text)
        self.artist_label.set_ellipsize(pango.ELLIPSIZE_END)
        self.artist_label.width = 0.4
        self.add(self.artist_label)

        self.progress_bar = ProgressBar(0.5, 0.667, 0.4, 0.04)
        self.progress_bar.media_player = media_player
        self.add(self.progress_bar)

    def update(self, track):
        '''
        Called when currently playing changes tracks. The provided track
        is used to update all the necessary labels.
        '''
        album = track.album

        if track.number == 0:
            self.track_label.set_text(track.title)
        else:
            self.track_label.set_text(str(track.number) + ". " + track.title)

        if album.year != 0:
            self.album_label.set_text(_("From %(title)s, %(year)s") % \
            {'title': album.title, 'year': album.year})
        else:
            self.album_label.set_text(_("From %(album)s") % \
                {'album': album.title})
            self.artist_label.set_text(_("By %(artist)s") % \
                {'artist': track.artist})

    def can_activate(self):
        '''No interaction is available on the PlayingTab.'''
        return False

