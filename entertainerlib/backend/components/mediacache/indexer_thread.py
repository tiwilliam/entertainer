# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''IndexerThread - Walks directories recursively and adds files to cache.'''

import threading

from entertainerlib.backend.components.mediacache.image_cache import ImageCache
from entertainerlib.backend.components.mediacache.music_cache import MusicCache
from entertainerlib.backend.components.mediacache.video_cache import VideoCache

class IndexerThread(threading.Thread):
    """
    IndexerThread

    This is a thread that indexes all the media into media cache. Each media
    type has it's own indexing thread. Each thread therefore has a media type
    which is set with setCacheType() -method.
    """

    def __init__(self):
        """
        Create a new indexer thread.
        """
        threading.Thread.__init__(self)
        self.setName("IndexerThread")
        self.cache_type = None
        # Root folders (Root folders that should be indexed.
        # Get from content.conf)
        self.root_folders = None

    def setCacheType(self, cache_type):
        """
        Set cache type  for this indexer. Allowed values are 'image','music',
        'video'
        @param cache_type: Cache type (String)
        """
        if (cache_type != "image" and
            cache_type != "music" and
            cache_type != "video"):
            raise Exception("Illegal cache type.")
        else:
            self.cache_type = cache_type

    def setFolders(self, folders):
        """
        Set root folders for this indexer
        @param folders: String array that contains folder paths
        """
        self.root_folders = folders

    def run(self):
        """
        Walk root directories recursively and add all found files to the cache.
        """
        if self.cache_type == "image":
            cache = ImageCache()
        elif self.cache_type == "music":
            cache = MusicCache()
        elif self.cache_type == "video":
            cache = VideoCache()

        if self.root_folders == None:
            return

        for element in self.root_folders:
            cache.addDirectory(element)

