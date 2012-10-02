# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Photo - Screen displays photograph in fullscreen'''

import clutter
import gobject

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.texture import Texture

class Photo(Screen):
    '''Screen displays photograph in fullscreen and allows user to zoom in.'''

    # How much one zoom click zooms in
    ZOOM_FACTOR = 0.5
    MOVE_SIZE = 100

    def __init__(self, current_photo_index, images):
        Screen.__init__(self, 'Photo')

        self.animate = self.config.show_effects
        self.slideshow_step = self.config.slideshow_step

        self.zoom_level = 1
        self.index = current_photo_index
        self.images = images
        self.slideshow = False
        # Slideshow gobject timeout tag
        self.slideshow_timeout_tag = None

        # Create black background
        self.background = clutter.Rectangle()
        self.background.set_size(
            self.config.stage_width, self.config.stage_height)
        self.background.set_color((0, 0, 0, 255))
        self.add(self.background)

        # Screen Title (Displayed at the bottom left corner)
        self.screen_title = Label(0.13, "screentitle", 0, 0.87,
            _("Information"))
        self.add(self.screen_title)

        self.texture = None
        self._change_image(self.index)

    def set_animate(self, boolean):
        """Animate this screen."""
        self.animate = boolean

    def _change_image(self, index):
        """
        Change current image. Display image from given index.
        """
        if self.texture:
            self.texture.destroy()

        # Create a new texture and display it
        image = self.images[index]
        self.index = index
        self.texture = Texture(image.get_filename())
        self._scale_image(self.texture)

        timeline = clutter.Timeline(1000)
        alpha = clutter.Alpha(timeline, clutter.EASE_IN_OUT_SINE)
        self.opacity_behaviour = clutter.BehaviourOpacity(alpha=alpha,
            opacity_start=0, opacity_end=255)
        self.opacity_behaviour.apply(self.texture)
        self.texture.set_opacity(0)
        timeline.start()

        self.add(self.texture)

    def _scale_image(self, texture, zoom_level=1):
        """
        Scale image. Scaling doesn't change image aspect ratio.
        @param texture: Texture to scale
        @param zoom_level: Zoom level - Default value is 1 (no zoom)
        """
        # Center position when zoomed
        width = texture.get_width()
        height = texture.get_height()
        x_ratio = self.config.stage_width / float(width)
        y_ratio = self.config.stage_height / float(height)

        if x_ratio > y_ratio:
            texture.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            texture.set_scale(
                self.config.stage_height / float(height) * zoom_level,
                self.config.stage_height / float(height) * zoom_level)
            texture.set_anchor_point(0, 0)

            if zoom_level == 1: # Center image if in normal size
                new_width = int(width *
                    (self.config.stage_height / float(height)))
                new_x = int(
                    (self.config.stage_width - new_width) / float(2))
                texture.set_position(new_x, 0)
        else:
            texture.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            texture.set_scale(
                self.config.stage_width / float(width) * zoom_level,
                self.config.stage_width / float(width) * zoom_level)
            texture.set_anchor_point(0, 0)

            if zoom_level == 1:  # Center image if in normal size
                new_height = int(
                    height * (self.config.stage_width / float(width)))
                new_y = int((self.config.stage_height - new_height) / float(2))
                texture.set_position(0, new_y)

    def is_interested_in_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        """
        return True

    def execute_play_action(self):
        """
        Override function from Screen class. See Screen class for
        better documentation.
        """
        if self.slideshow:
            self.stop_slideshow()
        else:
            self.start_slideshow()

    def slideshow_progress(self):
        """slideshow loop called every slideshow_step seconds"""
        if ((self.zoom_level == 1) and self.slideshow):
            self._handle_right()
        return True

    def start_slideshow(self):
        """Start the slideshow"""
        self.zoom_level = 1
        self.slideshow = True
        self.slideshow_progress()
        self.slideshow_timeout_tag = gobject.timeout_add(self.slideshow_step *
            1000, self.slideshow_progress)

    def stop_slideshow(self):
        """Stop the slideshow"""
        self.slideshow = False
        if self.slideshow_timeout_tag:
            gobject.source_remove(self.slideshow_timeout_tag)

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        if self.zoom_level != 1:
            self.texture.move_by(0, self.MOVE_SIZE)

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        if self.zoom_level != 1:
            self.texture.move_by(0, -self.MOVE_SIZE)

    def _handle_left(self):
        '''Handle UserEvent.NAVIGATE_LEFT.'''
        # Change to previous image
        if self.zoom_level == 1:
            if self.index == 0:
                self.index = len(self.images) - 1
            else:
                self.index = self.index - 1
            self._change_image(self.index)
        # Change texture position (texture is zoomed)
        else:
            self.texture.move_by(self.MOVE_SIZE, 0)

    def _handle_right(self):
        '''Handle UserEvent.NAVIGATE_RIGHT.'''
        # Change to next image
        if self.zoom_level == 1:
            if self.index == len(self.images) - 1:
                self.index = 0
            else:
                self.index = self.index + 1
            self._change_image(self.index)
        # Change texture position (texture is zoomed)
        else:
            self.texture.move_by(-self.MOVE_SIZE, 0)

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        # Zoom image. If we zoom then we stop sliding photos.
        self.stop_slideshow()
        if self.zoom_level >= 3:
            self.zoom_level = 1
        else:
            self.zoom_level = self.zoom_level + self.ZOOM_FACTOR
        self._scale_image(self.texture, self.zoom_level)

