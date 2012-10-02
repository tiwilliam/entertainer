# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''MusicCache - Audio file cache.'''

import os
import time
import shutil

import eyeD3
import ogg.vorbis
from pysqlite2 import dbapi2 as sqlite

from entertainerlib.backend.components.mediacache.cache import Cache
from entertainerlib.configuration import Configuration
from entertainerlib.download import AlbumArtDownloader
from entertainerlib.logger import Logger


class MusicCache(Cache):
    """
    Handles audio file cache.
    """

    # Supported file formats
    __SUPPORTED_FILE_EXTENSIONS = ['mp3', 'ogg']

    # SQLite database stuff
    __db_conn = None
    __db_cursor = None

    # Default values
    __DEFAULT = { "artist" : "Unknown artist",
                  "album" : "Unknown album",
                  "title" : "Unknown track",
                  "genre" : "Unknown" }

    def __init__(self):
        """Create a new music database object."""
        self.logger = Logger().getLogger(
            'backend.components.mediacache.MusicCache')
        self.config = Configuration()

        if not os.path.exists(self.config.MUSIC_DB):
            self.__createMusicCacheDatabase()
        self.__db_conn = sqlite.connect(self.config.MUSIC_DB)
        self.__db_cursor = self.__db_conn.cursor()

    def clearCache(self):
        """
        Clear music cache.

        Clean cache database and remova all albumart.
        """
        covers = os.listdir(self.config.ALBUM_ART_DIR)
        for element in covers:
            os.remove(os.path.join(self.config.ALBUM_ART_DIR, element))

        os.remove(self.config.MUSIC_DB)
        self.__createMusicCacheDatabase()

    def addFile(self, filename):
        """Add audio file to the cache."""
        filename = filename.encode('utf8')
        if (not self.isFileInCache(filename) and
            self.isSupportedFormat(filename)):
            if self.__getFileExtension(filename) == "mp3":
                self.__addMP3file(filename)
            elif self.__getFileExtension(filename) == "ogg":
                self.__addOGGfile(filename)

    def removeFile(self, filename):
        """Remove audio file from the cache."""
        if self.isFileInCache(filename):
            # Check if we should remove albumart
            self.__db_cursor.execute("""SELECT artist, album
                                        FROM track
                                        WHERE filename=:fn""",
                                        { "fn" : filename })
            result = self.__db_cursor.fetchall()
            artist = result[0][0]
            album = result[0][1]
            self.__db_cursor.execute(
                """
                SELECT *
                FROM track
                WHERE artist=:artist
                AND album=:album""",
                { "artist" : artist, "album" : album})
            result = self.__db_cursor.fetchall()

            # If only one found then it's the file that is going to be removed
            if (len(result) == 1 and artist != self.__DEFAULT['artist'] and
                album != self.__DEFAULT['album']):
                albumart_file = artist + " - " + album + ".jpg"
                try:
                    os.remove(os.path.join(self.config.ALBUM_ART_DIR,
                        albumart_file))
                except OSError:
                    self.logger.error("Couldn't remove albumart: " +
                        os.path.join(self.config.ALBUM_ART_DIR, albumart_file))

            # Remove track from cache
            self.__db_cursor.execute("""DELETE FROM track
                                        WHERE filename=:fn""", {
                                            "fn" : filename})
            self.__db_cursor.execute("""DELETE FROM playlist_relation
                                        WHERE filename=:fn""", {
                                            "fn" : filename})
            self.__db_conn.commit()

    def updateFile(self, filename):
        """Update audio file that is already in the cache."""
        if self.isFileInCache(filename):
            self.removeFile(filename)
            self.addFile(filename)

    def addDirectory(self, path):
        """Add directory that contains audio files to the cache."""
        # pylint: disable-msg=W0612
        if not os.path.isdir(path) or not os.path.exists(path):
            self.logger.error(
                "Adding a directory to the music cache failed. " +
                "Path doesn't exist: " + path)
        else:
            for root, dirs, files in os.walk(path):
                for name in files:
                    self.addFile(os.path.join(root, name))
                    time.sleep(float(self.SLEEP_TIME_BETWEEN_FILES) / 1000)


    def removeDirectory(self, path):
        """Remove directory from the cache."""
        # Get current artist and albums that are on the removed path
        self.__db_cursor.execute(
            """
            SELECT DISTINCT artist, album
            FROM track
            WHERE filename LIKE '
            """ + path + "%'")
        result = self.__db_cursor.fetchall()

        # Remove tracks from database
        self.__db_cursor.execute(
            "DELETE FROM track WHERE filename LIKE '" + path + "%'")
        self.__db_cursor.execute(
            "DELETE FROM playlist_relation WHERE filename LIKE '" +
            path + "%'")
        self.__db_conn.commit()

        # Check which album art we should remove
        for element in result:
            artist = element[0]
            album = element[1]
            self.__db_cursor.execute("""SELECT *
                                        FROM track
                                        WHERE artist=:artist
                                        AND album=:album""",
                                        { "artist" : artist, "album" : album})
            found = self.__db_cursor.fetchall()
            # After delete there is no artist, album combination, so we can
            # remove album art
            if (len(found) == 0 and artist != self.__DEFAULT['artist'] and
                album != self.__DEFAULT['album']):
                albumart_file = artist + " - " + album + ".jpg"
                try:
                    os.remove(os.path.join(self.config.ALBUM_ART_DIR,
                        albumart_file))
                except OSError:
                    self.logger.error(
                        "Couldn't remove albumart: " +
                        os.path.join(self.config.ALBUM_ART_DIR, albumart_file))

    def updateDirectory(self, path):
        """Update directory that is already in the cache."""
        self.removeDirectory(path)
        self.addDirectory(path)

    def isDirectoryInCache(self, path):
        """Check if directory is in cache."""
        self.__db_cursor.execute(
            "SELECT * FROM track WHERE filename LIKE '" + path + "%'")
        result = self.__db_cursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

    def isFileInCache(self, filename):
        """Check if file is in cache."""
        self.__db_cursor.execute("""SELECT *
                                    FROM track
                                    WHERE filename=:fn""", {"fn":filename} )
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

    def __createMusicCacheDatabase(self):
        """Creates a music cache database file."""
        db_conn = sqlite.connect(self.config.MUSIC_DB)
        db_cursor = db_conn.cursor()
        db_cursor.execute("""CREATE TABLE track(
                             filename TEXT,
                             title VARCHAR(255),
                             artist VARCHAR(255),
                             album VARCHAR(255),
                             tracknumber INTEGER,
                             bitrate INTEGER,
                             year INTEGER,
                             rating INTEGER DEFAULT NULL,
                             length INTEGER,
                             genre VARCHAR(128),
                             comment TEXT,
                             lyrics TEXT DEFAULT "",
                             PRIMARY KEY(filename))""")

        db_cursor.execute("""CREATE TABLE playlist(
                             title TEXT,
                             PRIMARY KEY(title))""")

        db_cursor.execute("""CREATE TABLE playlist_relation(
                             title TEXT,
                             filename TEXT,
                             PRIMARY KEY(title, filename))""")
        db_conn.commit()
        db_conn.close()
        self.logger.debug("MusicCache database created successfully")

    def __getFileExtension(self, filename):
        """Return lower case file extension"""
        return filename[filename.rfind('.') + 1 :].lower()

    def __addMP3file(self, filename):
        """
        Add mp3 file to the music cache

        Process:
            - Open file
            - Get tags
            - Insert data to the music cache database
        """
        try:
            mp3_file = eyeD3.Mp3AudioFile(filename, eyeD3.ID3_ANY_VERSION)
            tags = mp3_file.getTag()
        except ValueError: # Tags are corrupt
            self.logger.error("Couldn't read ID3tags: " + filename)
            return

        if tags is None:
            self.logger.error("Couldn't read ID3tags: " + filename)
            return

        # Get track lenght in seconds
        length = mp3_file.getPlayTime()

        # Get avarage bitrate
        bitrate = mp3_file.getBitRate()[1]

        # Get artist name
        artist = tags.getArtist()
        if artist is None or len(artist) == 0:
            artist = self.__DEFAULT['artist']

        # Get album name
        album = tags.getAlbum()
        if album is None or len(album) == 0:
            album = self.__DEFAULT['album']

        # Get track title
        title = tags.getTitle()
        if title is None or len(title) == 0:
            title = self.__DEFAULT['title']

        # Get track genre
        genre = str(tags.getGenre())
        if genre is None or len(genre) == 0:
            genre = self.__DEFAULT['genre']

        # Get track number
        tracknumber = tags.getTrackNum()[0]
        if tracknumber is None:
            tracknumber = 0

        # Get track comment
        comment = tags.getComment()
        if comment is None or len(comment) == 0:
            comment = ""

        # Get track release year
        year = tags.getYear()
        if year is None or len(year) == 0:
            year = 0

        db_row = (filename, title, artist, album, genre, length, tracknumber,
            bitrate, comment, year)
        self.__db_cursor.execute("""INSERT INTO track(filename,
                                                      title,
                                                      artist,
                                                      album,
                                                      genre,
                                                      length,
                                                      tracknumber,
                                                      bitrate,
                                                      comment,
                                                      year)
                                    VALUES(?,?,?,?,?,?,?,?,?,?)""", db_row)
        self.__db_conn.commit()

        # Get song lyrics
        lyrics = tags.getLyrics()
        if len(lyrics) != 0:
            lyrics = str(lyrics[0])
            self.__db_cursor.execute("""UPDATE track
                                        SET lyrics=:lyrics
                                        WHERE filename=:fn""",
                                        { "lyrics" : lyrics,
                                          "fn" : filename })
            self.__db_conn.commit()

        # Get album art
        self.__searchAlbumArt(artist, album, filename)

    def __addOGGfile(self, filename):
        """
        Add ogg file to the music cache

        Process:
            - Open file
            - Get tags
            - Insert data to the music cache database
        """
        ogg_file = ogg.vorbis.VorbisFile(filename)
        info = ogg_file.comment().as_dict()

        # Get length
        length = round(ogg_file.time_total(-1))

        # Get avarage bitrate
        bitrate = round(ogg_file.bitrate(-1) / 1000)

        # Get album name
        if info.has_key('ALBUM'):
            album = info['ALBUM'][0]
        else:
            album = self.__DEFAULT['album']

        # Get artist name
        if info.has_key('ARTIST'):
            artist = info['ARTIST'][0]
        else:
            artist = self.__DEFAULT['artist']

        # Get track title
        if info.has_key('TITLE'):
            if info.has_key('VERSION'):
                title = (str(info['TITLE'][0]) +
                    " (" + str(info['VERSION'][0]) + ")")
            else:
                title = info['TITLE'][0]
        else:
            title = self.__DEFAULT['title']

        # Get track number
        if info.has_key('TRACKNUMBER'):
            track_number = info['TRACKNUMBER'][0]
        else:
            track_number = 0

        # Get track genre
        if info.has_key('GENRE'):
            genre = info['GENRE'][0]
        else:
            genre = self.__DEFAULT['genre']

        # Get track comment
        if info.has_key('DESCRIPTION'):
            comment = info['DESCRIPTION'][0]
        elif info.has_key('COMMENT'):
            comment = info['COMMENT'][0]
        else:
            comment = ""

        # Get track year
        if info.has_key('DATE'):
            date = info['DATE'][0]
            year = date[:date.find('-')]
        else:
            year = 0

        db_row = (filename, title, artist, album, genre, length, track_number,
            bitrate, comment, year)
        self.__db_cursor.execute("""INSERT INTO track(filename,
                                                      title,
                                                      artist,
                                                      album,
                                                      genre,
                                                      length,
                                                      tracknumber,
                                                      bitrate,
                                                      comment,
                                                      year)
                                    VALUES(?,?,?,?,?,?,?,?,?,?)""", db_row)
        self.__db_conn.commit()

        # Get album art
        self.__searchAlbumArt(artist, album, filename)

    def __searchAlbumArt(self, artist, album, filename):
        """Execute album art search thread"""

        # base64 encode artist and album so there can be a '/' in the artist or
        # album
        artist_album = artist + " - " + album
        artist_album = artist_album.encode("base64")

        album_art_file = os.path.join(
            self.config.ALBUM_ART_DIR, artist_album + ".jpg")
        if not os.path.exists(album_art_file):
            # Search for local albumart
            if os.path.exists(filename[:filename.rfind('/')+1]+"cover.jpg"):
                shutil.copyfile(filename[:filename.rfind('/')+1]+"cover.jpg",
                    album_art_file)
            elif os.path.exists(filename[:filename.rfind('/')+1]+"folder.jpg"):
                shutil.copyfile(filename[:filename.rfind('/')+1]+"folder.jpg",
                    album_art_file)
            # Local not found -> try internet
            else:
                if self.config.download_album_art:
                    if album != "Unknown album" and artist != "Unknown Artist":
                        loader_thread = AlbumArtDownloader(album, artist,
                            self.config.ALBUM_ART_DIR)
                        loader_thread.start()

