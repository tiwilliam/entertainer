# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''PhotoAlbums - Screen contains a list of photograph albums'''

import gtk
import pango
import gobject
import clutter

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.eyecandy_texture import EyeCandyTexture
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.gui.widgets.text_menu import TextMenu

class PhotoAlbums(Screen):
    '''Screen contains a list of photo albums and album previews.'''

    def __init__(self, image_library, move_to_new_screen_callback):
        Screen.__init__(self, 'PhotoAlbums', move_to_new_screen_callback)

        self.theme = self.config.theme
        self.image_library = image_library
        self.timeout = None # Timeout key (this is used when scrolling menu)

        # Screen Title (Displayed at the bottom left corner)
        screen_title = Label(0.13, "screentitle", 0, 0.87, _("Photographs"))
        self.add(screen_title)

        if self.image_library.get_number_of_albums() == 0:
            self._create_no_photos_information()
        else:
            # Album preview group
            self.preview = clutter.Group()
            self.preview.set_position(self.get_abs_x(0.07),
                self.get_abs_y(0.1953))
            self.preview.show()
            self.add(self.preview)

            self.preview_fade = None
            self.menu = None
            self.in_behaviour = None
            self.out_behaviour = None
            self.in_opacity = None
            self.out_opacity = None
            self.preview_textures = None
            self.menu = self._create_album_menu()
            self.add(self.menu)
            self.li = None
            self._create_list_indicator()

            self._update_album_preview(self.menu.selected_userdata)

            self.menu.connect('selected', self._handle_select)
            self.menu.connect('moved', self._display_selected_album)

    def _create_no_photos_information(self):
        """
        Create textures and labels for information screen. This is displayed
        instead of album list if there are no photos available and it helps
        users to add new photographs to the system.
        """
        # Create warning icon
        warning_icon = Texture(self.theme.getImage("warning_icon"), 0.28, 0.27)
        self.add(warning_icon)

        # Create warning title
        info_title = Label(0.0625, "title", 0.3367, 0.2709,
            _("No photographs available!"))
        self.add(info_title)

        # Create warning help text
        message = _(
            "There are no indexed photographs in the Entertainer media "
            "library. To add photographs, start the Content management tool "
            "and open the 'Images' tab. Now click on the 'Add' button and "
            "select some folders which contain image files.")
        info = Label(0.0417, "menuitem_inactive", 0.2804, 0.45, message)
        info.set_size(0.5, 0.5859)
        self.add(info)

    def _create_album_menu(self):
        """
        Create ImageAlbum-menu. This menu contains list of albums. It also
        displays number of photographs per album.
        """
        menu = TextMenu(0.5271, 0.3385, 0.4393, 0.0781)
        menu.visible_rows = 7

        albums = self.image_library.get_albums()
        albums_list = [[album.get_title(), str(album.get_number_of_images()),
            album] for album in albums if album.get_number_of_images() != 0]
        menu.async_add(albums_list)

        menu.active = True

        return menu

    def _create_album_preview(self, album):
        """
        Create a clutter.Group that contains album preview actors.
        """
        group = clutter.Group()
        group.set_position(self.get_abs_x(0.07), self.get_abs_y(0.1953))

        # Preview images
        images = album.get_preview_images(3)
        self.preview_textures = []

        max_w = 0.4026
        max_h = 0.5599
        abs_max_w = self.get_abs_x(max_w)
        abs_max_h = self.get_abs_y(max_h)

        for image in images:
            pix_buffer = gtk.gdk.pixbuf_new_from_file(image.get_thumbnail_url())
            ratio = float(pix_buffer.get_width())
            ratio /= float(pix_buffer.get_height())

            # Resize and center preview texture
            if ratio > 1:
                texture = EyeCandyTexture(0.0, 0.0, max_w, max_h / ratio,
                    pix_buffer)
                new_y = int((abs_max_h - abs_max_h / ratio) / 2.0)
                texture.set_position(0, new_y)
            else:
                texture = EyeCandyTexture(0.0, 0.0, max_w * ratio,
                    max_h, pix_buffer)
                new_x = int((abs_max_w - abs_max_w * ratio) / 2.0)
                texture.set_position(new_x, 0)

            texture.set_rotation(clutter.Y_AXIS, 25, 0, 0, 0)
            texture.set_opacity(0)

            self.preview_textures.append(texture)
            group.add(texture)
        self.preview_textures[0].set_opacity(255)

        title = Label(0.03646, "title", 0.4649, 0, album.get_title(),
            font_weight="bold")
        title.width = 0.4758
        title.set_ellipsize(pango.ELLIPSIZE_END)
        group.add(title)

        desc = Label(0.026, "subtitle", 0.4649, 0.0521, album.get_description())
        desc.width = 0.4758
        group.add(desc)

        return group

    def _update_album_preview(self, album):
        """
        Update album preview. Display preview images from the current album.
        @param album: Currently selected album in menu
        """
        if self.preview_fade is not None:
            gobject.source_remove(self.preview_fade)

        new = self._create_album_preview(album)

        if self.config.show_effects:
            old = self.preview
            new.set_opacity(0)
            self.preview = new
            self.add(self.preview)

            #Fade out timeline
            timeline1 = clutter.Timeline(500)
            alpha1 = clutter.Alpha(timeline1, clutter.EASE_IN_OUT_SINE)
            self.out_opacity = clutter.BehaviourOpacity(255, 0, alpha1)
            self.out_opacity.apply(old)

            timeline1.connect('completed', self._change_preview_timeline_ended,
                old)

            # Fade in timeline
            timeline2 = clutter.Timeline(500)
            alpha2 = clutter.Alpha(timeline2, clutter.EASE_IN_OUT_SINE)
            self.in_opacity = clutter.BehaviourOpacity(0, 255, alpha2)
            self.in_opacity.apply(new)

            # Start animation
            timeline1.start()
            timeline2.start()
        else:
            # Do it without animation
            if self.preview is not None:
                self.remove(self.preview)
            self.preview = new
            self.add(self.preview)

        if len(self.preview_textures) > 1:
            self.preview_fade = gobject.timeout_add(6000,
                self._change_preview_image)

        return False # see gobject.timeout_add() doc

    def _change_preview_timeline_ended(self, timeline, group):
        """
        This is a callback function for preview updates. This is called when
        transition effect is finished. This method removes old preview group
        from the stage.
        """
        self.remove(group)

    def _change_preview_image(self):
        """
        Run a timeline that crossfades preview images. This method is a callback
        that is called every 4 seconds.
        """
        if len(self.preview_textures)<=1:
            self.preview_textures[0].set_opacity(255)
        elif self.config.show_effects:
            #Fade out timeline
            fade_out = clutter.Timeline(500)
            alpha_out = clutter.Alpha(fade_out, clutter.EASE_IN_OUT_SINE)
            self.out_behaviour = clutter.BehaviourOpacity(255, 0, alpha_out)
            self.out_behaviour.apply(self.preview_textures[0])

            # Fade in timeline
            fade_in = clutter.Timeline(500)
            alpha_in = clutter.Alpha(fade_in, clutter.EASE_IN_OUT_SINE)
            self.in_behaviour = clutter.BehaviourOpacity(0, 255, alpha_in)
            self.in_behaviour.apply(self.preview_textures[1])

            # Start animation
            fade_out.start()
            fade_in.start()
        else:
            self.preview_textures[0].set_opacity(0)
            self.preview_textures[1].set_opacity(255)

        # Scroll images
        self.preview_textures = self.preview_textures[1:] + \
            self.preview_textures[:1]

        return True

    def _create_list_indicator(self):
        '''Create list indicator for albums list.'''
        self.li = ListIndicator(0.77, 0.9, 0.2, 0.045, ListIndicator.VERTICAL)
        albums = self.image_library.get_albums()
        albums_list = [[album.get_title(), str(album.get_number_of_images()),
            album] for album in albums if album.get_number_of_images() != 0]
        self.li.set_maximum(len(albums_list))
        self.add(self.li)

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        self.menu.up()

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        self.menu.down()

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        album = self.menu.selected_userdata
        kwargs = { 'title' : album.get_title(), 'images' : album.get_images() }
        self.callback("photographs", kwargs)

    def handle_user_event(self, event):
        '''Handle screen specific user events unless the library is empty.'''
        if self.image_library.get_number_of_albums() == 0:
            return
        else:
            Screen.handle_user_event(self, event)

    def _display_selected_album(self, event=None):
        '''Update of the list indicator'''
        self.li.set_current(self.menu.selected_index + 1)
        # 500ms timeout before preview is updated (fast scrolling)
        if self.timeout is not None:
            gobject.source_remove(self.timeout)
        self.timeout = gobject.timeout_add(500, self._update_album_preview,
            self.menu.selected_userdata)

