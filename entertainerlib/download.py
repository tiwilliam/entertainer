# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Downloader classes.'''

import locale
import os
import re
import socket
import threading
import urllib
from xml.dom import minidom

import gobject

# Amazon licence for Entertainer
LICENSE_KEY = "1YCWYZ0SPPAJ27YZZ482"
DEFAULT_LOCALE = "en_US"
ASSOCIATE = "webservices-20"

# We are not allowed to batch more than 2 requests at once
# http://docs.amazonwebservices.com/AWSEcommerceService/4-0/
# PgCombiningOperations.html
MAX_BATCH_JOBS = 2


class AlbumArtDownloader(threading.Thread):
    """
    Search and download album art from the internet.

    This class is heavily based on Rhythmbox - AlbumArt plugin's class
    'AmazonCoverArtSearch'. That plugin is released under GPLv2 (or higher)
    and it's copyrights belong to Gareth Murphy and Martin Szulecki.

    See more: http://www.gnome.org/projects/rhythmbox/

    If you want better cover search, please contribute to Rhyhtmbox project.
    """

    def __init__(self, album, artist, art_file_path, callback = None):
        """
        Initialize album art downloader
        @param album: Album title
        @param artist: Artist name
        @param art_file_path: Path where albumart is saved
        @param callback: Callback function that is called after search if set
        """
        threading.Thread.__init__(self)
        self.setName("AlbumArt Downloader")
        self.callback_function = callback        # Callback function
        self.album = album                       # Album title
        self.artist = artist                     # Artist name
        # Album art files are in this directory
        self.path = art_file_path
        (self.tld, self.encoding) = self.__get_locale ()

    def run(self):
        """Start searching and downloading albumart."""
        self.search()

    def __get_locale (self):
        '''Get locale information from user\'s machine'''
        # "JP is the only locale that correctly takes UTF8 input.
        # All other locales use LATIN1."
        # http://developer.amazonwebservices.com/connect/
        # entry.jspa?externalID=1295&categoryID=117
        supported_locales = {
            "en_US" : ("com", "latin1"),
            "en_GB" : ("co.uk", "latin1"),
            "de" : ("de", "latin1"),
            "ja" : ("jp", "utf8")
        }

        lc_id = DEFAULT_LOCALE
        default = locale.getdefaultlocale ()[0]
        if default:
            if supported_locales.has_key (default):
                lc_id = default
            else:
                lang = default.split("_")[0]
                if supported_locales.has_key (lang):
                    lc_id = lang

        return supported_locales[lc_id]

    def __valid_match (self, item):
        '''Determine if item matches tag criteria'''
        return (hasattr (item, "LargeImage") or hasattr (item, "MediumImage")) \
               and hasattr (item, "ItemAttributes")

    def __tidy_up_string (self, str_input):
        """
        Tidy up string. Remove spaces, convert to lowercase and replace chars.
        """
        # Lowercase
        str_input = str_input.lower ()
        # Strip
        str_input = str_input.strip ()

        # XXX: Convert accented to unaccented
        str_input = str_input.replace (" - ", " ")
        str_input = str_input.replace (": ", " ")
        str_input = str_input.replace (" & ", " and ")

        return str_input

    def search(self):
        """Search album art from Amazon"""
        self.searching = True
        self.cancel = False
        self.keywords = []

        st_artist = self.artist or u'Unknown'
        st_album = self.album or u'Unknown'

        if st_artist == st_album == u'Unknown':
            self.on_search_completed (None)
            return

        # Tidy up

        # Replace quote characters
        # don't replace single quote: could be important punctuation
        for char in ["\""]:
            st_artist = st_artist.replace (char, '')
            st_album = st_album.replace (char, '')


        self.st_album = st_album
        self.st_artist = st_artist

        # Remove variants of Disc/CD [1-9] from album title before search
        for exp in ["\([Dd]isc *[1-9]+\)", "\([Cc][Dd] *[1-9]+\)"]:
            p = re.compile (exp)
            st_album = p.sub ('', st_album)

        st_album_no_vol = st_album
        for exp in ["\(*[Vv]ol.*[1-9]+\)*"]:
            p = re.compile (exp)
            st_album_no_vol = p.sub ('', st_album_no_vol)

        self.st_album_no_vol = st_album_no_vol

        # Save current search's entry properties
        self.search_album = st_album
        self.search_artist = st_artist
        self.search_album_no_vol = st_album_no_vol

        # XXX: Improve to decrease wrong cover downloads, maybe add severity?
        # Assemble list of search keywords (and thus search queries)
        if st_album == u'Unknown':
            self.keywords.append ("%s Best of" % (st_artist))
            self.keywords.append ("%s Greatest Hits" % (st_artist))
            self.keywords.append ("%s Essential" % (st_artist))
            self.keywords.append ("%s Collection" % (st_artist))
            self.keywords.append ("%s" % (st_artist))
        elif st_artist == u'Unknown':
            self.keywords.append ("%s" % (st_album))
            if st_album_no_vol != st_artist:
                self.keywords.append ("%s" % (st_album_no_vol))
            self.keywords.append ("Various %s" % (st_album))
        else:
            if st_album != st_artist:
                self.keywords.append ("%s %s" % (st_artist, st_album))
                if st_album_no_vol != st_album:
                    self.keywords.append ("%s %s" %
                        (st_artist, st_album_no_vol))
                self.keywords.append ("Various %s" % (st_album))
            self.keywords.append ("%s" % (st_artist))

        # Initiate asynchronous search
        self.search_next ()

    def search_next(self):
        """Search again, because the last one didn't find any covers."""
        if len (self.keywords) == 0:
            # No keywords left to search -> no results
            self.on_search_completed (None)
            return False

        self.searching = True

        url = "http://ecs.amazonaws." + self.tld + "/onca/xml" \
              "?Service=AWSECommerceService"                   \
              "&AWSAccessKeyId=" + LICENSE_KEY +               \
              "&AssociateTag=" + ASSOCIATE +                   \
              "&ResponseGroup=Images,ItemAttributes"           \
              "&Operation=ItemSearch"                          \
              "&ItemSearch.Shared.SearchIndex=Music"

        job = 1
        while job <= MAX_BATCH_JOBS and len (self.keywords) > 0:
            keyword = self.keywords.pop (0)
            keyword = keyword.encode (self.encoding, "ignore")
            keyword = keyword.strip ()
            keyword = urllib.quote (keyword)
            url += "&ItemSearch.%d.Keywords=%s" % (job, keyword)
            job += 1

        # Retrieve search for keyword
        temp = urllib.urlopen(url)
        search_results = temp.read()
        self.on_search_response(search_results)
        return True

    def __unmarshal(self, element):
        rc = object()
        child_elements = [e for e in element.childNodes if isinstance (e,
            minidom.Element)]
        if child_elements:
            for child in child_elements:
                key = child.tagName
                if hasattr (rc, key):
                    if not isinstance (getattr (rc, key), list):
                        setattr (rc, key, [getattr (rc, key)])
                    getattr (rc, key).append (self.__unmarshal (child))
                # get_best_match_urls() wants a list, even if there is only
                # one item/artist
                elif child.tagName in ("Items", "Item", "Artist"):
                    setattr (rc, key, [self.__unmarshal(child)])
                else:
                    setattr (rc, key, self.__unmarshal(child))
        else:
            rc = "".join ([e.data for e in element.childNodes if isinstance (e,
                minidom.Text)])
        return rc

    def on_search_response (self, result_data):
        '''Check search results

        If results are not good, we search again with the next keyword.
        '''
        if result_data is None:
            self.search_next()
            return

        try:
            xmldoc = minidom.parseString(result_data)
        except (TypeError, AttributeError):
            self.search_next()
            return

        data = self.__unmarshal (xmldoc)
        if not hasattr (data, "ItemSearchResponse") or \
           not hasattr (data.ItemSearchResponse, "Items"):
            # Something went wrong ...
            self.search_next ()
        else:
            # We got some search results
            self.on_search_results (data.ItemSearchResponse.Items)

    def on_search_results (self, results):
        '''Results were found, now we need to take action.'''
        self.on_search_completed (results)

    def on_search_completed (self, result):
        """
        Search completed and results found.

        Download large album art image from the first result and save it to
        the disk. This function diverges greatly from the rhythmbox
        implementation in order to avoid their loader and CoverArtDatabase
        """
        self.searching = False
        image_urls = self.get_best_match_urls(result)
        if len(image_urls) == 0:
            return
        image_url = image_urls[0]
        image_file = urllib.urlopen(image_url)
        # base64 encode artist and album so there can be a '/' in the artist
        # or album
        artist_album = self.artist + " - " + self.album
        artist_album = artist_album.encode("base64")

        dest = open(os.path.join(self.path, artist_album + ".jpg"),'w')
        dest.write(image_file.read())
        dest.close()

        if self.callback_function is not None:
            self.callback_function(self.artist, self.album)

    def get_best_match_urls (self, search_results):
        """Return tuple of URL's to large and medium cover of the best match"""
        # Default to "no match", our results must match our criteria

        # This code comes from Rhythmbox so we can't control the use of 'filter'
        # pylint: disable-msg=W0141

        if not search_results:
            return []

        best_match = None

        for result in search_results:
            if not hasattr (result, "Item"):
                # Search was unsuccessful, try next batch job
                continue

            items = filter(self.__valid_match, result.Item)
            if self.search_album != u'Unknown':
                album_check = self.__tidy_up_string (self.search_album)
                for item in items:
                    if not hasattr (item.ItemAttributes, "Title"):
                        continue

                    album = self.__tidy_up_string (item.ItemAttributes.Title)
                    if album == album_check:
                        # Found exact album, can not get better than that
                        best_match = item
                        break
                    # If we already found a best_match, just keep checking for
                    # exact one. Check the results for both an album name that
                    # contains the name we're searching for, and an album name
                    # that's a substring of the name we're searching for
                    elif (best_match is None) and \
                         (album.find (album_check) != -1 or
                          album_check.find (album) != -1):
                        best_match = item

            # If we still have no definite hit, use first result where artist
            # matches
            if (self.search_album == u'Unknown' and \
                self.search_artist != u'Unknown'):
                artist_check = self.__tidy_up_string (self.search_artist)
                if best_match is None:
                    # Check if artist appears in the Artists list
                    hit = False
                    for item in items:
                        if not hasattr (item.ItemAttributes, "Artist"):
                            continue

                        for artist in item.ItemAttributes.Artist:
                            artist = self.__tidy_up_string (artist)
                            if artist.find (artist_check) != -1:
                                best_match = item
                                hit = True
                                break
                        if hit:
                            break

            urls = [getattr (best_match, size).URL for size in ("LargeImage",
                "MediumImage")
                    if hasattr (best_match, size)]
            if urls:
                return urls

        # No search was successful
        return []


