# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Music Library - Interface for Entertainer music library cache'''

import os

import CDDB, DiscID
from pysqlite2 import dbapi2 as sqlite

from entertainerlib.client.medialibrary.playable import Playable
from entertainerlib.configuration import Configuration
from entertainerlib.download import LyricsDownloader


class AlbumHasNoTracks(Exception):
    '''Exception to handle Albums with no tracks'''
    pass

class TrackTypeError(TypeError):
    '''Exception to handle track errors'''
    pass

class MusicLibrary:
    '''Interface for Entertainer's music cache.'''

    def __init__(self):
        self.config = Configuration()

        if not os.path.exists(self.config.MUSIC_DB):
            raise Exception("Music database doesn't exist!")
        self.db_connection = sqlite.connect(self.config.MUSIC_DB)
        self.cursor = self.db_connection.cursor()

    def __del__(self):
        '''Close the connection when this object is destroyed.'''
        self.db_connection.close()

    def get_compact_disc_information(self):
        '''Get the CompactDisc object of the current disc in drive by querying
        CD information from an Internet database (CDDB).'''
        cdrom = DiscID.open()
        disc_id = DiscID.disc_id(cdrom)
        return CompactDisc(disc_id)

    def get_all_artists(self):
        '''Return all the artists names.'''
        self.cursor.execute("SELECT DISTINCT artist FROM track ORDER BY artist")

        artists = []
        for row in self.cursor:
            artists.append(row[0])
        return artists

    def get_tracks_by_artist(self, artist):
        '''Return track objects from the given artist.'''
        self.cursor.execute(
            """SELECT filename, title, tracknumber,  artist,  album,
                year, length, lyrics
               FROM   track
               WHERE  artist=:artist
               ORDER BY title""", { "artist" : artist})
        tracks = []
        for row in self.cursor:
            tracks.append(Track(row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], self._create_album))
        return tracks

    def get_all_albums(self):
        '''Return all the albums in the library.'''
        self.cursor.execute("SELECT DISTINCT album FROM track ORDER BY album")
        albums = []
        for row in self.cursor.fetchall():
            albums.append(self._create_album(row[0]))
        return albums

    def get_albums_by_artist(self, artist):
        '''Return all albums from the given artist.'''
        self.cursor.execute("""SELECT DISTINCT album
                          FROM track
                          WHERE artist=:artist
                          ORDER BY album""", { "artist" : artist})
        albums = []
        for row in self.cursor.fetchall():
            albums.append(self._create_album(row[0]))
        return albums

    def number_of_tracks(self):
        '''Return the number of tracks.'''
        self.cursor.execute("SELECT COUNT(filename) FROM track")
        result = self.cursor.fetchall()
        return result[0][0]

    def number_of_tracks_by_artist(self, artist):
        '''Return the number of tracks from the given artist.'''
        self.cursor.execute("""SELECT COUNT(filename)
                          FROM track
                          WHERE artist=:artist""", { "artist" : artist})
        result = self.cursor.fetchall()
        return result[0][0]

    def number_of_albums_by_artist(self, artist):
        '''Return the number of albums from the given artist.'''
        self.cursor.execute("""SELECT DISTINCT album
                          FROM track
                          WHERE artist=:artist
                          ORDER BY album""", { "artist" : artist})
        result = self.cursor.fetchall()
        return len(result)

    def save_lyrics(self, track, lyrics):
        '''Save the lyrics to the database.'''
        track.lyrics = lyrics # Be certain to save for this track instance,
                              # not just persistent storage
        self.cursor.execute(
            """UPDATE track SET lyrics=:lyrics WHERE filename=:fn""",
            { "lyrics" : lyrics, "fn" : track.filename})
        self.db_connection.commit()

    def _create_album(self, title):
        '''Factory method to create an Album object.'''
        self.cursor.execute(
            """SELECT filename, title, tracknumber,  artist,  album,
                year, length, lyrics
               FROM   track
               WHERE  album=:title
               ORDER BY tracknumber""", {"title" : title})

        length = 0
        tracks = []
        for row in self.cursor:
            tracks.append(Track(row[0], row[1], row[2], row[3], row[4], row[5],
                row[6], row[7], self._create_album))
            length += int(row[6])
        if len(tracks) == 0:
            raise AlbumHasNoTracks()

        artist = tracks[0].artist

        for track in tracks:
            if track.artist != artist:
                artist = _("Various")
                break

        encoded_path = artist + ' - ' + title
        encoded_path = encoded_path.encode('base64')
        album_art_url = os.path.join(self.config.ALBUM_ART_DIR,
            encoded_path + '.jpg')

        return Album(artist, title, length, tracks[0].year, album_art_url,
            tracks)


class Album(object):
    '''Representation of music album which contains tracks.'''

    def __init__(self, artist, title, length, year, album_art_url, tracks):
        self.config = Configuration()
        self.artist = artist
        self.title = title
        self.length = length
        self.year = year
        self.album_art_url = album_art_url
        self.tracks = tracks

    def has_album_art(self):
        '''Test if the album has album art.'''
        return os.path.exists(self.album_art_url)


