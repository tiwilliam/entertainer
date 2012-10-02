# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Contains all storm ORM models'''
# pylint: disable-msg=W0621,W0223

from storm.base import Storm
from storm.properties import DateTime, Int, Unicode
from storm.references import Reference, ReferenceSet


class BaseModel(Storm):
    '''Abstract class from which all Entertainer models inherit.'''

    def to_dict(self, recurse=True):
        '''Convert model into a static dict.'''
        raise NotImplementedError


class PhotoAlbum(BaseModel):
    '''A photo group'''

    __storm_table__ = 'photoalbum'
    id = Int(primary=True)
    title = Unicode()
    description = Unicode()
    creation_date = DateTime()
    images = ReferenceSet('PhotoAlbum.id', 'PhotoImage.album_id')

    def to_dict(self, recurse=True):
        '''See BaseModel.to_dict.'''
        ret = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'creation_date': self.creation_date,
            }
        if recurse:
            ret['images'] = [image.to_dict(recurse=False)
                for image in self.images]
        return ret


class PhotoImage(BaseModel):
    '''Image file references and metadata'''

    __storm_table__ = 'photoimage'
    id = Int(primary=True)
    filename = Unicode()
    thumbnail = Unicode()
    title = Unicode()
    description = Unicode()
    creation_date = DateTime()
    album_id = Int()
    album = Reference(album_id, 'PhotoAlbum.id')

    def to_dict(self, recurse=True):
        '''See BaseModel.to_dict'''
        ret = {
            'id': self.id,
            'filename': self.filename,
            'thumbnail': self.thumbnail,
            'title': self.title,
            'description': self.description,
            'creation_date': self.creation_date,
            }
        if recurse:
            ret['album_id'] = self.album_id
            ret['album'] = self.album.to_dict(recurse=False)
        return ret


class MusicAlbum(BaseModel):
    '''A music file container

    Music can be categorized many ways.  Albums are found in the music file's
    ID3 tags
    '''

    __storm_table__ = 'musicalbum'
    id = Int(primary=True)
    artist = Unicode()
    title = Unicode()
    year = Int()
    genre = Unicode()
    tracks = ReferenceSet('MusicAlbum.id', 'MusicTrack.album_id')

    def to_dict(self, recurse=True):
        '''See BaseModel.to_dict.'''
        ret = {
            'id': self.id,
            'artist': self.artist,
            'title': self.title,
            'year': self.year,
            'genre': self.genre,
            }
        if recurse:
            ret['tracks'] = [track.to_dict(recurse=False)
                for track in self.tracks]
        return ret


class MusicTrack(BaseModel):
    '''Music file references and metadata'''

    __storm_table__ = 'musictrack'
    id = Int(primary=True)
    filename = Unicode()
    title = Unicode()
    tracknumber = Int()
    rating = Int()
    length = Int()
    bitrate = Int()
    comment = Unicode()
    lyrics = Unicode()
    album_id = Int()
    album = Reference(album_id, 'MusicAlbum.id')

    def to_dict(self, recurse=True):
        '''See BaseModel.to_dict.'''
        ret = {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'tracknumber': self.tracknumber,
            'rating': self.rating,
            'length': self.length,
            'bitrate': self.bitrate,
            'comment': self.comment,
            'lyrics': self.lyrics
            }
        if recurse:
            ret['album_id'] = self.album_id
            ret['album'] = self.album.to_dict(recurse=False)
        return ret


class MusicPlaylist(BaseModel):
    '''A music file container

    Users can create and add music tracks to a playlist
    '''

    __storm_table__ = 'musicplaylist'
    id = Int(primary=True)
    title = Unicode()
    tracks = ReferenceSet(  'MusicPlaylist.id',
                            'MusicPlaylistTrack.playlist_id',
                            'MusicPlaylistTrack.track_id',
                            'MusicTrack.id')


class MusicPlaylistTrack(BaseModel):
    '''Join table between MusicTrack and MusicPlaylist'''

    __storm_table__ = 'musicplaylisttrack'
    __storm_primary__ = 'track_id', 'playlist_id'
    track_id = Int(primary=True)
    playlist_id = Int()


class VideoFile(BaseModel):
    '''Video file reference and metadata'''

    __storm_table__ = 'videofile'
    id = Int(primary=True)
    filename = Unicode()
    thumb = Unicode()
    type = Unicode() #Default 'CLIP'

    def to_dict(self, recurse=True):
        '''See BaseModel.to_dict.'''
        ret = {
            'id': self.id,
            'filename': self.filename,
            'thumb': self.thumb,
            'type': self.type
            }
        return ret


class VideoSeries(BaseModel):
    '''A video container

    Videos can be grouped by the series they were created for, with their
    accompanying season and episode numbers.  This does not apply to anything
    but television
    '''

    __storm_table__ = 'videoseries'
    id = Int(primary=True)
    title = Unicode()
    actor_1 = Unicode()
    actor_2 = Unicode()
    actor_3 = Unicode()
    actor_4 = Unicode()
    actor_5 = Unicode()
    writer_1 = Unicode()
    writer_2 = Unicode()
    director_1 = Unicode()
    director_2 = Unicode()


class VideoMeta(BaseModel):
    '''Extra meta data for different types of videos'''

    __storm_table__ = 'videometa'
    id = Int(primary=True)
    season = Int()
    episode = Int()
    runtime = Int()
    genres = Unicode()
    year = Int()
    plot = Unicode()
    file_id = Int()
    file = Reference(file_id, 'VideoFile.id')
    series_id = Int()
    series = Reference(series_id, VideoSeries.id)


