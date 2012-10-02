# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''SeriesTab - Group of objects that are displayed on tv-series tab'''

import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.image_menu import ImageMenu
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation

class SeriesTab(Tab):
    """
    Tab can be used as part of the TabGroup

    Tab is a very simple container that contains all the widgets and logic
    of the tab page.
    """

    def __init__(self, video_library, move_to_new_screen_callback,
        name="series", tab_title=_("TV-Series")):
        Tab.__init__(self, name, tab_title, move_to_new_screen_callback)

        self.video_library = video_library
        self.theme = self.config.theme
        self.list_indicator = None
        self.series_info = None
        self.menu = None
        self.series_title = None

        if self.video_library.get_number_of_tv_series() == 0:
            self._create_empty_library_notice()
        else:
            # Start the loading animation while the menu is loading
            self.throbber = LoadingAnimation(0.4, 0.1)
            self.throbber.show()
            self.add(self.throbber)

            self.menu = self._create_menu()
            self.add(self.menu)
            self.menu.connect("moved", self._update_serie_info)
            self.menu.connect("selected", self._handle_select)
            self.menu.connect("activated", self._on_activated)
            self.menu.connect("filled", self._on_menu_filled)

            self.connect('activated', self._on_activated)
            self.connect('deactivated', self._on_deactivated)

    def can_activate(self):
        """
        Allow if we have some TV-series indexed.
        """
        if self.video_library.get_number_of_tv_series() == 0:
            return False
        else:
            return True

    def _create_empty_library_notice(self):
        """
        Create an information box that is displayed if there are no indexed
        tv-series.
        """
        message = _(
            "There are no indexed TV-series in Entertainer media library. To "
            "add TV-series, click on 'content' button on toolbar and open "
            "'videos' tab. Now click on 'add' button and select some folders "
            "which contains video files.")
        Tab.show_empty_tab_notice(self, _("No TV-series available!"), message)

    def _create_menu(self):
        """
        Create a view that is displayed when there is indexed TV-series in
        the video library.
        """
        #Create TV-series menu
        menu = ImageMenu(0.06, 0.18, 0.12, 0.25)
        menu.items_per_col = 2
        menu.visible_rows = 2
        menu.visible_cols = 7

        series = self.video_library.get_tv_series()
        series_list = [[serie.cover_art_url, serie] for serie in series]
        menu.async_add_videos(series_list)

        # Create list indicator
        self.list_indicator = ListIndicator(0.75, 0.76, 0.2, 0.045,
            ListIndicator.HORIZONTAL)
        self.list_indicator.set_maximum(len(series))
        self.list_indicator.show()
        self.add(self.list_indicator)

        # Create information labels
        self.series_title = Label(0.042, "title", 0.2, 0.75, "",
            font_weight="bold")
        self.series_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.series_title.set_line_wrap(False)
        self.series_title.width = 0.5
        self.add(self.series_title)

        self.series_info = Label(0.034, "subtitle", 0.2, 0.82, "")
        self.add(self.series_info)

        return menu

    def _update_serie_info(self, event=None):
        '''Update the series information labels.'''
        if self.active:
            series = self.menu.selected_userdata
            info = _("%(season)d Seasons\n%(episode)d Episodes") % {'season':
                len(series.seasons), 'episode': series.number_of_episodes}

            self.series_info.set_text(info)
            self.series_title.set_text(series.title)
            self.list_indicator.show()
            self.list_indicator.set_current(self.menu.selected_index + 1)
        else:
            self.series_info.set_text("")
            self.series_title.set_text("")
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
        series = self.menu.selected_userdata
        kwargs = { 'tv_series' : series }
        self.callback("tv_series", kwargs)
        return False

    def _on_activated(self, event=None):
        '''Tab activated.'''
        if self.tab_group is not None:
            self.tab_group.active = False
        self.menu.active = True
        self.active = True
        self._update_serie_info()
        return False

    def _on_deactivated(self, event=None):
        '''Tab deactivated.'''
        self.active = False
        self.menu.active = False
        self._update_serie_info()
        return False

    def _on_menu_filled(self, event=None):
        '''Handles filled event.'''
        self.throbber.hide()

