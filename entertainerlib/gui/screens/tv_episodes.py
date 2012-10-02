# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''TvEpisodes - Screen allows user to browse episodes of a season'''

import gtk
import pango

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.eyecandy_texture import EyeCandyTexture
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.text_menu import TextMenu
from entertainerlib.gui.widgets.scroll_area import ScrollArea

class TvEpisodes(Screen):
    '''Screen contains list of all episodes of one specific season.'''

    def __init__(self, media_player, move_to_new_screen_callback, episodes,
        tv_series):
        Screen.__init__(self, 'TvEpisodes', move_to_new_screen_callback)

        self.episodes = episodes
        self.media_player = media_player
        self.theme = self.config.theme
        self.tv_series = tv_series

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, self.tv_series.title)
        self.add(screen_title)

        self.scroll_area = None
        self.title = None
        self.thumb = None
        self.menu = self._create_episode_menu()
        self.add(self.menu)
        self._create_episode_info_box()

        #List indicator
        self.li = ListIndicator(0.8, 0.9, 0.2, 0.045, ListIndicator.VERTICAL)
        self.li.set_maximum(len(self.episodes))
        self.add(self.li)

        self.menu.connect("moved", self._update_episode_info)
        self.menu.connect("selected", self._handle_select)
        self.menu.connect("activated", self._on_menu_activated)

    def _create_episode_menu(self):
        """Create a list of available seasons."""
        menu = TextMenu(0.4978, 0.1563, 0.4393, 0.0781)

        episodes_list = [[_("%(num)d. %(title)s") % \
            {'num': episode.number, 'title': episode.title},
            None, episode] for episode in self.episodes]
        menu.async_add(episodes_list)

        menu.active = True

        return menu

    def _create_thumbnail_texture(self):
        """Create a thumbnail texture. This is called as menu is scrolled."""
        if self.thumb:
            self.thumb.hide()

        # Thumbnail. Use cover art if thumbnail doesn't exist
        thumbnail = self.menu.selected_userdata.thumbnail_url
        if(thumbnail is not None):
            pixbuf = gtk.gdk.pixbuf_new_from_file(thumbnail)
            thumb_width = 0.2928
            thumb_height = 0.2799
            thumb_x = 0.05
            thumb_y = 0.2
        else:
            thumb_width = 0.1098
            thumb_height = 0.2799
            thumb_x = 0.20
            thumb_y = 0.15
            if(self.tv_series.has_cover_art()):
                pixbuf = gtk.gdk.pixbuf_new_from_file(
                    self.tv_series.cover_art_url)
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file(
                    self.theme.getImage("default_movie_art"))

        self.thumb = EyeCandyTexture(thumb_x, thumb_y, thumb_width,
            thumb_height, pixbuf)
        self.add(self.thumb)

    def _create_episode_info_box(self):
        """
        Create a texture that is displayed next to track list. This texture
        displays album cover art.
        """
        self._create_thumbnail_texture()

        # Title
        self.title = Label(0.04, "title", 0.05, 0.55,
            self.menu.selected_userdata.title, font_weight="bold")
        self.title.set_ellipsize(pango.ELLIPSIZE_END)
        self.title.set_line_wrap(False)
        self.title.width = 0.4
        self.add(self.title)

        # Plot
        plot = Label(0.029, "subtitle", 0, 0, self.menu.selected_userdata.plot)
        plot.width = 0.4

        self.scroll_area = ScrollArea(0.05, 0.63, 0.4, 0.15, plot)
        self.scroll_area.connect("activated", self._on_scroll_area_activated)
        self.add(self.scroll_area)

    def _update_episode_info(self, event=None):
        '''Update information from this episode.'''
        self.li.set_current(self.menu.selected_index + 1)

        self._create_thumbnail_texture()
        self.title.set_text(self.menu.selected_userdata.title)
        self.title.width = 0.4

        plot = Label(0.029, "subtitle", 0, 0, self.menu.selected_userdata.plot)
        plot.width = 0.4
        self.scroll_area.set_content(plot)

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        if self.menu.active:
            self.menu.up()
        else:
            self.scroll_area.scroll_up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        if self.menu.active:
            self.menu.down()
        else:
            self.scroll_area.scroll_down()

    def _handle_left(self):
        '''Handle UserEvent.NAVIGATE_LEFT.'''
        self.menu.active = False
        self.scroll_area.active = True

    def _handle_right(self):
        '''Handle UserEvent.NAVIGATE_RIGHT.'''
        self.menu.active = True
        self.scroll_area.active = False

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        episode = self.menu.selected_userdata
        self.media_player.set_media(episode)
        self.media_player.play()
        self.callback("video_osd")

    def _on_menu_activated(self, event=None):
        '''Handle menu activation.'''
        self.scroll_area.active = False

    def _on_scroll_area_activated(self, event=None):
        '''Handle scroll_area activation.'''
        self.menu.active = False

