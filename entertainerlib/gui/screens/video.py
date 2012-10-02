# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Video - Screen allows user to browse video library content'''

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.tabs.movies_tab import MoviesTab
from entertainerlib.gui.tabs.series_tab import SeriesTab
from entertainerlib.gui.tabs.video_clips_tab import VideoClipsTab
from entertainerlib.gui.widgets.label import Label


class Video(Screen):
    '''Screen contains tabs for different video types in the video library.'''

    def __init__(self, media_player, video_library,
        move_to_new_screen_callback):
        Screen.__init__(self, 'Video', has_tabs=True)

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, _("Videos"))
        self.add(screen_title)

        # Tabs
        tab1 = MoviesTab(video_library, move_to_new_screen_callback)
        tab2 = SeriesTab(video_library, move_to_new_screen_callback)
        tab3 = VideoClipsTab(media_player, video_library,
            move_to_new_screen_callback)

        self.add_tab(tab1)
        self.add_tab(tab2)
        self.add_tab(tab3)

