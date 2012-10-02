# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests LyricsDownloader'''
# pylint: disable-msg=W0212

import os
import urllib

from entertainerlib.download import LyricsDownloader
from entertainerlib.tests import EntertainerTest

THIS_DIR = os.path.dirname(__file__)


class testLyricsDownloader(EntertainerTest):

    def testLyricsConstructor(self):
        '''testMetadataConstructor - Ensures instantiation of Lyric Downloader
        class'''
        callback = False
        lyrics = LyricsDownloader('Foo', 'Bar', callback)
        self.assertTrue(isinstance(lyrics, LyricsDownloader))

    def testCleanUpArtistTitle(self):
        '''testCleanUpArtistTitle - Ensures the artist is converted for use in
        the url'''
        callback = False
        lyrics = LyricsDownloader('Foo', "Test 123 ()$^*=:;|#@}{][!,.-_\\&'" ,
            callback)
        lyrics._clean_up_artist_title()
        self.assertEqual(lyrics.artist,
            'test%20123%20()$^*=:;|#@}{][!,.-_\\%%')

    def testGetLyricsXML(self):
        '''testGetLyricsXML - Ensures the lyrics are fetched correctly'''
        lyrics = LyricsDownloader('On A Plain', 'Nirvana', False)
        lyrics._clean_up_artist_title()
        test_xml = urllib.urlopen(THIS_DIR +
            '/data/LyricsDownloader/lyrics_xml').read()
        self.assertEqual(lyrics._get_lyrics_xml(), test_xml)

    def testParseLyricsXML(self):
        '''testParseLyricsXML - Ensures the lyrics are parsed correctly'''
        callback = False
        lyrics = LyricsDownloader('On A Plain', 'Nirvana', callback)
        test_xml = urllib.urlopen(THIS_DIR +
            '/data/LyricsDownloader/lyrics_xml').read()
        final_lyrics = lyrics._parse_lyrics_xml(test_xml)
        temp = open(THIS_DIR + '/data/LyricsDownloader/final_lyrics')
        final_lyrics_from_file = temp.read()
        self.assertEqual(final_lyrics, final_lyrics_from_file)

