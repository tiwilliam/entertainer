# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Interface for media caches'''

class Cache:
    """
    Cache interface. Defines interface for cache handling. This
    interface is implemented by VideoCache, MusicCache and
    ImageCache classes.
    """

    #How many millisecons we should wait between files when adding to cache.
    SLEEP_TIME_BETWEEN_FILES = 2000

    def clearCache(self):
        """
        Implement this method in deriving classes.

        This method removes the cache completely. It should be used when the
        cache needs to be rebuild from scratch.
        """
        pass

    def addFile(self, filename):
        """
        Implement this method in deriving classes.

        This method adds a new file to the cache. This method should get all
        metadata from the internet, create a thumbnail etc.
        """
        pass

    def removeFile(self, filename):
        """
        Implement this method in deriving classes.

        This method removes file from the cache. This also should remove all
        extrnal data like thumbnails.
        """
        pass

    def updateFile(self, filename):
        """
        Implement this method in deriving classes.

        This method is executed when a file, that is already in cache, changes.
        This can happen forexample if user uses some ID3-tag editor for audio
        files. This method should update cache and all metadata up-to-date.
        """
        pass

    def addDirectory(self, path):
        """
        Implement this method in deriving classes.

        This method adds a new directory to the cache. Sub directories are
        added recursively and all files in them.
        """
        pass

    def removeDirectory(self, path):
        """
        Implement this method in deriving classes.

        This method removes directory from the cache. Also removes all
        subdirectories and all files in them. This also should remove all
        external data like thumbnails.
        """
        pass

    def updateDirectory(self, path):
        """
        Implement this method in deriving classes.

        This method is executed when a file, that is already in cache, changes.
        This can happen forexample if user uses some ID3-tag editor for audio
        files. This method should update cache and all metadata up-to-date.
        """
        pass

    def isDirectoryInCache(self, path):
        """
        Implement this method in deriving classes.

        This method returns True if given directory is in cache. Otherwise
        method returns False.
        """
        pass

    def isFileInCache(self, filename):
        """
        Implement this method in deriving classes.

        This method returns True if given file is in cache. Otherwise
        method returns False.
        """
        pass

    def isSupportedFormat(self, filename):
        """
        Returns true if cache can handle the given file. Otherwise returns
        false
        """
        pass

