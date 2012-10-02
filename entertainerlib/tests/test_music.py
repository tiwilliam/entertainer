# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests Music'''
# pylint: disable-msg=W0212

import os

from pysqlite2 import dbapi2 as sqlite

from entertainerlib.client.medialibrary.music import (
    Album, AlbumHasNoTracks,
    CompactDisc, CompactDiscTrack,
    MusicLibrary,
    Track, TrackTypeError)
from entertainerlib.client.medialibrary.playable import Playable
from entertainerlib.tests import EntertainerTest

class TestMusic(EntertainerTest):
    """This test class sets up the test database required for all test
    classes that need to access the music cache"""

    def setUp(self):
        EntertainerTest.setUp(self)

        self.debug = False
        # The location of album art is required for some tests
        self.art_path = self.config.ALBUM_ART_DIR

        connection = sqlite.connect(self.config.MUSIC_DB)
        self.cursor = connection.cursor()
        self.cursor.execute("""DROP TABLE IF EXISTS track""")
        self.cursor.execute("""CREATE TABLE track(
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
        # Populate the test database with enough information to make it useful
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    total = i + j + k # to get unique track numbers for albums
                    db_row = ('/filename/%s' % str(i) + str(j) + str(k),
                              'title%s' % str(i) + str(j),
                              'artist0',
                              'album%d' % j,
                              'genre%d' % i,
                              i + j + k, # length
                              total, # tracknumber
                              i, # bitrate
                              'comment%d' % i,
                              i  # year
                              )
                    self.cursor.execute("""INSERT INTO track(filename,
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

        connection.commit()

    def tearDown(self):
        """Clean up after the test"""
        EntertainerTest.tearDown(self)

        connection = sqlite.connect(self.config.MUSIC_DB)
        cursor = connection.cursor()
        cursor.execute("""DROP TABLE IF EXISTS track""")
        connection.commit()
        connection.close()


class TestTrack(TestMusic):

    def setUp(self):
        TestMusic.setUp(self)
        self.music_library = MusicLibrary()
        self.track = Track('/path/to/track.mp3', # filename
                           'title',
                           1, # tracknumber
                           'artist0',
                           'album0',
                           2008, # year
                           240, # length
                           'lyrics',
                            self.music_library._create_album)

    def test_constructor(self):
        '''Test that a Track object is created.'''
        self.assertTrue(isinstance(self.track, Track))
        self.assertEqual(self.track.artist, 'artist0')
        self.assertEqual(self.track.filename, '/path/to/track.mp3')
        self.assertEqual(self.track.length, 240)
        self.assertEqual(self.track.length_string, '4:00')
        self.assertEqual(self.track.lyrics, 'lyrics')
        self.assertEqual(self.track.number, 1)
        self.assertEqual(self.track.title, 'title')
        self.assertEqual(self.track.year, 2008)

    def test_bad_constructor(self):
        '''Test that bad track construction raises an exception for the integer
        fields.'''
        for i in [2, 5, 6]:
            t = ['', '', 1, '', '', 2, 3, '']
            t[i] = str(t[i])
            self.assertRaises(TrackTypeError, Track, t[0], t[1], t[2], t[3],
                t[4], t[5], t[6], t[7], None)

    def test_album_property(self):
        '''Test that an album object is returned.'''
        result = self.track.album
        self.assertTrue(isinstance(result, Album))
        self.assertEqual(result.title, 'album0')

    def test_bad_album(self):
        '''Test that a bad album in the track returns AlbumHasNoTracks.'''
        bad_track = Track('', '', 1, '', 'foo-bar-baz**', 2, 3, '',
            self.music_library._create_album)
        try:
            # pylint: disable-msg=W0612
            album = bad_track.album
            self.fail()
        except AlbumHasNoTracks:
            pass

    def test_get_album_art_url(self):
        '''Test that the album art url is returned.'''
        album_artist = "artist0 - album0"
        album_artist = album_artist.encode("base64")
        album_art = os.path.join(self.art_path, album_artist + ".jpg")
        open(album_art, "wb").close()
        result = self.track.get_album_art_url()
        self.assertEqual(result, album_art)
        if os.path.exists(album_art):
            os.remove(album_art)

        result = self.track.get_album_art_url()
        self.assertEqual(result, None)

    def test_lyrics_property(self):
        '''Test the lyrics property.'''
        self.track.lyrics = 'some new lyrics'
        self.assertEqual(self.track.lyrics, 'some new lyrics')

        self.track.lyrics = None
        self.assertEqual(self.track.lyrics, '')

    def test_get_type(self):
        '''Test that the type is returned.'''
        self.assertEqual(self.track.get_type(), Playable.AUDIO_STREAM)

    def test_get_uri(self):
        '''Test that the uri is returned.'''
        self.assertEqual(self.track.get_uri(), 'file:///path/to/track.mp3')


class TestMusicLibrary(TestMusic):
    '''Tests MusicLibrary'''

    def setUp(self):
        TestMusic.setUp(self)
        self.musiclibrary = MusicLibrary()

    def test_music_library_constructor(self):
        '''Test that the music library contructor works.'''
        self.assertTrue(isinstance(self.musiclibrary, MusicLibrary))

    def testGetAllArtists(self):
        """testGetAllArtists - Ensures that all artists are returned from
        the music library"""
        result = self.musiclibrary.get_all_artists()
        self.assertEqual(result, ['artist0'])

    def testGetTracksByArtist(self):
        """testGetTracksByArtist - Ensure tracks by a certain artist are
        returned"""
        result = self.musiclibrary.get_tracks_by_artist('artist0')
        self.assertEqual(len(result), 8)
        for i in result:
            self.assertEqual(i.artist, 'artist0')

    def testGetTracksByUnknownArtist(self):
        """testGetTracksByUnknownArtist - Ensure proper handling of an missing
        artist in the cache"""
        self.assertEquals(
            len(self.musiclibrary.get_tracks_by_artist('foo')), 0)

    def testGetAllAlbums(self):
        """testGetAllAlbums - Ensures all albums are returned"""
        result = self.musiclibrary.get_all_albums()
        for i in result:
            self.assertTrue(isinstance(i, Album))
        self.assertEqual(len(result), 2)

    def testGetAlbumsByArtist(self):
        """testGetAlbumsByArtist - Ensures correct albums by an artist is
        returned"""
        result = self.musiclibrary.get_albums_by_artist('artist0')
        self.assertEqual(len(result), 2)
        for i in result:
            self.assertEqual(i.artist, 'artist0')

    def testGetAlbumsByUnknownArtist(self):
        """testGetAlbumsByUnknownArtist - Ensures proper handling of an
        artist not in the cache"""
        self.assertEquals(
            len(self.musiclibrary.get_albums_by_artist('foo')), 0)

    def testNumberOfTracks(self):
        """testNumberOfTracks - Ensures number of all tracks is returned"""
        result = self.musiclibrary.number_of_tracks()
        self.assertEqual(result, 8)

    def testNumberOfTracksByArtist(self):
        """testNumberOfTracksByArtist - Ensures number of all tracks by one
        artist is returned"""
        result = self.musiclibrary.number_of_tracks_by_artist('artist0')
        self.assertEqual(result, 8)

    def testNumberOfTracksByUnknownArtist(self):
        """testNumberOfTracksByUnknownArtist - Ensures proper handling when
        artist called is not in the cache"""
        self.assertEqual(
            self.musiclibrary.number_of_albums_by_artist('foo'), 0)

    def testNumberOfAlbumsByArtist(self):
        """testNumberOfAlbumsByArtist - Ensures number of all albums by one
        artist is returned"""
        result = self.musiclibrary.number_of_albums_by_artist('artist0')
        self.assertEqual(result, 2)

    def testNumberOfAlbumsByUnknownArtist(self):
        """testNumberOfAlbumsByUnknownArtist - Ensures proper handling when
        artist called is not in the cache"""
        self.assertEqual(
            self.musiclibrary.number_of_albums_by_artist('foo'), 0)

    def testSaveLyrics(self):
        """testSaveLyrics - Ensures lyrics for a track are saved in the
        database"""
        # Only need a filename that matches something in the database, the rest
        # of the track is for construction purposes only
        track = Track('/filename/000', '', 0, '', '', 0, 1, '', None)
        self.musiclibrary.save_lyrics(track, 'some lyrics here')
        self.assertEqual(track.lyrics, 'some lyrics here')


class TestAlbum(TestMusic):
    '''Tests Album'''

    def setUp(self):
        TestMusic.setUp(self)
        self.music_library = MusicLibrary()
        self.album = self.music_library._create_album('album1')

    def test_constructor(self):
        """Test that an Album object is properly constructed"""
        self.assertTrue(isinstance(self.album, Album))
        self.assertEqual(self.album.artist, 'artist0')
        self.assertEqual(self.album.length, 8)
        self.assertEqual(self.album.title, 'album1')
        self.assertEqual(self.album.year, 0)

    def test_constructor_not(self):
        """Test that an AlbumHasNoTracks exception is raised when the created
        album doesn't exist in the cache"""
        self.assertRaises(AlbumHasNoTracks, self.music_library._create_album,
            'foo')

    def test_has_album_art(self):
        """Test that album art exists for the file"""
        album_artist = "artist0 - album1"
        album_artist = album_artist.encode("base64")
        album_art = os.path.join(self.art_path, album_artist + ".jpg")
        open(album_art, "wb").close()
        self.assertTrue(self.album.has_album_art())
        if os.path.exists(album_art):
            os.remove(album_art)

    def test_has_album_art_not(self):
        """Test that missing album art is reported back"""
        other_album = self.music_library._create_album('album1')
        self.assertFalse(other_album.has_album_art())

    def test_album_art_url(self):
        """Test that the path to the album's art is returned"""
        result = self.album.album_art_url
        album_artist = "artist0 - album1"
        album_artist = album_artist.encode("base64")
        album_art = os.path.join(self.art_path, album_artist + ".jpg")
        self.assertEqual(result, album_art)

    def test_tracks(self):
        """Test that all tracks for an album are returned"""
        result = self.album.tracks
        self.assertEqual(len(result), 4)
        for i in result:
            self.assertTrue(isinstance(i, Track))


class TestCompactDisc(TestMusic):
    '''Tests CompactDisc'''

    def setUp(self):
        TestMusic.setUp(self)
        self.cd = CompactDisc([2299253003L, 11, 150, 25433, 46436, 68737, 89292,
            108536, 130667, 144099, 160174, 181568, 203695, 3027])

    def test_constructor(self):
        '''Test that a CompactDisc object is properly constructed.'''
        self.assertTrue(isinstance(self.cd, CompactDisc))
        self.assertEqual(self.cd.artist, 'U2')
        self.assertEqual(self.cd.length, 3027)
        self.assertEqual(self.cd.title, 'The Joshua Tree')

    def test_tracks(self):
        '''Test that track names are returned from CDDB.'''
        tracks = [track.title for track in self.cd.tracks]

        self.assertEqual(tracks, ['Where the Streets Have No Name',
            "I Still haven't Found What I'm Looking For", 'With or Without You',
            'Bullet the Blue Sky', 'Running To Stand Still',
            'Red Hill Mining Town', "In God's Country",
            'Trip Through Your Wires', 'One Tree Hill', 'Exit',
            'Mothers of the Disappeared'])

class TestCompactDiscTrack(TestMusic):
    '''Tests CompactDiscTrack'''

    def setUp(self):
        TestMusic.setUp(self)
        self.track = CompactDiscTrack(1, 'test', 120)

    def test_constructor(self):
        '''Test that a CompactDiscTrack object is properly constructed.'''
        self.assertTrue(isinstance(self.track, CompactDiscTrack))
        self.assertEqual(self.track.length, 120)
        self.assertEqual(self.track.title, 'test')

    def test_get_uri(self):
        '''Test that the URI is in the proper CD format.'''
        self.assertEqual(self.track.uri, 'cdda://1')

    def test_length_string_property(self):
        '''Test the length_string property.'''
        self.assertEqual(self.track.length_string, '2:00')

