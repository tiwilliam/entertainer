# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Contains database connection wrappers'''

import os

from storm.locals import create_database, Store

SCHEMA = {
    'NewsFeed': '''CREATE TABLE `newsfeed` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    title TEXT,
                    description TEXT);''',
    'NewsEntry': '''CREATE TABLE `newsentry` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    title TEXT,
                    description TEXT,
                    creation_date DATETIME,
                    is_read BOOLEAN,
                    feed_id INTEGER);''',
    'PhotoAlbum': '''CREATE TABLE `photoalbum` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    creation_date INTEGER);''',
    'PhotoImage': '''CREATE TABLE `photoimage` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    thumbnail VARCHAR(32),
                    title TEXT,
                    description TEXT,
                    creation_date DATETIME,
                    album_id INTEGER);''',
    'MusicAlbum': '''CREATE TABLE `musicalbum` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artist TEXT,
                    title TEXT,
                    year INTEGER,
                    genre TEXT);''',
    'MusicTrack': '''CREATE TABLE `musictrack` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    title TEXT,
                    tracknumber INTEGER,
                    rating INTEGER,
                    length INTEGER,
                    bitrate INTEGER,
                    comment TEXT,
                    lyrics TEXT,
                    album_id INTEGER);''',
    'MusicPlaylist': '''CREATE TABLE `musicplaylist` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT);''',
    'MusicPlaylistTrack': '''CREATE TABLE `musicplaylisttrack` (
                    track_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER);''',
    'VideoFile': '''CREATE TABLE `videofile` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    thumb VARCHAR(32),
                    type TEXT);''',
    'VideoSeries': '''CREATE TABLE `videoseries` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    actor_1 TEXT,
                    actor_2 TEXT,
                    actor_3 TEXT,
                    actor_4 TEXT,
                    actor_5 TEXT,
                    writer_1 TEXT,
                    writer_2 TEXT,
                    director_1 TEXT,
                    director_2 TEXT);''',
    'VideoMeta': '''CREATE TABLE `videometa` (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    season INTEGER,
                    episode INTEGER,
                    runtime INTEGER,
                    genres TEXT,
                    year INTEGER,
                    plot TEXT,
                    file_id INTEGER,
                    series_id INTEGER);''',
}

class DatabaseConnectionException(Exception):
    '''Exception for handling various database connection issues'''


class Database(object):
    '''Database connection object handler

    Wraps a sqlite connection and a storm Store
    '''

    def __init__(self, filename, debug=False):
        if debug:
            import sys
            from storm.tracer import debug
            debug(True, stream=sys.stdout)

        self._filename = filename

        create = False
        if not os.path.exists(self._filename):
            create = True

        self._db = create_database('sqlite:%s' % self._filename)

        if create:
            self._create()

    def _create(self):
        '''Create a new entertainer database

        Reads the current database schema dictionary, and creates the sqlite
        database based on that schema
        '''

        store = Store(self._db)
        store.execute("""
        CREATE TABLE `entertainer_data` (
            name VARCHAR PRIMARY KEY,
            value VARCHAR);""")
        store.execute(
        "INSERT INTO `entertainer_data` VALUES ('version', '0.2a');")

        for query in SCHEMA.itervalues():
            store.execute(query, noresult=True)
            store.commit()

    def connect(self, *args, **kwargs):
        '''Wrapper around Database.connect'''
        return self._db.connect(*args, **kwargs)

