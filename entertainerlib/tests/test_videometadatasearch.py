# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests VideoMetadataSearch'''

from entertainerlib.backend.components.mediacache.video_metadata_search import (
    VideoMetadataSearch)
from entertainerlib.tests import EntertainerTest

class testVideoMetadataSearch(EntertainerTest):
    '''Tests VideoMetdataSearch'''

    def testMetadataConstructor(self):
        '''testMetadataConstructor - Ensures instantiation of metadata search
        class'''
        serie = "/home/user/videos/Futurama s02e05 something.avi"
        self.video_metadata_search_serie = VideoMetadataSearch(serie)
        self.assertTrue(isinstance(self.video_metadata_search_serie,
                        VideoMetadataSearch))

    def testSerieTitle(self):
        '''testSerieTitle - Ensures a serie title is returned correctly'''
        serie = "/home/user/videos/Futurama s02e05 something.avi"
        self.video_metadata_search_serie = VideoMetadataSearch(serie)
        self.assertEqual(self.video_metadata_search_serie.title, "futurama")

    def testSerieSeason(self):
        '''testSerieSeason - Ensures a serie season is returned correctly'''
        serie = "/home/user/videos/Futurama s02e05 something.avi"
        self.video_metadata_search_serie = VideoMetadataSearch(serie)
        self.assertEqual(self.video_metadata_search_serie.season, 2)

    def testSerieEpisode(self):
        '''testSerieEpisode - Ensures a serie episode is returned correctly'''
        serie = "/home/user/videos/Futurama s02e05 something.avi"
        self.video_metadata_search_serie = VideoMetadataSearch(serie)
        self.assertEqual(self.video_metadata_search_serie.episode, 5)

    def testMovieTitle(self):
        '''testMovieTitle - Ensures a movie title is returned correctly'''
        movie = "/home/user/videos/Clerks.2[2006]DvDrip[Eng]-aXXo.avi"
        self.video_metadata_search_movie = VideoMetadataSearch(movie)
        title = "clerks 2"
        self.assertEqual(self.video_metadata_search_movie.title, title)

    def testMovieSeason(self):
        '''testMovieSeason - Ensures a movie season is 0'''
        movie = "/home/user/videos/Clerks.2[2006]DvDrip[Eng]-aXXo.avi"
        self.video_metadata_search_movie = VideoMetadataSearch(movie)
        season = 0
        self.assertEqual(self.video_metadata_search_movie.season, season)

    def testMovieEpisode(self):
        '''testMovieEpisode - Ensures a movie episode is 0'''
        movie = "/home/user/videos/Clerks.2[2006]DvDrip[Eng]-aXXo.avi"
        self.video_metadata_search_movie = VideoMetadataSearch(movie)
        episode = 0
        self.assertEqual(self.video_metadata_search_movie.episode, episode)
