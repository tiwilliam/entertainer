# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''VideoMetadataSearch - Search video file metadata from IMDB database'''
# pylint: disable-msg=C0301

import os
import imdb
import re
import urllib
import threading
from pysqlite2 import dbapi2 as sqlite

from entertainerlib.logger import Logger
from entertainerlib.configuration import Configuration

class VideoMetadataSearch(threading.Thread):
    """
    Search video file metadata from IMDB database. This class is a thread that
    connects to IMDb website and tries to find information for video file. This
    search finds movies and TV-Series.
    """

    # Title split keywords
    __TITLE_SPLIT_KEYWORDS = [
        "[", "]", "~", "(", ")", "dvdscr", "dvdrip", "dvd-rip", "dvdr", "vcd",
        "divx", "xvid", "ac3", "r5", "pal", "readnfo", "uncut", "cd1", "cd2",
        "dvdiso"
        ]

    # Title strip items
    __TITLE_STRIP_SEARCH = [".", "-", "_"]

    def __init__(self, filename):
        """
        Initialize metadata search thread.
        @param filename: Filename as string (find metadata for this file)
        """
        threading.Thread.__init__(self)
        self.setName("Video metadata search thread")
        self.logger = Logger().getLogger(
            'backend.components.mediacache.VideoMetadataSearch')
        self.config = Configuration()

        self.filename = filename
        self.title, self.season, self.episode = self._parse_filename(filename)
        try:
            self.IMDb = imdb.IMDb()
        except imdb.IMDbError:
            raise IOError("Couldn't connect to IMDB server!")

    def _parse_filename(self, filename):
        """
        Parse filename. Tries to get title of the movie/tv-series etc.

        TV-episode filenames should be format:
            Prison_Break_s02e10_something.something.avi
            Prison.Break - 02x10 - something_something.avi
            etc.

        Movies should be something like:
            movie_name_keyword_something.avi
            movie.name.avi
            etc.
        @param filename: Path of the movie
        @return: Title, season and episode
        """
        season = 0
        episode = 0

        # lowercase filename and remove the path and extension
        filename = filename.lower()
        filename = os.path.split(filename)[1]
        filename = os.path.splitext(filename)[0]

        # strip ., - and _ from filename
        for item in self.__TITLE_STRIP_SEARCH:
            filename = filename.replace(item, ' ')

        # split title at keywords
        for item in self.__TITLE_SPLIT_KEYWORDS:
            filename = filename.split('%s' % item)[0]
        filename = filename.strip()

        # try to get the title, season and episode from filename
        regexp = r'(?P<title>.*?)(s?)(?P<season>\d{1,2})(x|e|xe)(?P<episode>\d{1,2})'
        match = re.search(regexp, filename)
        if not match:
            regexp = r'(?P<title>.*?)season\s(?P<season>\d{1,2})\sepisode\s(?P<episode>\d{1,2})'
            match = re.search(regexp, filename)
        if match:
            filename = match.group('title')
            filename = filename.strip()
            season = match.group('season')
            episode = match.group('episode')

        return filename, int(season), int(episode)

    def run(self):
        """
        Search metadata from IMDB and update video cache database.
        """
        search_results = []
        search_results = self.IMDb.search_movie(self.title)

        if len(search_results) == 0:
            return # No matches for this search

        if search_results[0]['kind'] == "movie":
            # We trust that the first search result is the best
            movie = search_results[0]
            self.IMDb.update(movie)

            video_type = "MOVIE"
            title = movie['title']
            year = movie['year']
            # convert to 5-stars rating
            rating = round(float(movie['rating']) / 2)

            genres = ','.join(movie['genres'])
            plot_outline = movie['plot outline']

            plot_string = movie['plot'][0]
            plot = plot_string[plot_string.rfind("::")+2:].lstrip()

            # IMDb returns sometimes list and sometimes string
            if(type(plot)) is list:
                plot = plot[0]
            if(type(plot_outline)) is list:
                plot_outline = plot_outline[0]

            runtime = movie['runtime'][0]
            int(runtime) # Raises exception if not integer
            p = self._get_persons(movie)
            row = (video_type, title, "", runtime, genres, rating,
                   year, plot_outline, plot, 0, 0, p[0], p[1], p[2],
                   p[3], p[4], p[5], p[6], p[7], p[8], self.filename)
            self._update_video_cache(row)

            # Download and save cover art
            self._download_cover_art(movie['cover url'], title)

        elif search_results[0]['kind'] == "tv series":
            series = search_results[0]
            # We trust that the first search result is the best
            self.IMDb.update(series)
            self.IMDb.update(series, "episodes")

            video_type = "TV-SERIES"
            p = self._get_persons(series)
            rating = 0
            #round(float(series['rating']) / 2)
            # convert to 5-stars rating

            series_title = series['title']
            genres = ','.join(series['genres'])
            time = series['runtime']
            runtime = time[0][:time[0].find(":")]
            int(runtime) # This raises exception if runtime is not integer
            year = series['series years']
            title = series['episodes'][self.season][self.episode]['title']
            plot =  series['episodes'][self.season][self.episode]['plot']
            row = (video_type, title, series_title, runtime, genres, rating, \
                   year, "", plot, self.season, self.episode, p[0], p[1], \
                   p[2], p[3], p[4], p[5] ,p[6], p[7], p[8], self.filename)
            self._update_video_cache(row)

            # Download and save cover art
            self._download_cover_art(series['cover url'], series_title)
        else:
            # This file wasn't identified to be a movie or a TV-series episode.
            return

    def _update_video_cache(self, db_row):
        """
        Update data to video cache database
        @param db_row: List that contains all information we want to store into
                       cache
        """
        db_conn = sqlite.connect(self.config.VIDEO_DB)
        db_cursor = db_conn.cursor()
        db_cursor.execute("""UPDATE metadata
                             SET type=?,
                                 title=?,
                                 series_title=?,
                                 runtime=?,
                                 genres=?,
                                 rating=?,
                                 year=?,
                                 plot_outline=?,
                                 plot=?,
                                 season=?,
                                 episode=?,
                                 actor_1=?,
                                 actor_2=?,
                                 actor_3=?,
                                 actor_4=?,
                                 actor_5=?,
                                 writer_1=?,
                                 writer_2=?,
                                 director_1=?,
                                 director_2=?
                             WHERE filename=?""", db_row)
        db_conn.commit()
        db_conn.close()


    def _get_persons(self, movie):
        """
        Get a list of persons. First five names are actors, then comes two
        directors and two writers.
        @param movie: Movie name
        @return: List of strings containing actors, directors and writers
        """
        a1 = movie['actors'][0]['name']
        a2 = movie['actors'][1]['name']
        a3 = movie['actors'][2]['name']
        a4 = movie['actors'][3]['name']
        a5 = movie['actors'][4]['name']
        w1 = movie['writer'][0]['name']
        w2 = movie['writer'][1]['name']
        d1 = movie['director'][0]['name']
        d2 = movie['director'][1]['name']

        return [a1, a2, a3, a4, a5, w1, w2, d1, d2]

    def _download_cover_art(self, url, title):
        """
        Download cover art from given URL and save it to cache
        @param url: URL to the image file
        @param title: Title of the series or movie
        """
        # Check if we have cover art for this series or movie already
        if not os.path.exists(
            os.path.join(self.config.MOVIE_ART_DIR, title + ".jpg")):
            image = urllib.urlopen(url)
            dest = open(os.path.join(
                self.config.MOVIE_ART_DIR, title + ".jpg"), 'w')
            dest.write(image.read())
            dest.close()

