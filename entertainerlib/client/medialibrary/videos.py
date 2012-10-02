# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Video Library - Interface for Entertainer video library cache'''

import os

from pysqlite2 import dbapi2 as sqlite

from entertainerlib.client.medialibrary.playable import Playable
from entertainerlib.configuration import Configuration

class VideoLibrary(object):
    '''Interface for Entertainer's video cache.'''

    def __init__(self):
        self.config = Configuration()

        if not os.path.exists(self.config.VIDEO_DB):
            raise Exception("Video database doesn't exist!")

        self.connection = sqlite.connect(self.config.VIDEO_DB)
        self.cursor = self.connection.cursor()

    def __del__(self):
        '''Close the db connection when this object is deleted.'''
        self.connection.close()

    def get_movies(self):
        '''Get all the movies.'''
        self.cursor.execute("""SELECT videofile.filename
                          FROM   videofile, metadata
                          WHERE  type='MOVIE'
                          AND    videofile.filename=metadata.filename
                          ORDER BY title""")
        movies = []
        for row in self.cursor.fetchall():
            movies.append(self._create_movie(row[0]))
        return movies

    def _create_movie(self, filename):
        '''Factory method to create a movie.'''
        self.cursor.execute(
            """SELECT metadata.filename, hash, length, resolution,
                                 title, runtime, genres, rating, year,
                                 plot_outline, plot, actor_1, actor_2,
                                 actor_3, actor_4, actor_5, writer_1,
                                 writer_2, director_1, director_2
                          FROM   videofile, metadata
                          WHERE  metadata.filename=:fn
                          AND    videofile.filename=metadata.filename
                          ORDER BY title""", { "fn" : filename })
        result = self.cursor.fetchall()
        db_movie = result[0]

        movie = Movie()
        movie.filename = db_movie[0]
        movie.art_hash = db_movie[1]
        movie.title = db_movie[4]
        movie.runtime = db_movie[5]
        movie.genres = db_movie[6].split(',')
        movie.plot = db_movie[10]
        movie.rating = db_movie[7]
        movie.short_plot = db_movie[9]
        movie.year = db_movie[8]

        for i in range(11, 16):
            if len(db_movie[i]) > 0:
                movie.actors.append(db_movie[i])

        for i in [16, 17]:
            if len(db_movie[i]) > 0:
                movie.writers.append(db_movie[i])

        for i in [18, 19]:
            if len(db_movie[i]) > 0:
                movie.directors.append(db_movie[i])

        return movie

    def get_tv_series(self):
        '''Get all the TV series.'''
        self.cursor.execute("""SELECT DISTINCT series_title
                          FROM   metadata
                          WHERE  type='TV-SERIES'
                          ORDER BY title""")
        series = []
        for row in self.cursor.fetchall():
            series.append(self._create_tv_series(row[0]))
        return series

    def _create_tv_series(self, title):
        '''Factory method to create a TV series.'''
        tv_series = TVSeries(title)

        self.cursor.execute(
            "SELECT DISTINCT season FROM metadata WHERE series_title=:title",
            { "title" : title })
        for row in self.cursor.fetchall():
            tv_series.seasons.append(row[0])

        self.cursor.execute(
            "SELECT COUNT(filename) FROM metadata WHERE series_title=:title",
            { "title" : title })
        result = self.cursor.fetchall()
        tv_series.number_of_episodes = result[0][0]

        return tv_series

    def get_video_clips(self):
        '''Get all the video clips.'''
        self.cursor.execute("""SELECT filename
                          FROM   metadata
                          WHERE  type='CLIP'
                          ORDER BY title""")
        clips = []
        for row in self.cursor.fetchall():
            clips.append(self._create_video_clip(row[0]))
        return clips

    def _create_video_clip(self, filename):
        '''Factory method to create a video clip.'''
        self.cursor.execute(
            """SELECT videofile.filename, hash, title
                          FROM   videofile, metadata
                          WHERE  videofile.filename=:fn
                          AND    videofile.filename=metadata.filename
                          ORDER BY title""", { "fn" : filename })
        result = self.cursor.fetchall()

        video_item = VideoItem()
        video_item.filename = result[0][0]
        video_item.art_hash = result[0][1]
        video_item.title = result[0][2]
        return video_item

    def get_number_of_movies(self):
        '''Get the number of movies.'''
        self.cursor.execute(
            """SELECT COUNT(filename) FROM metadata WHERE type='MOVIE'""")
        result = self.cursor.fetchall()
        return result[0][0]

    def get_number_of_tv_series(self):
        '''Get the number of TV series.'''
        self.cursor.execute("""SELECT DISTINCT COUNT(series_title)
                          FROM   metadata
                          WHERE  type='TV-SERIES'""")
        result = self.cursor.fetchall()
        return result[0][0]

    def get_number_of_video_clips(self):
        '''Get the number of video clips.'''
        self.cursor.execute(
            """SELECT COUNT(filename) FROM metadata WHERE type='CLIP'""")
        result = self.cursor.fetchall()
        return result[0][0]

    def get_episodes_from_season(self, series_title, season_number):
        '''Get TV episodes from the series' season.'''
        self.cursor.execute("""SELECT filename
                          FROM   metadata
                          WHERE  series_title=:title
                          AND    season=:season
                          ORDER BY episode""",
                          { "title" : series_title, "season" : season_number })
        episodes = []
        for row in self.cursor.fetchall():
            episodes.append(self._create_tv_episode(row[0]))
        return episodes

    def _create_tv_episode(self, filename):
        '''Factory method to create a TV episode.'''
        self.cursor.execute(
            """SELECT videofile.filename, hash, title, plot, episode
                          FROM   videofile, metadata
                          WHERE  videofile.filename=:fn
                          AND    videofile.filename=metadata.filename
                          ORDER BY title""", { "fn" : filename })
        result = self.cursor.fetchall()
        db_episode = result[0]

        tv_episode = TVEpisode()
        tv_episode.filename = db_episode[0]
        tv_episode.art_hash = db_episode[1]
        tv_episode.title = db_episode[2]
        tv_episode.plot = db_episode[3]
        tv_episode.number = db_episode[4]

        return tv_episode


