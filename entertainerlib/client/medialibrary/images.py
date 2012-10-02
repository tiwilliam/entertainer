# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Image Library - Interface for Entertainer image library cache'''

import os
from pysqlite2 import dbapi2 as sqlite

from entertainerlib.configuration import Configuration

class ImageLibrary:
    """Entertainer's image cache."""

    def __init__(self):
        self.config = Configuration()

        if not os.path.exists(self.config.IMAGE_DB):
            raise Exception("Image database doesn't exist!")

    def get_all_images(self):
        """
        Get list of image objects. List contains all images in library in
        albhabetical order.
        @return: List of Image objects
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute("""SELECT filename, album_path, title, description,
                                 date, time, width, height,filesize, hash
                          FROM   image
                          ORDER BY title""")
        images = []
        for row in cursor:
            images.append(Image(row[0], row[1], row[2], row[3], row[4],
                                row[5], row[6], row[7], row[8], row[9]))
        connection.close()
        return images

    def get_albums(self):
        """
        Get all albums in library as a list of ImageAlbum objects in
        albhabetical order.
        @return: List of ImageAlbum objects
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT path FROM album ORDER BY title")
        albums = []
        for row in cursor:
            albums.append(ImageAlbum(row[0]))
        connection.close()
        return albums

    def get_number_of_images(self):
        """
        Get the number of images in image library.
        @return: Integer
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(filename) FROM image")
        result = cursor.fetchall()
        num = result[0][0]
        connection.close()
        return num

    def get_number_of_albums(self):
        """
        Get the number of albums in image library.
        @return: Integer
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(path) FROM album")
        result = cursor.fetchall()
        num = result[0][0]
        connection.close()
        return num


class ImageAlbum:
    """
    ImageAlbum is a container that contains Images.

    Album has a title and optional description text.
    """

    def __init__(self, path):
        """Initialize album"""
        self.config = Configuration()

        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT path, title, description, hash FROM album WHERE path='%s'"
            % path)
        result = cursor.fetchall()
        self.__path = result[0][0]         # Path of the album
        self.__title = result[0][1]        # Title of the album
        self.__description = result[0][2]  # Description text for the album
        self.__thumbnail = None            # Thumbnail URL of the album
        if len(result[0][3]) > 0:
            self.__thumbnail = os.path.join(self.config.IMAGE_THUMB_DIR,
                 result[0][3] + ".jpg")
        connection.close()

    def get_path(self):
        """
        Get the absolute path of the album
        @return: String
        """
        return self.__path

    def get_title(self):
        """
        Get the title of the album
        @return: String
        """
        return self.__title

    def get_description(self):
        """
        Get the description of the album
        @return: String
        """
        return self.__description

    def get_album_thumbnail_url(self):
        """
        Get the album thumbnail URL. 'None' if there is no thumbnail.
        @return: String
        """
        return self.__thumbnail

    def get_number_of_images(self):
        """
        Get the number of images in this album.
        @return: Integer
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(filename) FROM image WHERE album_path='%s'"
            % self.__path)
        result = cursor.fetchall()
        connection.close()
        return result[0][0]

    def get_preview_images(self, number=3):
        """
        Get three images that can be used for creating a preview of
        the album.
        @param number: How many images should be returned
        @return: List of Image objects
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute("""SELECT filename, album_path, title, description,
                                 date, time, width, height,filesize, hash
                          FROM   image
                          WHERE  album_path=:path
                          ORDER BY title
                          LIMIT 0,:number""", { "path" : self.__path,
                                                "number" : number })
        images = []
        for row in cursor:
            images.append(Image(row[0], row[1], row[2], row[3], row[4],
                                row[5], row[6], row[7], row[8], row[9]))
        connection.close()
        return images

    def get_images(self):
        """
        Get images in this album as a list of Image objects.
        @return: List of Image objects
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute("""SELECT filename, album_path, title, description,
                                 date, time, width, height,filesize, hash
                          FROM   image
                          WHERE  album_path='%s'
                          ORDER BY title""" % self.__path)
        images = []
        for row in cursor:
            images.append(Image(row[0], row[1], row[2], row[3], row[4],
                                row[5], row[6], row[7], row[8], row[9]))
        connection.close()
        return images


class Image(object):
    """
    Image is a basic object of the Image library.
    """

    def __init__(self, filename, album_path, title, description,
                 date, time, width, height,filesize, thumb_hash):
        """Initialize image"""
        self.config = Configuration()

        # Filename of the image (full absolute path)
        self.__filename = filename
        # Album path of the album that contains this image
        self.__album_path = album_path
        self.__title = title                # Title of the image
        self.__description = description    # Description/Comment of the image
        self.__date = date                  # Taken date of image
        self.__time = time                  # Taken time of the image
        self.__width = width                # Width in pixels
        self.__height = height              # Height in pixels
        self.__filesize = filesize          # Image filesize in bytes
        self.__thumb_hash = thumb_hash      # Image thumbnail hash value

    def get_filename(self):
        """
        Get the filename of the image (absolute path).
        @return: String
        """
        return self.__filename

    def get_title(self):
        """
        Get the title ot the image.
        @return: String
        """
        return self.__title

    def get_description(self):
        """
        Get the description ot the image.
        @return: String
        """
        return self.__description

    def get_date(self):
        """
        Get the date of the image.
        @return: String
        """
        return self.__date

    def get_time(self):
        """
        Get the time of the image.
        @return: String
        """
        return self.__time

    def get_width(self):
        """
        Get the width of the image.
        @return: Integer
        """
        return int(self.__width)

    def get_height(self):
        """
        Get the height of the image.
        @return: Integer
        """
        return int(self.__height)

    def get_filesize(self):
        """
        Get the filesize (in bytes) of the image.
        @return: Integer
        """
        return int(self.__filesize)

    def get_thumbnail_url(self):
        """
        Get the absolute path of the thumbnail of this image.
        @return: String
        """
        return os.path.join(self.config.IMAGE_THUMB_DIR,
            self.__thumb_hash + ".jpg")

    def get_album(self):
        """
        Get the ImageAlbum object. Returned album contains this image.
        @return: String
        """
        connection = sqlite.connect(self.config.IMAGE_DB)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT path FROM album WHERE path='%s'" % self.__album_path)
        result = cursor.fetchall()
        connection.close()
        return ImageAlbum(result[0][0])

