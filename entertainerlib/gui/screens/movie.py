# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Movie - Screen allows user to view movie information'''

import clutter
import gtk
import pango

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.widgets.eyecandy_texture import EyeCandyTexture
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.scroll_area import ScrollArea
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.gui.widgets.text_menu import TextMenu

class Movie(Screen):
    '''Screen contains information of one movie.'''

    def __init__(self, media_player, movie, move_to_new_screen_callback):
        Screen.__init__(self, 'Movie', move_to_new_screen_callback)

        self.theme = self.config.theme
        self.media_player = media_player
        self.movie = movie

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, _("Movie"))
        self.add(screen_title)

        # Add the additional actions that are needed but not handled by default
        self.event_handlers.update({
            UserEvent.NAVIGATE_FIRST_PAGE : self._handle_first_page,
            UserEvent.NAVIGATE_LAST_PAGE : self._handle_last_page,
            UserEvent.NAVIGATE_PREVIOUS_PAGE : self._handle_previous_page,
            UserEvent.NAVIGATE_NEXT_PAGE : self._handle_next_page
        })

        self.menu = None
        self.scroll_area = None
        self.create_menu()
        self.create_movie_information()

    def create_movie_information(self):
        '''Create clutter parts related to movie information'''

        # Movie art texture
        if self.movie.has_cover_art():
            pixbuf = gtk.gdk.pixbuf_new_from_file(self.movie.cover_art_url)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(
                self.theme.getImage("default_movie_art"))
        movie_art = EyeCandyTexture(0.33, 0.1, 0.1, 0.25, pixbuf)
        self.add(movie_art)

        # Movie title
        title = Label(0.04, "title", 0.47, 0.1, self.movie.title,
            font_weight="bold")
        title.set_ellipsize(pango.ELLIPSIZE_END)
        title.set_size(0.5124, 0.05208)
        self.add(title)

        # Movie release year
        year_text = _("Released in %(year)s") % {'year': self.movie.year}
        year = Label(0.032, "subtitle", 0.47, 0.3, year_text)
        year.set_ellipsize(pango.ELLIPSIZE_END)
        year.set_size(0.5124, 0.05208)
        self.add(year)

        # Show only 2 genres (or one if there is only one)
        genres_list = self.movie.genres
        if len(genres_list) == 0:
            genres_text = _("Unknown")
        else:
            genres_text = "/".join(genres_list[:2])

        # Runtime and genres
        info_text = _("%(runtime)s min, %(genre)s") % \
            {'runtime': self.movie.runtime, 'genre': genres_text}
        info = Label(0.032, "subtitle", 0.47, 0.24, info_text)
        info.set_ellipsize(pango.ELLIPSIZE_END)
        info.set_size(0.5124, 0.05208)
        self.add(info)

        # Stars (rating)
        star = Texture(self.theme.getImage("star"))
        star.hide()
        self.add(star)
        star2 = Texture(self.theme.getImage("star2"))
        star2.hide()
        self.add(star2)

        for i in range(self.movie.rating):
            tex = clutter.Clone(star)
            tex.set_position(
                self.get_abs_x(0.47) + (self.get_abs_x(0.0366) * i),
                self.get_abs_y(0.17))
            tex.set_size(self.get_abs_x(0.024), self.get_abs_y(0.04))
            self.add(tex)

        dark_star = 5 - self.movie.rating
        for i in range(dark_star):
            tex = clutter.Clone(star2)
            tex.set_position(self.get_abs_x(0.47) + (self.get_abs_x(0.0366) * \
                (i + self.movie.rating)), self.get_abs_y(0.17))
            tex.set_size(self.get_abs_x(0.024), self.get_abs_y(0.04))
            self.add(tex)

        # Plot
        plot = Label(0.029, "subtitle", 0, 0, self.movie.plot)
        plot.set_justify(True)
        plot.set_line_wrap_mode(pango.WRAP_WORD)
        plot.set_line_wrap(True)
        plot.width = 0.5124
        self.scroll_area = ScrollArea(0.33, 0.38, 0.5124, 0.3516, plot)
        self.add(self.scroll_area)

        # Actors
        self.add(Label(0.032, "title", 0.33, 0.8, _("Starring")))

        actors_list = self.movie.actors
        if len(actors_list) == 0:
            actors_text = _("Unknown")
        else:
            actors_text = ", ".join(actors_list[:5])
        actors = Label(0.032, "subtitle", 0.46, 0.8, actors_text)
        actors.set_ellipsize(pango.ELLIPSIZE_END)
        actors.set_size(0.5124, 0.05208)
        self.add(actors)

        # Directors
        self.add(Label(0.032, "title", 0.33, 0.86, _("Directed by")))

        directors_list = self.movie.directors
        if len(directors_list) == 0:
            directors_text = _("Unknown")
        else:
            directors_text = ", ".join(directors_list[:2])
        directors = Label(0.032, "subtitle", 0.46, 0.86, directors_text)
        directors.set_ellipsize(pango.ELLIPSIZE_END)
        directors.set_size(0.5124, 0.05208)
        self.add(directors)

        # Writers
        self.add(Label(0.032, "title", 0.33, 0.92, _("Written by")))

        writers_list = self.movie.writers
        if len(directors_list) == 0:
            writers_text = _("Unknown")
        else:
            writers_text = ", ".join(writers_list[:2])
        writers = Label(0.032, "subtitle", 0.46, 0.92, writers_text)
        writers.set_ellipsize(pango.ELLIPSIZE_END)
        writers.set_size(0.5124, 0.05208)
        self.add(writers)

    def create_menu(self):
        """
        Create menu of the screen. This displayed the left side of the screen.
        """
        self.menu = TextMenu(0.07, 0.1, 0.2196, 0.0781)
        self.menu.add_item(_("Watch"), None, "watch")
        self.menu.active = True

        self.add(self.menu)

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
        self.menu.active = True
        self.scroll_area.active = False

    def _handle_right(self):
        '''Handle UserEvent.NAVIGATE_RIGHT.'''
        self.menu.active = False
        self.scroll_area.active = True

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        if self.menu.active:
            item = self.menu.selected_userdata
            if item == "watch":
                self.media_player.set_media(self.movie)
                self.media_player.play()
                self.callback("video_osd")

    def _handle_first_page(self):
        '''Handle UserEvent.NAVIGATE_FIRST_PAGE.'''
        self.scroll_area.scroll_to_top()

    def _handle_last_page(self):
        '''Handle UserEvent.NAVIGATE_LAST_PAGE.'''
        self.scroll_area.scroll_to_bottom()

    def _handle_previous_page(self):
        '''Handle UserEvent.NAVIGATE_PREVIOUS_PAGE.'''
        self.scroll_area.scroll_page_up()

    def _handle_next_page(self):
        '''Handle UserEvent.NAVIGATE_NEXT_PAGE.'''
        self.scroll_area.scroll_page_down()