class VideoItem(Playable):
    '''Representation of a playable video item.'''

    def __init__(self):
        # XXX: laymansterms - VideoItem should really have a few mandatory
        # parameters. title, filename, maybe more.
        Playable.__init__(self)
        self.config = Configuration()

        self._title = ""
        self.filename = ""
        self.art_hash = ""

    def _get_title(self):
        '''Get the title.'''
        if (self._title == "") or (self._title == None):
            return self.filename
        else:
            return self._title

    def _set_title(self, title):
        '''Set the title.'''
        self._title = title

    title = property(_get_title, _set_title)

    def has_thumbnail(self):
        '''Test if there is a thumbnail.'''
        thumb_path = os.path.join(self.config.VIDEO_THUMB_DIR,
            self.art_hash + ".jpg")
        return os.path.exists(thumb_path)

    @property
    def thumbnail_url(self):
        '''Get the path to the thumbnail or a default.'''
        thumb = os.path.join(self.config.VIDEO_THUMB_DIR,
            self.art_hash + ".jpg")
        if os.path.exists(thumb):
            return thumb
        else:
            return os.path.join(self.config.theme_path,
                "images/default_movie_art.png")

    # Implement playable interface
    def get_title(self):
        '''Get the title.'''
        return self.title

    def get_type(self):
        '''Get the type.'''
        return Playable.VIDEO_STREAM

    def get_uri(self):
        '''Get the URI.'''
        return "file://" + self.filename


class VideoFilm(VideoItem):
    '''Generic representation of a film.'''

    def __init__(self):
        VideoItem.__init__(self)
        self.actors = []
        self.directors = []
        self.genres = []
        self.plot = ''
        self.runtime = ''
        self.short_plot = ''
        self.writers = []
        self.rating = 0
        self.year = 2000


class Movie(VideoFilm):
    '''Representation of a movie.'''

    def has_cover_art(self):
        '''Test if there is cover art in the cache.'''
        art_path =  os.path.join(self.config.MOVIE_ART_DIR, self.title + ".jpg")
        return os.path.exists(art_path)

    @property
    def cover_art_url(self):
        '''Get the URL to the cover art.'''
        return os.path.join(self.config.MOVIE_ART_DIR, self.title + ".jpg")


class TVSeries(object):
    '''TV Series contains TVEpisodes organized by seasons.'''

    def __init__(self, title):
        self.config = Configuration()

        self.number_of_episodes = 0
        # Season list of numbers. For example [1,2,3,5] in case that user
        # doesn't have episodes from season 4.
        self.seasons = []
        self.title = title

    def has_cover_art(self):
        '''Test if there is cover art in the cache.'''
        art_path =  os.path.join(self.config.MOVIE_ART_DIR, self.title + ".jpg")
        return os.path.exists(art_path)

    @property
    def cover_art_url(self):
        '''Get the URL to the cover art.'''
        return os.path.join(self.config.MOVIE_ART_DIR, self.title + ".jpg")


class TVEpisode(VideoFilm):
    '''Representation of a TV show episode.'''

    def __init__(self):
        VideoFilm.__init__(self)
        self.number = 0

