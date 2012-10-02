# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''MediaCacheManager - Downloads metadata and keeps media cache up-to-date'''

from entertainerlib.configuration import Configuration
from entertainerlib.logger import Logger

from entertainerlib.backend.core.message_type_priority import MessageType
from entertainerlib.backend.core.message_handler import MessageHandler
from entertainerlib.backend.components.mediacache.indexer_thread import (
    IndexerThread)
from entertainerlib.backend.components.mediacache.image_cache import ImageCache
from entertainerlib.backend.components.mediacache.music_cache import MusicCache
from entertainerlib.backend.components.mediacache.video_cache import VideoCache

class MediaCacheManager(MessageHandler):
    """Makes sure that client has all the data available."""

    def __init__(self):
        """
        Create a new MediaCacheManager object
        """
        MessageHandler.__init__(self)
        self.logger = Logger().getLogger(
            'backend.components.mediacache.MediaCacheManager')
        self.config = Configuration()
        self.video_folders = self.config.media_folders
        self._index_videos(self.video_folders)
        self.music_folders = self.config.media_folders
        self._index_music(self.music_folders)
        self.image_folders = self.config.media_folders
        self._index_images(self.image_folders)

        # Should we rebuild to detect files that were removed while backend was
        # not running?! THERE HAS TO BE A BETTER SOLUTION FOR THIS PROBLEM
        #self.rebuildAllMediaCaches()

    def rebuildAllMediaCaches(self):
        """Rebuilds all media caches."""
        self.rebuildImageCache()
        self.rebuildMusicCache()
        self.rebuildVideoCache()

    def rebuildVideoCache(self):
        """Destroy all current data and index everything from the scratch."""
        self.logger.info("Video cache rebuilding requested")
        video_cache = VideoCache()
        video_cache.clearCache()
        self._index_videos(self.video_folders)

    def rebuildMusicCache(self):
        """Destroy all current data and index everything from the scratch."""
        self.logger.info("Music cache rebuilding requested")
        music_cache = MusicCache()
        music_cache.clearCache()
        self._index_music(self.music_folders)

    def rebuildImageCache(self):
        """Destroy all current data and index everything from the scratch."""
        self.logger.info("Image cache rebuilding requested")
        image_cache = ImageCache()
        image_cache.clearCache()
        self._index_images(self.image_folders)

    # Implements MessageHandler interface
    def handleMessage(self, message):
        '''Handles messages'''
        if message.get_type() == MessageType.CONTENT_CONF_UPDATED:
            self._update_content_folders()
        elif message.get_type() == MessageType.REBUILD_VIDEO_CACHE:
            self.rebuildVideoCache()
        elif message.get_type() == MessageType.REBUILD_MUSIC_CACHE:
            self.rebuildMusicCache()
        elif message.get_type() == MessageType.REBUILD_IMAGE_CACHE:
            self.rebuildImageCache()

    def _index_images(self, folders):
        """Index images from the given folders and their subfolders"""
        if len(folders) > 0:
            indexer = IndexerThread()
            indexer.setCacheType("image")
            indexer.setFolders(folders)
            indexer.start()

    def _index_music(self, folders):
        """Index music from the given folders and their subfolders"""
        if len(folders) > 0:
            indexer = IndexerThread()
            indexer.setCacheType("music")
            indexer.setFolders(folders)
            indexer.start()

    def _index_videos(self, folders):
        """Index videos from the given folders and their subfolders"""
        if len(folders) > 0:
            indexer = IndexerThread()
            indexer.setCacheType("video")
            indexer.setFolders(folders)
            indexer.start()

    def _update_content_folders(self):
        """
        This updates media manager's content folders. This method is
        executed when content.conf has been updated. If folders are added
        we need to index them. If folders are removed, we need to remove
        them from the cache and also from FileSystemObeserver.
        """
        updated_video_folders = self.config.media_folders
        updated_music_folders = self.config.media_folders
        updated_image_folders = self.config.media_folders

        # Handle image folder changes
        current_images = set(self.image_folders)
        updated_images = set(updated_image_folders)
        removed_images = current_images - updated_images
        new_images = updated_images - current_images
        self.image_folders = updated_image_folders

        image_cache = ImageCache()
        for element in removed_images:
            image_cache.removeDirectory(element)

        self._index_images(list(new_images))

        # Handle music folder changes
        current_music = set(self.music_folders)
        updated_music = set(updated_music_folders)
        removed_music = current_music - updated_music
        new_music = updated_music - current_music
        self.music_folders = updated_music_folders

        music_cache = MusicCache()
        for element in removed_music:
            music_cache.removeDirectory(element)

        self._index_music(list(new_music))

        # Handle video folder changes
        current_videos = set(self.video_folders)
        updated_videos = set(updated_video_folders)
        removed_videos = current_videos - updated_videos
        new_videos = updated_videos - current_videos
        self.video_folders = updated_video_folders

        video_cache = VideoCache()
        for element in removed_videos:
            video_cache.removeDirectory(element)

        self._index_videos(list(new_videos))

