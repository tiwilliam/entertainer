# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Main - Screen has a main menu'''

import clutter

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.clock_label import ClockLabel
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.scroll_menu import ScrollMenu
from entertainerlib.gui.widgets.texture import Texture

class Main(Screen):
    '''Screen displayed when frontend is opened and provides main navigation.'''

    # Size of the preview area
    PREVIEW_WIDTH = 830
    PREVIEW_HEIGHT = 580

    # Directions
    UP = 0
    DOWN = 1

    def __init__(self, media_player, move_to_new_screen_callback):
        Screen.__init__(self, 'Main', move_to_new_screen_callback)

        self.media_player = media_player
        self.media_player.connect("stop", self.update)
        self.media_player.connect("play", self.update)
        self.media_player.connect('refresh', self._update_preview_title)

        self.theme = self.config.theme

        self._preview_title = None
        self.preview = clutter.Group() # Group that contains preview actors
        self.preview.set_position(self.get_abs_x(0.07), self.get_abs_y(0.1))
        self.preview.show()
        self.preview.set_opacity(0x00)
        self.add(self.preview)

        self.menu = self._create_main_menu()
        self.add(self.menu)

        self._update_preview_area()

        self.add(ClockLabel(0.13, "screentitle", 0, 0.87))

        self.menu.connect('selected', self._handle_select)
        self.menu.connect('moved', self._on_menu_moved)

        self.menu.active = True

    def get_type(self):
        """Return screen type."""
        return Screen.NORMAL

    def get_name(self):
        """Return screen name (human readble)."""
        return "Main"

    def _create_main_menu(self):
        """Create main menu of the home screen."""
        menu = ScrollMenu(10, 60, 0.045, "menuitem_active")
        menu.set_name("mainmenu")

        menu.add_item(_("Play CD"), "disc")
        menu.add_item(_("Videos"), "videos")
        menu.add_item(_("Music"), "music")
        menu.add_item(_("Photographs"), "photo")

        if self.config.display_weather_in_client:
            menu.add_item(_("Weather"), "weather")

        if self.media_player.has_media():
            menu.add_item(_("Playing now..."), "playing")

        menu.visible_items = 5
        menu.selected_index = 2

        # Menu position
        menu_clip = menu.visible_items * 70
        menu_y = int((self.config.stage_height - menu_clip + 10) / 2)
        menu.set_position(self.get_abs_x(0.75), menu_y)

        return menu

    def _create_playing_preview(self):
        '''Create the Now Playing preview sidebar.'''
        preview = clutter.Group()

        # Video preview of current media
        video_texture = self.media_player.get_texture()
        if video_texture == None:
            video_texture = Texture(self.theme.getImage("default_album_art"))
        width, height = video_texture.get_size()
        x_ratio = (self.PREVIEW_WIDTH - 50) / float(width)
        y_ratio = (self.PREVIEW_HEIGHT - 50) / float(height)

        if x_ratio > y_ratio:
            video_texture.set_scale((self.PREVIEW_HEIGHT - 50) / float(height),
                                    (self.PREVIEW_HEIGHT - 50) / float(height))
            new_width = int(width * \
                ((self.PREVIEW_HEIGHT - 50) / float(height)))
            new_x = int(((self.PREVIEW_WIDTH - 50) - new_width) / 2.0)
            video_texture.set_position(int(new_x), 0)
            # Below are size and position calculations for border rectangle
            rect_x = new_x -3
            rect_y = -3
            new_width = (self.PREVIEW_HEIGHT - 50) / float(height) * width
            new_height = (self.PREVIEW_HEIGHT - 50) / float(height) * height
        else:
            video_texture.set_scale((self.PREVIEW_WIDTH - 50) / float(width),
                                    (self.PREVIEW_WIDTH - 50) / float(width))
            new_height = int(height * \
                ((self.PREVIEW_WIDTH - 50) / float(width)))
            new_y = int(((self.PREVIEW_HEIGHT - 50) - new_height) / 2.0)
            video_texture.set_position(0, int(new_y))
            rect_x = -3
            rect_y = new_y -3
            # Below are size and position calculations for border rectangle
            new_width = (self.PREVIEW_WIDTH - 50) / float(width) * width
            new_height = (self.PREVIEW_WIDTH - 50) / float(width) * height

        # Video frame
        rect = clutter.Rectangle()
        rect.set_size(int(new_width + 6), int(new_height + 6))
        rect.set_position(rect_x, rect_y)
        rect.set_color((128, 128, 128, 192))
        preview.add(rect)

        preview.add(video_texture)

        self._preview_title = Label(0.03, "text", 0.03, 0.74, "")
        preview.add(self._preview_title)

        return preview

    def _update_preview_title(self, event=None):
        '''Update the label showing the currently playing media.'''
        if self._preview_title != None:
            title_text = _("Now Playing: %(title)s (%(pos)s/%(length)s)") % \
                {'title': self.media_player.get_media_title(), 
                'pos': self.media_player.get_media_position_string(),
                'length': self.media_player.get_media_duration_string()}
            self._preview_title.set_text(title_text)

    def _update_preview_area(self):
        '''Update the preview area to display the current menu item.'''
        self.preview.remove_all()
        item = self.menu.get_selected()

        self.preview.set_opacity(0x00)

        update = True

        if item.get_name() == "playing":
            self.preview.add(self._create_playing_preview())
        else:
            update = False

        # If the preview was updated fade it in.
        if update:
            fade_in = clutter.Timeline(500)
            alpha_in = clutter.Alpha(fade_in, clutter.EASE_IN_OUT_SINE)
            self.behaviour = clutter.BehaviourOpacity(0, 255, alpha_in)
            self.behaviour.apply(self.preview)
            fade_in.start()

    def update(self, event=None):
        """
        Update screen widgets. This is called always when screen is poped from
        the screen history. Updates main menu widget.
        """
        if self.media_player.is_playing and \
                (self.menu.get_index("playing") == -1):
            self.menu.add_item(_("Playing now..."), "playing")
        elif not self.media_player.is_playing and \
                (self.menu.get_index("playing") != -1):
            self.menu.remove_item("playing")

        self.menu.refresh()
        self._update_preview_area()

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        self.menu.scroll_up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        self.menu.scroll_down()

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        item = self.menu.get_selected()

        if item.get_name() == "disc":
            self.callback("audio_cd")
        elif item.get_name() == "playing":
            self.callback("video_osd")
        elif item.get_name() == "music":
            self.callback("music")
        elif item.get_name() == "videos":
            self.callback("video")
        elif item.get_name() == "weather":
            self.callback("weather")
        elif item.get_name() == "photo":
            self.callback("photo_albums")

    def _on_menu_moved(self, event):
        '''Update preview area when selected item changed on the menu.'''
        self._update_preview_area()

