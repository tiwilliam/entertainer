# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''TvSeries - Screen allows user to browse seasons of one TV series'''

import gtk

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.eyecandy_texture import EyeCandyTexture
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.text_menu import TextMenu

class TvSeries(Screen):
    '''Screen that contains all seasons of one TV series.'''

    def __init__(self, video_library, move_to_new_screen_callback, tv_series):
        Screen.__init__(self, 'TvSeries', move_to_new_screen_callback)

        self.theme = self.config.theme
        self.tv_series = tv_series
        self.video_library = video_library

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, self.tv_series.title)
        self.add(screen_title)

        self.art = None
        self.menu = None
        self._create_series_cover_texture()
        self.menu = self._create_season_menu()
        self.add(self.menu)

        #List indicator
        self.li = ListIndicator(0.8, 0.9, 0.2, 0.045, ListIndicator.VERTICAL)
        self.li.set_maximum(len(self.tv_series.seasons))
        self.add(self.li)

        self.menu.connect("moved", self._update_season_info)
        self.menu.connect("selected", self._handle_select)

    def _create_season_menu(self):
        """
        Create a list of available seasons
        """
        menu = TextMenu(0.4978, 0.1563, 0.4393, 0.0781)

        seasons = self.tv_series.seasons
        seasons.sort()

        seasons_list = [[_("Season %(num)s") % {'num': season}, None, season] \
            for season in seasons]
        menu.async_add(seasons_list)

        menu.active = True

        return menu

    def _create_series_cover_texture(self):
        """
        Create a texture that is displayed next to track list. This texture
        displays album cover art.
        """
        if(self.tv_series.has_cover_art()):
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.tv_series.cover_art_url)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(
                self.theme.getImage("default_movie_art"))
        self.art = EyeCandyTexture(0.16, 0.15, 0.2196, 0.5859, pixbuf)
        self.add(self.art)

    def _update_season_info(self, event=None):
        '''Update the ListIndicator.'''
        self.li.set_current(self.menu.selected_index + 1)

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        self.menu.up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        self.menu.down()

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        season = self.menu.selected_userdata
        episodes = self.video_library.get_episodes_from_season(
            self.tv_series.title, season)
        kwargs = { 'episodes' : episodes, 'tv_series' : self.tv_series }
        self.callback("tv_episodes", kwargs)

