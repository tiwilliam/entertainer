# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''VideoCache - Handles video file cache.'''

import os
import time
from pysqlite2 import dbapi2 as sqlite

from entertainerlib.thumbnailer import VideoThumbnailer
from entertainerlib.configuration import Configuration
from entertainerlib.logger import Logger

from entertainerlib.backend.components.mediacache.cache import Cache
from entertainerlib.backend.components.mediacache.video_metadata_search import (
    VideoMetadataSearch)

class VideoCache(Cache):
    """Handles video file cache."""

    # Supported file extensions
    __SUPPORTED_FILE_EXTENSIONS = [
        'avi', 'mpg', 'mpeg', 'mov', 'wmv', 'ogm', 'mkv', 'mp4', 'm4v'
        ]

    # SQLite database stuff
    __db_conn = None
    __db_cursor = None

    # Thread lock for metadata search
    __metadata_lock = None

    def __init__(self):
        self.logger = Logger().getLogger(
            'backend.components.mediacache.VideoCache')
        self.config = Configuration()

        if not os.path.exists(self.config.VIDEO_DB):
            self.__createVideoCacheDatabase()
        self.__db_conn = sqlite.connect(self.config.VIDEO_DB)
        self.__db_cursor = self.__db_conn.cursor()

    def clearCache(self):
        """
        Clear video cache.
        Clean cache database and remova all metadata.
        """
        covers = os.listdir(self.config.MOVIE_ART_DIR)
        for element in covers:
            if element[-3:] == "jpg":
                os.remove(os.path.join(self.config.MOVIE_ART_DIR, element))

        os.remove(self.config.VIDEO_DB)
        self.__createVideoCacheDatabase()

    def addFile(self, filename):
        """
        This method adds a new file to the cache.
        """
        filename = filename.encode('utf8')
        if not self.isFileInCache(filename) and \
            self.isSupportedFormat(filename):
            self._addVideoFile(filename)

    def removeFile(self, filename):
        """
        This method removes file from the cache.
        """
        print "removeFile(): " + filename
        if self.isFileInCache(filename):
            self.__db_cursor.execute(
                """
                SELECT title, hash, series_title
                FROM videofile, metadata
                WHERE videofile.filename=:fn
                AND videofile.filename=metadata.filename""",
                { "fn" : filename })
            result = self.__db_cursor.fetchall()
            title = result[0][0]
            thash = result[0][1]
            series = result[0][2]

            # Series cover art is named by series title (not episode title)
            if series is not None and len(series) != 0:
                title = series

            # Generate absolute path of thumbnail and cover art
            art = os.path.join(self.config.MOVIE_ART_DIR, str(title) + ".jpg")
            thumb = os.path.join(self.config.VIDEO_THUMB_DIR,
                str(thash) + ".jpg")

            # Remove video from video cache database
            self.__db_cursor.execute('''DELETE FROM videofile
                                    WHERE filename=:fn''',
                                    { "fn" : filename })
            self.__db_cursor.execute('''DELETE FROM metadata
                                    WHERE filename=:fn''',
                                    { "fn" : filename })
            self.__db_conn.commit()

            # Remove thumbnail and cover art
            if os.path.exists(art) and not self.__hasSeriesEpisodes(series):
                os.remove(art)
            if os.path.exists(thumb):
                os.remove(thumb)

    def updateFile(self, filename):
        """
        This method is executed when a file, that is already in cache, changes.
        """
        if self.isFileInCache(filename):
            self.removeFile(filename)
            self.addFile(filename)

    def addDirectory(self, path):
        """
        This method adds a new directory to the cache. Sub directories are
        added recursively and all files in them.
        """
        if not os.path.isdir(path) or not os.path.exists(path):
            self.logger.error(
                "Adding a directory to the video cache failed. " +
                "Path doesn't exist: '" + path + "'")
        else:
            self.logger.debug(
                "Adding a directory to the video cache. Path is: '" +
                path + "'")
            # pylint: disable-msg=W0612
            for root, dirs, files in os.walk(path):
                for name in files:
                    self.addFile(os.path.join(root, name))
                    time.sleep(float(self.SLEEP_TIME_BETWEEN_FILES) / 1000)

    def removeDirectory(self, path):
        """
        This method removes directory from the cache. Also removes all
        subdirectories and all files in them.
        """
        self.__db_cursor.execute("""SELECT filename
                                    FROM videofile
                                    WHERE filename LIKE '""" + path + "%'")
        result = self.__db_cursor.fetchall()
        for row in result:
            self.removeFile(row[0])

    def updateDirectory(self, path):
        """
        This method is executed when a directory, that is already in cache,
        changes.
        """
        self.removeDirectory(path)
        self.addDirectory(path)

    def isDirectoryInCache(self, path):
        """
        This method returns True if given directory is in cache. Otherwise
        method returns False.
        """
        self.__db_cursor.execute("""SELECT * FROM videofile
                                    WHERE filename LIKE '""" + path + "%'")
        result = self.__db_cursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

    def isFileInCache(self, filename):
        """
        This method returns True if given file is in cache. Otherwise
        method returns False.
        """
        self.__db_cursor.execute("""SELECT *
                                    FROM videofile
                                    WHERE filename=:fn""",
                                    { "fn" : filename})
        result = self.__db_cursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

    def isSupportedFormat(self, filename):
        """Check if file is supported."""
        if (self.__getFileExtension(filename) in
            self.__SUPPORTED_FILE_EXTENSIONS):
            return True
        else:
            return False

    def __createVideoCacheDatabase(self):
        """Creates a video cache database file."""
        db_conn = sqlite.connect(self.config.VIDEO_DB)
        db_cursor = db_conn.cursor()
        db_cursor.execute("""CREATE TABLE videofile(
                             filename TEXT,
                             hash VARCHAR(32),
                             length INTEGER,
                             resolution VARCHAR(16),
                             PRIMARY KEY(filename))""")

        db_cursor.execute("""CREATE TABLE metadata(
                             type VARCHAR(16) DEFAULT 'CLIP',
                             filename TEXT,
                             title TEXT,
                             series_title VARCHAR(128),
                             runtime INTEGER,
                             genres VARCHAR(128),
                             rating INTEGER,
                             year VARCHAR(16),
                             plot_outline TEXT,
                             plot TEXT,
                             season INTEGER,
                             episode INTEGER,
                             actor_1 VARCHAR(128),
                             actor_2 VARCHAR(128),
                             actor_3 VARCHAR(128),
                             actor_4 VARCHAR(128),
                             actor_5 VARCHAR(128),
                             writer_1 VARCHAR(128),
                             writer_2 VARCHAR(128),
                             director_1 VARCHAR(128),
                             director_2 VARCHAR(128),
                             PRIMARY KEY(filename))""")

        db_conn.commit()
        db_conn.close()
        self.logger.debug("VideoCache database created successfully")

    def __getFileExtension(self, filename):
        """Return lower case file extension"""
        return filename[filename.rfind('.') + 1 :].lower()

    def _addVideoFile(self, filename):
        """Add video file to the video cache."""
        # Generate thumbnail
        thumbnailer = VideoThumbnailer(filename)
        thumbnailer.create_thumbnail()
        thash = thumbnailer.get_hash()
        del thumbnailer

        self.__db_cursor.execute("""INSERT INTO videofile(filename, hash)
                                    VALUES (:fn, :hash)""",
                                    { 'fn': filename, 'hash': thash, } )
        self.__db_cursor.execute("""INSERT INTO metadata(filename)
                                    VALUES (:fn)""",
                                    { "fn" : filename } )
        self.__db_conn.commit()
        if self.config.download_metadata:
            self.__searchMetadata(filename)

    def __searchMetadata(self, filename):
        """Search metadata for video file from the Internet."""
        search_thread = None
        search_thread = VideoMetadataSearch(filename)

        if search_thread is not None:
            search_thread.start()

    def __hasSeriesEpisodes(self, series_title):
        """
        Return True if there are episodes for given series, otherwise False.
        This is used when removing file from cache.
        """
        if len(series_title) == 0:
            return False
        else:
            self.__db_cursor.execute("""SELECT *
                                        FROM metadata
                                        WHERE series_title=:sn""",
                                        { "sn" : series_title} )
            result = self.__db_cursor.fetchall()
            if len(result) == 0:
                return False
            else:
                return True

