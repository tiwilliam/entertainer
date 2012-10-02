# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Photographs - Screen contains a list/grid of photographs'''

import pango

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.image_menu import ImageMenu
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.loading_animation import LoadingAnimation
from entertainerlib.gui.widgets.texture import Texture

class Photographs(Screen):
    '''Screen displays a grid of selectable photograph thumbnails.'''

    def __init__(self, move_to_new_screen_callback, title, images):
        Screen.__init__(self, 'Photographs', move_to_new_screen_callback)

        self.images = images

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, title)
        self.add(screen_title)

        # Image Title (over album list)
        self.image_title = Label(0.04167, "title", 0.0586, 0.7943, " ")
        self.image_title.set_ellipsize(pango.ELLIPSIZE_END)
        self.add(self.image_title)

        self.image_desc = Label(0.04167, "subtitle", 0.0586, 0.9115, " ")
        self.image_desc.set_line_wrap(True)
        self.image_desc.set_ellipsize(pango.ELLIPSIZE_END)
        self.add(self.image_desc)

        # Display throbber animation while loading photographs
        self.throbber = LoadingAnimation(0.9, 0.9)
        self.throbber.show()
        self.add(self.throbber)

        # List indicator
        self.li = None
        self._create_list_indicator()

        # Create photomenu
        self.menu = ImageMenu(0.03, 0.08, 0.12, self.y_for_x(0.12))
        self.menu.items_per_col = 3
        self.menu.visible_rows = 3
        self.menu.visible_cols = 8
        self.menu.active = True
        self.add(self.menu)

        photos = self.images
        photos_list = [[Texture(photo.get_thumbnail_url()), photo] \
            for photo in photos]
        self.menu.async_add(photos_list)

        self.menu.connect("selected", self._handle_select)
        self.menu.connect('moved', self._update_image_info)
        self.menu.connect("filled", self._on_menu_filled)

    def _update_image_info(self, event=None):
        """Update image information box."""
        image = self.images[self.menu.selected_index]
        name = image.get_title()
        desc = image.get_description()
        self.image_title.set_text(name)
        self.image_title.set_size(0.366, 0.04167)
        self.image_desc.set_text(desc)
        self.image_desc.set_size(0.366, 0.0911)
        self.li.set_current(self.menu.selected_index + 1)

    def _create_list_indicator(self):
        '''Create list indicator for albums list.'''
        self.li = ListIndicator(0.77, 0.8, 0.18, 0.045,
            ListIndicator.HORIZONTAL)
        self.li.set_maximum(len(self.images))
        self.add(self.li)

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        self.menu.up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        self.menu.down()

    def _handle_left(self):
        '''Handle UserEvent.NAVIGATE_LEFT.'''
        self.menu.left()

    def _handle_right(self):
        '''Handle UserEvent.NAVIGATE_RIGHT.'''
        self.menu.right()

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        index = self.menu.selected_index
        kwargs = {'current_photo_index' : index, 'images' : self.images}
        self.callback("photo", kwargs)

    def _on_menu_filled(self, event=None):
        '''Handles filled event.'''
        self.throbber.hide()

