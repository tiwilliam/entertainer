# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''ImageCache - Handles image file caching.'''

import os
import time
import Image
import datetime
from pysqlite2 import dbapi2 as sqlite

from entertainerlib.thumbnailer import ImageThumbnailer
from entertainerlib.configuration import Configuration
from entertainerlib.logger import Logger

from entertainerlib.backend.components.mediacache.cache import Cache

class ImageCache(Cache):
    """
    This class is responsible of updating image cache as requested.

    ImageCache has a public interface that consists of 3 mehtods: addFile,
    removeFile and updateFile. All these methods get filename as a parameter.
    When ImageCache is called with filename it checks if the filename is
    supported format. This is done simply by checking the file extension.

    Supported file formats are: JPEG
    """
    # Supported file formats
    SUPPORTED_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png']

    def __init__(self):
        """
        Create a new ImageCache.

        Creates a new database if not already exists and opens a connection
        to it.
        """
        self.logger = Logger().getLogger(
            'backend.components.mediacache.ImageCache')
        self.config = Configuration()

        if not os.path.exists(self.config.IMAGE_DB):
            self._createImageCacheDatabase()
        self.db_conn = sqlite.connect(self.config.IMAGE_DB)
        self.db_cursor = self.db_conn.cursor()

    def clearCache(self):
        """
        Clean image cache completely.

        Clean cache database and remove all thumbnails.
        """
        thumbnails = os.listdir(self.config.IMAGE_THUMB_DIR)
        for element in thumbnails:
            thumb_file = os.path.join(self.config.IMAGE_THUMB_DIR, element)
            try:
                os.remove(thumb_file)
            except OSError:
                self.logger.error(
                    "Media manager couldn't remove thumbnail : %s"
                    % thumb_file)
        os.remove(self.config.IMAGE_DB)
        self._createImageCacheDatabase()


    def addFile(self, filename):
        """
        Add image file to the cache. Do nothing if file is already cached.
        """
        filename = filename.encode('utf8')
        if (not self.isFileInCache(filename) and
            self.isSupportedFormat(filename)):
            # Do not add album thumbnail to images
            if (filename[filename.rfind('/') +1:filename.rfind('.')] ==
                ".entertainer_album"):
                return
            self._addJPEGfile(filename)

    def removeFile(self, filename):
        """
        Remove image file from the cache. Do nothing if file is not in cache.
        """
        # Remove image file
        if self.isFileInCache(filename):
            self.db_cursor.execute("""SELECT hash
                                        FROM image
                                        WHERE filename=:fn""",
                                        { "fn" : filename})
            result = self.db_cursor.fetchall()
            if len(result) > 0:
                name = result[0][0] + '.jpg'
                thumb = os.path.join(self.config.IMAGE_THUMB_DIR, name)
                try:
                    os.remove(thumb)
                except OSError:
                    self.logger.error("Couldn't remove thumbnail: " + thumb)
                self.db_cursor.execute("""DELETE
                                            FROM image
                                            WHERE filename=:fn""",
                                            { "fn" : filename })
                self.db_conn.commit()

    def updateFile(self, filename):
        """Update image file that is already in the cache."""
        if self.isFileInCache(filename):
            self.removeFile(filename)
            self.addFile(filename)

    def addDirectory(self, path):
        """
        Adds a new directory to the cache. Sub directories are
        added recursively and all files in them.
        """
        # pylint: disable-msg=W0612
        if not os.path.isdir(path) or not os.path.exists(path):
            self.logger.error(
                "Adding a directory to the image cache failed. " +
                "Path doesn't exist: " + path)
        else:
            for root, dirs, files in os.walk(path):
                if os.path.split(root)[-1][0] == ".":
                    continue
                if not self.isDirectoryInCache(root):
                    self._addAlbum(root)

                for name in files:
                    if os.path.split(name)[-1][0] == ".":
                        continue
                    if self.isSupportedFormat(name):
                        self.addFile(os.path.join(root, name))
                        time.sleep(float(self.SLEEP_TIME_BETWEEN_FILES) / 1000)

    def removeDirectory(self, path):
        """
        Removes directory from the cache. Also removes all subdirectories
        and all files in them.

        @param path - Absolute path
        """
        # Remove image file thumbnails
        self.db_cursor.execute("""SELECT hash
                                    FROM image
                                    WHERE filename LIKE '""" + path + "%'")
        for row in self.db_cursor:
            thumb_file = row[0] + ".jpg"
            os.remove(os.path.join(self.config.IMAGE_THUMB_DIR, thumb_file))

        # Remove folder thumbnails
        self.db_cursor.execute("""SELECT hash
                                    FROM album
                                    WHERE path LIKE '""" + path + "%'")
        for row in self.db_cursor:
            thumb_file = row[0] + ".jpg"
            os.remove(os.path.join(self.config.IMAGE_THUMB_DIR, thumb_file))

        # Clean cache database
        self.db_cursor.execute(
            "DELETE FROM album WHERE path LIKE '" + path + "%'")
        self.db_cursor.execute(
            "DELETE FROM image WHERE album_path LIKE '" + path + "%'")
        self.db_conn.commit()

    def updateDirectory(self, path):
        """
        Update directory.
        """
        self.removeDirectory(path)
        self.addDirectory(path)

    def isFileInCache(self, filename):
        """Check if file is already in cache. Returns boolean value."""
        self.db_cursor.execute("""SELECT *
                                    FROM image
                                    WHERE filename=:fn""", { "fn" : filename })
        result = self.db_cursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

    def isDirectoryInCache(self, path):
        """Check if album is already in cache. Returns boolean value."""
        self.db_cursor.execute("""SELECT *
                                    FROM album
                                    WHERE path=:p""", { "p" : path})
        result = self.db_cursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

    def isSupportedFormat(self, filename):
        """Check if file is supported."""
        if (filename[filename.rfind('.') + 1 :].lower() in
            self.SUPPORTED_FILE_EXTENSIONS):
            return True
        else:
            return False

    def _createImageCacheDatabase(self):
        """Creates a image cache database file."""
        db_conn = sqlite.connect(self.config.IMAGE_DB)
        db_cursor = db_conn.cursor()
        db_cursor.execute(
            """
            CREATE TABLE image(
                filename TEXT,
                album_path TEXT,
                title TEXT,
                description TEXT,
                date DATE,
                time TIME,
                width INTEGER,
                height INTEGER,
                filesize LONG,
                hash VARCHAR(32),
                PRIMARY KEY(filename))""")

        db_cursor.execute(
            """
            CREATE TABLE album(
                path TEXT,
                title TEXT,
                description TEXT,
                hash VARCHAR(32),
                PRIMARY KEY(path))""")
        db_conn.commit()
        db_conn.close()
        self.logger.debug("ImageCache database created successfully")

    def _addAlbum(self, path):
        """
        Create a new album into image cache. Folders are handled as albums.
        Nested folders are not nested in database! All albums are on top level.
        """

        album_info = os.path.join(path, ".entertainer_album.info")
        album_thumb = os.path.join(path, ".entertainer_album.jpg")

        # Get album information
        if os.path.exists(album_info):
            try:
                inf_f = open(album_info)
                a_title = inf_f.readline()[6:]
                a_description = inf_f.readline()[12:]
            except IOError:
                a_title = path[path.rfind('/')+1:].replace('_',' ').title()
                a_description = ""
        else:
            a_title = path[path.rfind('/')+1:].replace('_',' ').title()
            a_description = ""

        if os.path.exists(album_thumb):
            thumbnailer = ImageThumbnailer(album_thumb)
            thumbnailer.create_thumbnail()
            a_hash = thumbnailer.get_hash()
        else:
            a_hash = ""

        album_row = (path, a_title, a_description, a_hash)
        self.db_cursor.execute(
            """
            INSERT INTO album(path, title, description, hash)
            VALUES(?,?,?,?)
            """, album_row)
        self.db_conn.commit()
        #print "Album added to cache: " + a_title

    def _addJPEGfile(self, filename):
        """
        Add JPEG image to the image cache. Raises exception if adding fails.

        Process:
            - Open file
            - Get image date and time
            - Get image title and description
            - Get image size
            - Generate thumbnail / get hash from thumbnailer
            - Insert data to image cache database
        """
        tmp = datetime.datetime.fromtimestamp(os.stat(filename)[-1])
        timestamp = [str(tmp.year) + "-" + str(tmp.month) + "-" +
            str(tmp.day), str(tmp.hour) + ":" + str(tmp.minute) + ":" +
            str(tmp.second)]

        # Generate name from filename
        tmp = filename[filename.rfind('/') + 1 : filename.rfind('.')]
        title = tmp.replace('_',' ').title() # Make title more attractive
        description = "" # No description for this image file

        try:
            im = Image.open(filename)
            width, height = im.size
        except IOError:
            self.logger.error("Couldn't identify image file: " + filename)
            return

        # Create thumbnail and return hash
        thumbnailer = ImageThumbnailer(filename)
        thumbnailer.create_thumbnail()
        thumb_hash = thumbnailer.get_hash()
        del thumbnailer
        album_path = filename[:filename.rfind('/')]

        db_row = (filename, # Filename (full path)
                  title, # Title of the image
                  description, # Description of the image
                  timestamp[0], # Image's taken date
                  timestamp[1], # Image's taken time
                  width,  # Image's width
                  height, # Image's height
                  os.path.getsize(filename), # Image file size in bytes
                  thumb_hash, # Thumbnail hash (hash of the filename)
                  album_path) # Path of the album (folder of this image)

        self.db_cursor.execute(
            """
            INSERT INTO image(filename,
                title,
                description,
                date,
                time,
                width,
                height,
                filesize,
                hash,
                album_path)
                VALUES(?,?,?,?,?,?,?,?,?,?)""", db_row)
        self.db_conn.commit()

