'''File handlers for the indexer.'''
from storm.locals import Store

from entertainerlib.configuration import Configuration
from entertainerlib.db import models
from entertainerlib.indexing.utilities import TagGetter
from entertainerlib.thumbnailer import ImageThumbnailer, VideoThumbnailer

__meta__ = type


class FileHandler:
    '''Abstract class for all file handlers.'''

    def __init__(self):
        self.configuration = Configuration()
        self._store = Store(self.configuration.MEDIA_DB)

    def __call__(self, filename):
        raise NotImplementedError


class AviHandler(FileHandler):
    '''Handler for avi files.'''

    def __call__(self, filename):
        if self._store.find(models.VideoFile,
            models.VideoFile.filename == filename).one():
            return self._update_file(filename)
        else:
            return self._add_file(filename)

    def _add_file(self, filename):
        '''Add a video.'''
        video_file = models.VideoFile()
        video_file.filename = unicode(filename)
        thumbnailer = VideoThumbnailer(filename)
        thumbnailer.create_thumbnail()
        video_file.thumbnail = thumbnailer.filename

        self._store.add(video_file)
        self._store.commit()

        return video_file

    def _update_file(self, filename):
        '''Update on existing video.'''
        # TODO: There's no metadata currently, so just return the existing
        # object.
        return self._store.find(models.VideoFile,
            models.VideoFile.filename == filename).one()


class JpegHandler(FileHandler):
    '''Handler for jpg/jpeg files.'''

    def __call__(self, filename):
        if self._store.find(models.PhotoImage,
            models.PhotoImage.filename == filename).one():
            return self._update_file(filename)
        else:
            return self._add_file(filename)

    def _add_file(self, filename):
        '''Add an image to the store.'''
        photo_file = models.PhotoImage()
        photo_file.filename = unicode(filename)

        thumbnailer = ImageThumbnailer(filename)
        thumbnailer.create_thumbnail()
        photo_file.thumbnail = unicode(thumbnailer.filename)

        self._store.add(photo_file)
        self._store.commit()

        return photo_file

    def _update_file(self, filename):
        '''Update an existing image in the store.'''
        # TODO: There's no metadata currently, so just return the existing
        # object.
        return self._store.find(models.PhotoImage,
            models.PhotoImage.filename == filename).one()


class Mp3Handler(FileHandler):
    '''Handler for mp3 files.'''

    def __call__(self, filename):
        if self._store.find(models.MusicTrack,
            models.MusicTrack.filename == filename).one():
            return self._update_file(filename)
        else:
            return self._add_file(filename)

    def _add_file(self, filename):
        '''Add a file to the store.'''
        music_file = models.MusicTrack()
        album = models.MusicAlbum()

        music_file.filename = filename

        tags = TagGetter(filename)

        music_file.comment = tags.comment
        music_file.lyrics = u''
        music_file.title = tags.title
        music_file.tracknumber = tags.track_number
        album.artist = tags.artist
        album.title = tags.album
        album.genre = tags.genre
        music_file.album = album

        self._store.add(album)
        self._store.add(music_file)
        self._store.commit()

        # TODO: get album art
        return music_file

    def _update_file(self, filename):
        '''Update a file already in the store.'''
        music_file = self._store.find(models.MusicTrack,
            models.MusicTrack.filename == filename).one()
        album = music_file.album

        tags = TagGetter(filename)

        music_file.comment = tags.comment
        music_file.lyrics = u''
        music_file.title = tags.title
        music_file.tracknumber = tags.track_number
        album.artist = tags.artist
        album.title = tags.album
        album.genre = tags.genre
        music_file.album = album

        self._store.add(album)
        self._store.add(music_file)
        self._store.commit()

        # TODO: get album art
        return music_file

