# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Theme - Theme represents currently used theme.'''

import os
import sys
import ConfigParser
from ConfigParser import ParsingError

import gtk

class Theme:
    """
    Entertainer GUI theme.

    Object from this class represents currently used theme. All colors and
    imagefile paths should be queried from the object of this class. Theme
    object reads it's content from a current theme that is set in
    preferences.conf.
    """

    def __init__(self, theme_path):
        """
        Create a new theme. Read all data from the disk and initialize object.
        """
        self.theme_path = theme_path

        self.thumbnail = os.path.join(self.theme_path, "thumbnail.png")
        theme = ConfigParser.ConfigParser()
        try:
            theme.readfp(open(os.path.join(self.theme_path, "theme.conf")))
        except ParsingError:
            print "ParsingError: syntax error in theme file."
            sys.exit(1)
        except IOError:
            print "IOError: Couldn't read theme file."
            sys.exit(1)

        # Get theme information
        self.name = theme.get("Theme", "name")
        self.comment = theme.get("Theme", "comment")
        self.author = theme.get("Theme", "author")
        self.licence = theme.get("Theme", "licence")
        self.copyright = theme.get("Theme", "copyright")

        #The theme font must be pango compatible font, hence this code
        #checks the theme font against the pango list generated from a
        #pango context object and then sets self.font if the font is
        #compatible. Unfortunately the list can only be generated from a
        #gtk object at present.
        self._font = ""
        tmp_font = theme.get("Theme", "font")

        for font in gtk.TreeView().get_pango_context().list_families():
            if font.get_name() == tmp_font:
                self._font = tmp_font

        if self.font == "":
            self._font = "Arial"

        # Get theme colors
        self.color = {}
        self.color['background'] = theme.get(
            "Colors", "background").split(',')
        self.color['title'] = theme.get("Colors", "title").split(',')
        self.color['subtitle'] = theme.get("Colors", "subtitle").split(',')
        self.color['screentitle'] = theme.get(
            "Colors", "screentitle").split(',')
        self.color['text'] = theme.get("Colors", "text").split(',')
        self.color['menuitem_active'] = theme.get(
            "Colors", "menuitem_active").split(',')
        self.color['menuitem_inactive'] = theme.get(
            "Colors", "menuitem_inactive").split(',')
        self.color['arrow_foreground'] = theme.get(
            "Colors", "arrow_foreground").split(',')
        self.color['arrow_background'] = theme.get(
            "Colors", "arrow_background").split(',')

        # Build the image array : image[name] = filename
        self.image = {}
        self.build_image_array_with_folder("")
        self.build_image_array_with_folder("weather")

    def build_image_array_with_folder(self, folder):
        """Add every .png files to the image array"""
        img_path = os.path.join(self.theme_path, "images")

        # pylint: disable-msg=W0612
        for root, dirs, files in os.walk(os.path.join(img_path, folder)):
            for filename in files:
                ext = filename[filename.rfind('.') + 1 :].lower()
                name = filename[:filename.rfind('.')].lower()

                if (ext == "png"):
                    self.image[name] = os.path.join(img_path, folder, filename)

    def getName(self):
        """
        Get the name of the theme
        @return - Name of theme as string
        """
        return self.name

    def getComment(self):
        """
        Get comment of the theme
        @return - Comment of the theme as string
        """
        return self.comment

    def getAuthor(self):
        """
        Get the author of the theme
        @return - Author's name as string
        """
        return self.author

    def getLicence(self):
        """
        Get the licence of the theme
        @return - Licence information as string
        """
        return self.licence

    def getCopyright(self):
        """
        Get the copyright of the theme
        @return - Copyright information as string
        """
        return self.copyright

    @property
    def font(self):
        """
        Get name of the font
        @return - Name of the font as string
        """
        return self._font

    def getThumbnailURL(self):
        """
        Get URL to the theme's thumbnail image
        @return - Absolute path of the thumbnail as string
        """
        return self.thumbnail

    def getImage(self, element):
        """
        Get URL of the image for given element.
        @param element:
        @return - Absolute path of the image as string
        """
        if self.image.has_key(element) and os.path.exists(self.image[element]):
            return self.image[element]
        else:
            raise Exception("No image available for given element.")

    def get_color(self, element):
        """Return color for the element as a tuple of (r, b, g, a)."""
        if self.color.has_key(element):
            color = [int(ele) for ele in self.color[element]]
            return (color[0], color[1], color[2], color[3])
        else:
            # On error we return bright red.
            return (255, 0, 0, 255)