class LyricsDownloader(object):
    """
    Search and download song lyrics from the internet.
    Update music cache if lyrics found.
    """

    # The permanent user ID from Lyricsfly
    # NOTICE: This is the personal user ID for Entertainer, if you want to
    # experiment with the API from lyricsfly you can get an ID here =>
    # http://lyricsfly.com/api/, don't use this one as abuse of our key may
    # invalidate it.
    _LYRICSFLY_KEY = 'YzIxOTM4M2NkNGQ4MmRmODEtZW50ZXJ0YWluZXItcHJvamVjdC5jb20='

    def __init__(self, title, artist, callback):
        """
        Initialize lyrics downloader.
        @param title: Title of the track
        @param artist: Artist of the track
        @param callback: Callback function which is called when search is over.
                   lyrics are given as a parameter to this callback function.
        """
        self.title = title.lower()
        self.artist = artist.lower()
        self.callback = callback

    def search(self):
        """
        Search lyrics and download if found. Search is done asynchronously.
        This method returns immediately and set callback is called when search
        is over.
        """
        gobject.timeout_add(2000, self._async_search)

    def _async_search(self):
        """
        Search lyrics and download if found
        """
        lyrics = ""
        self._clean_up_artist_title()
        lyrics_xml = self._get_lyrics_xml()
        if lyrics_xml is not None:
            lyrics = self._parse_lyrics_xml(lyrics_xml)
        self.callback(lyrics)

    def _clean_up_artist_title(self):
        """
        Clean up the artist and title.
        """
        # Clean spaces
        self.title = self.title.strip()
        self.artist = self.artist.strip()

        # Convert title and artist to use in url, special symbols have to be
        # replaced by a '%' not '%xx'
        # XXX: Find out what the special symbols are (', &, ...)
        # not letters, digits, spaces and ()$^*=:;|#@}{][!,.-_\
        self.artist = urllib.quote(self.artist.encode('utf-8'),
                                   "'&()$^*=:;|#@}{][!,\\")
        self.title = urllib.quote(self.title.encode('utf-8'),
                                   "'&()$^*=:;|#@}{][!,\\")

        self.artist = self.artist.replace("'", "%").replace("&", "%")
        self.title = self.title.replace("'", "%").replace("&", "%")

    def _get_lyrics_xml(self):
        """
        Download the lyrics XML-file.
        """
        lyrics_xml = None

        # timeout in seconds
        timeout = 5
        socket.setdefaulttimeout(timeout)

        url = "http://lyricsfly.com/api/api.php?i=%s&a=%s&t=%s" \
            % (self._LYRICSFLY_KEY.decode('base64'), self.artist, self.title)
        try:
            temp = urllib.urlopen(url)
            lyrics_xml = temp.read()
        except IOError:
            return None

        return lyrics_xml

    def _parse_lyrics_xml(self, lyrics_xml):
        """Parse lyrics XML and return lyrics string"""
        xmldoc = minidom.parseString(lyrics_xml).documentElement

        # Get the lyric from the XML file
        try:
            lyrics = xmldoc.getElementsByTagName('tx')[0].firstChild.nodeValue
        except IndexError:
            return ''

        # Clean spaces and enters
        lyrics = lyrics.strip().replace('\n', '')
        lyrics = lyrics.replace('[br]', '\n')

        # Add the artist and title to the top of the lyric
        lyrics = xmldoc.getElementsByTagName('ar')[0].firstChild.nodeValue + \
        ' - ' + xmldoc.getElementsByTagName('tt')[0].firstChild.nodeValue + \
        '\n\n' + lyrics

        xmldoc.unlink()

        return lyrics

