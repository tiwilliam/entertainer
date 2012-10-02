# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''VideoClipsTab - Group of objects that are displayed on video clips tab'''

import os

import pango

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.widgets.image_menu import ImageMenu
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation

class VideoClipsTab(Tab):
    """
    Tab can be used as part of the TabGroup

    Tab is a very simple container that contains all the widgets and logic
    of the tab page.
    """

    def __init__(self, media_player, video_library, move_to_new_screen_callback,
        name="clips", tab_title=_("Video clips")):
        Tab.__init__(self, name, tab_title, move_to_new_screen_callback)
        self.media_player = media_player
        self.video_library = video_library
        self.theme = self.config.theme
        self.list_indicator = None
        self.clip_info = None
        self.menu = None
        self.clip_title = None

        if self.video_library.get_number_of_video_clips() == 0:
            self._create_empty_library_notice()
        else:
            # Start the loading animation while the menu is loading
            self.throbber = LoadingAnimation(0.7, 0.1)
            self.throbber.show()
            self.add(self.throbber)

            self.menu = self._create_menu()
            self.add(self.menu)
            self.menu.connect("moved", self._update_clip_info)
            self.menu.connect("selected", self._handle_select)
            self.menu.connect("activated", self._on_activated)
            self.menu.connect("filled", self._on_menu_filled)

            self.connect('activated', self._on_activated)
            self.connect('deactivated', self._on_deactivated)

    def can_activate(self):
        """
        Allow if we have some movies indexed.
        """
        if self.video_library.get_number_of_video_clips() == 0:
            return False
        else:
            return True

    def _create_empty_library_notice(self):
        """
        Create an information box that is displayed if there are no indexed
        movies.
        """
        message = _(
            "There are no indexed Video Clips in the Entertainer media "
            "library. Please add some folders containing video clips "
            "to the Library using the configuration tool.")
        Tab.show_empty_tab_notice(self, _("No video clips available!"), message)

    def _create_menu(self):
        """
        Create a view that is displayed when there are indexed clips in
        the video library.
        """
        menu = ImageMenu(0.04, 0.16, 0.23, self.y_for_x(0.23) * 0.7)
        menu.items_per_col = 2
        menu.visible_rows = 2
        menu.visible_cols = 4

        clips = self.video_library.get_video_clips()
        clips_list = [[clip.thumbnail_url, clip] for clip in clips]
        menu.async_add_clips(clips_list)

        # Create list indicator
        self.list_indicator = ListIndicator(0.7, 0.8, 0.2, 0.045,
            ListIndicator.HORIZONTAL)
        self.list_indicator.set_maximum(len(clips))
        self.list_indicator.show()
        self.add(self.list_indicator)

        # Create information labels
        self.clip_title = Label(0.042, "title", 0.15, 0.77, "",
            font_weight="bold")
        self.clip_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.clip_title.set_line_wrap(False)
        self.clip_title.width = 0.5
        self.add(self.clip_title)

        self.clip_info = Label(0.034, "subtitle", 0.15, 0.85, "")
        self.clip_info.set_ellipsize(pango.ELLIPSIZE_END)
        self.clip_info.set_line_wrap(False)
        self.clip_info.width = 0.5
        self.add(self.clip_info)

        return menu

    def _update_clip_info(self, event=None):
        '''Update the VideoClip information labels.'''
        if self.active:
            clip = self.menu.selected_userdata
            (folder, filename) = os.path.split(clip.filename)
            self.clip_title.set_text(filename)
            self.clip_info.set_text(folder)
            self.list_indicator.show()
            self.list_indicator.set_current(self.menu.selected_index + 1)
        else:
            self.clip_title.set_text("")
            self.clip_info.set_text("")
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
        clip = self.menu.selected_userdata
        self.media_player.set_media(clip)
        self.media_player.play()
        self.callback("video_osd")
        return False

    def _on_activated(self, event=None):
        '''Tab activated.'''
        if self.tab_group is not None:
            self.tab_group.active = False
        self.menu.active = True
        self.active = True
        self._update_clip_info()
        return False

    def _on_deactivated(self, event=None):
        '''Tab deactivated.'''
        self.active = False
        self.menu.active = False
        self._update_clip_info()
        return False

    def _on_menu_filled(self, event=None):
        '''Handles filled event.'''
        self.throbber.hide()