class Track(Playable):
    '''Representation of a music track.'''

    def __init__(self, filename, title, number, artist, album, year, length,
        lyrics, create_album_callback):
        Playable.__init__(self)

        # Check that these fields are integers
        for field in [number, year, length]:
            if type(field) != int:
                raise TrackTypeError("%s is not an integer" % field)

        self.filename = filename
        self.title = title
        self.number = number
        self.artist = artist
        self._album = album
        self.year = year
        # Length of the track in seconds (example 240)
        self.length = length
        self._lyrics = lyrics
        self.create_album_callback = create_album_callback

    @property
    def album(self):
        '''Get the album object and use the callback if it's not an instance.'''
        if not isinstance(self._album, Album):
            album = self.create_album_callback(self._album)
            self._album = album
            return album
        else:
            return self._album

    @property
    def length_string(self):
        '''Return length as a human readable string. Example: 2:46.'''
        return str(self.length / 60) + ":" + str.zfill(str(self.length % 60), 2)

    def _get_lyrics(self):
        '''Get the track lyrics.'''
        return self._lyrics

    def _set_lyrics(self, lyrics):
        '''Set the lyrics. LyricsDownloader returns None if it can't find
        anything so ensure that using lyrics is always a string.'''
        if lyrics is None:
            self._lyrics = ''
        else:
            self._lyrics = lyrics

    lyrics = property(_get_lyrics, _set_lyrics)

    def has_lyrics(self):
        '''Test if the track has any lyrics.'''
        if self.lyrics == "":
            return False
        else:
            return True

    def fetch_lyrics(self, callback=False):
        '''Fetch lyrics from the Internet using the LyricsDownloader, use a
        callback function to indicate completion since LyricsDownloader is
        asynchronous. Callback function must take lyrics as only input
        parameter.'''
        if not callback:
            callback = self.set_lyrics
        if not self.has_lyrics():
            self.ld = LyricsDownloader(self.title, self.artist, callback)
            self.ld.search()

    def get_album_art_url(self):
        '''Get the album art location if it exists.'''
        if self.album.has_album_art():
            return self.album.album_art_url
        else:
            return None

    # Implement playable interface
    def get_title(self):
        '''Get the title.'''
        return self.title

    def get_type(self):
        '''Get the type.'''
        return Playable.AUDIO_STREAM

    def get_uri(self):
        '''Get the URI.'''
        return "file://" + self.filename


class CompactDisc(object):
    '''Representation of a CD.'''

    def __init__(self, disc_id):
        # Assume that no results will be found.
        self.artist = _("Unknown artist")
        self.length = 0
        self.title = _("Unknown title")
        self.tracks = []

        try:
            (query_status, query_info) = CDDB.query(disc_id)
        except IOError:
            # Set query_status to 0 to act like an unknown CD.
            query_status = 0

        # See CDDB documentation for more information.
        # http://cddb-py.sourceforge.net/CDDB/README
        # query_info variable's type depends on query_status

        if query_status == 200:
            # On 200, a dictionary containing three items is returned
            self._get_information_from_result_element(query_info, disc_id)
        elif query_status == 210 or query_status == 211:
            # On 211 or 210, a list will be returned as the second item.
            # Each element of the list will be a dictionary containing
            # three items, exactly the same as a single 200 success return.
            self._get_information_from_result_element(query_info[0], disc_id)
        else:
            # No metadata found for this disc
            for i in range(disc_id[1]):
                self.tracks.append(CompactDiscTrack(i + 1,
                    _("Unknown track %(num)s.") % {'num': str(i + 1)}, 0))

    def _get_information_from_result_element(self, result, disc_id):
        """Catch any information from a CDDB result dictionnary"""
        title = unicode(result['title'], "iso-8859-1")
        category = unicode(result['category'], "iso-8859-1")
        disc = unicode(result['disc_id'], "iso-8859-1")

        self.artist = title[:title.index(' / ')]
        self.title = title[title.index(' / ') + 3:]

        # Get track titles
        info = CDDB.read(category, disc)[1]
        for i in range(disc_id[1]):
            if i + 4 == len(disc_id):
                # We must calculate last track length in a different way
                length = disc_id[len(disc_id) - 1] - self.length
            else:
                # Calculate track length in seconds
                length = (disc_id[i + 3] - disc_id[ i + 2]) / 75

            self.length += length
            track_title = unicode(info['TTITLE' + str(i)], "iso-8859-1")
            self.tracks.append(CompactDiscTrack(i + 1, track_title, length))


class CompactDiscTrack(Playable):
    '''Representation of a CD track.'''

    def __init__(self, number, title, length):
        Playable.__init__(self)
        self.title = title
        self.uri = "cdda://" + str(number)
        self.length = length

    @property
    def length_string(self):
        '''Return length as a human readable string. Example: 2:46.'''
        return str(self.length / 60) + ":" + str.zfill(str(self.length % 60), 2)

    # Implement playable interface
    def get_title(self):
        '''Get the title.'''
        return self.title

    def get_type(self):
        '''Get the type.'''
        return Playable.AUDIO_STREAM

    def get_uri(self):
        '''Get the URI.'''
        return self.uri

