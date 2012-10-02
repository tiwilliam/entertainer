# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''MoviesTab - MoviesTab is group of objects that are displayed on movie tab'''

import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.image_menu import ImageMenu
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation

class MoviesTab(Tab):
    """
    Tab can be used as part of the TabGroup

    Tab is a very simple container that contains all the widgets and logic
    of the tab page.
    """

    def __init__(self, video_library, move_to_new_screen_callback,
        name="movies", tab_title=_("Movies")):
        Tab.__init__(self, name, tab_title, move_to_new_screen_callback)

        self.video_library = video_library
        self.theme = self.config.theme
        self.list_indicator = None
        self.movie_info = None
        self.menu = None
        self.movie_plot = None
        self.movie_title = None

        if self.video_library.get_number_of_movies() == 0:
            self._create_empty_library_notice()
        else:
            # Start the loading animation while the menu is loading
            self.throbber = LoadingAnimation(0.1, 0.1)
            self.throbber.show()
            self.add(self.throbber)

            self.menu = self._create_menu()
            self.add(self.menu)
            self.menu.connect("moved", self._update_movie_info)
            self.menu.connect("selected", self._handle_select)
            self.menu.connect("activated", self._on_activated)
            self.menu.connect("filled", self._on_menu_filled)

            self.connect('activated', self._on_activated)
            self.connect('deactivated', self._on_deactivated)

    def can_activate(self):
        """
        Allow if we have some movies indexed.
        """
        if self.video_library.get_number_of_movies() == 0:
            return False
        else:
            return True

    def _create_empty_library_notice(self):
        """
        Create an information box that is displayed if there are no indexed
        movies.
        """
        message = _(
            "There are no indexed movies in Entertainer media library.  To "
            "add movies, click on 'content' button on toolbar and open "
            "'videos' tab. Now click on 'add' button and select some folders "
            "which contains movie files.")
        Tab.show_empty_tab_notice(self, _("No movies available!"), message)

    def _create_menu(self):
        """
        Create a view that is displayed when there is indexed movies in
        the video library.
        """
        #Create movie menu
        menu = ImageMenu(0.06, 0.18, 0.12, 0.25)
        menu.items_per_col = 2
        menu.visible_rows = 2
        menu.visible_cols = 7

        movies = self.video_library.get_movies()
        movies_list = [[movie.cover_art_url, movie] for movie in movies]
        menu.async_add_videos(movies_list)

        # Create list indicator
        self.list_indicator = ListIndicator(0.75, 0.76, 0.2, 0.045,
            ListIndicator.HORIZONTAL)
        self.list_indicator.set_maximum(len(movies))
        self.show()
        self.add(self.list_indicator)

        # Create information labels
        self.movie_title = Label(0.042, "title", 0.2, 0.75, "",
            font_weight="bold")
        self.movie_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.movie_title.set_line_wrap(False)
        self.movie_title.width = 0.5
        self.add(self.movie_title)

        self.movie_info = Label(0.034, "subtitle", 0.2, 0.8, "")
        self.movie_info.set_ellipsize(pango.ELLIPSIZE_END)
        self.movie_info.set_line_wrap(False)
        self.movie_info.width = 0.5
        self.add(self.movie_info)

        self.movie_plot = Label(0.025, "subtitle", 0.2, 0.85, "")
        self.movie_plot.width = 0.7
        self.add(self.movie_plot)

        return menu

    def _update_movie_info(self, event=None):
        '''Update the movie information labels.'''
        if self.active:
            movie = self.menu.selected_userdata
            genres = movie.genres
            if len(genres) > 1:
                genre = genres[0] + "/" + genres[1]
            else:
                genre = genres[0]

            self.movie_title.set_text(_("%(title)s (%(year)s)") % \
                {'title': movie.title, 'year': movie.year})
            self.movie_info.set_text(_("%(min)d min, (%(genre)s)") % \
                {'min': movie.runtime, 'genre': genre})
            self.movie_plot.set_text(movie.short_plot)
            self.list_indicator.show()
            self.list_indicator.set_current(self.menu.selected_index + 1)
        else:
            self.movie_title.set_text("")
            self.movie_info.set_text("")
            self.movie_plot.set_text("")
            self.list_indicator.hide()

    def _handle_up(self):
        '''Handle the up user event.'''
        if self.menu.on_top:
            return True # Move control back to tab bar
        else:
            self.menu.up()
            return False

    def _handle_down(self):
        '''Handle the down user event.'''
        self.menu.down()
        return False

    def _handle_left(self):
        '''Handle the left user event.'''
        self.menu.left()
        return False

    def _handle_right(self):
        '''Handle the right user event.'''
        self.menu.right()
        return False

    def _handle_select(self, event=None):
        '''Handle the select user event.'''
        movie = self.menu.selected_userdata
        kwargs = { 'movie' : movie }
        self.callback("movie", kwargs)
        return False

    def _on_activated(self, event=None):
        '''Tab activated.'''
        if self.tab_group is not None:
            self.tab_group.active = False
        self.menu.active = True
        self.active = True
        self._update_movie_info()
        return False

    def _on_deactivated(self, event=None):
        '''Tab deactivated.'''
        self.active = False
        self.menu.active = False
        self._update_movie_info()
        return False

    def _on_menu_filled(self, event=None):
        '''Handles filled event.'''
        self.throbber.hide()

