# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Main backend server object'''

import gobject

from entertainerlib.backend.components.mediacache.media_cache_manager import (
    MediaCacheManager)
from entertainerlib.backend.core.message_bus import MessageBus
from entertainerlib.backend.core.message_scheduler import MessageScheduler
from entertainerlib.backend.core.connection_server import ConnectionServer
from entertainerlib.backend.core.message_type_priority import (
    MessageType, MessagePriority)
from entertainerlib.configuration import Configuration
from entertainerlib.logger import Logger

class BackendServer:
    '''Backend is responsible for things like updating media library cache.'''

    def __init__(self):
        gobject.threads_init()

        self.config = Configuration()
        self.logger = Logger().getLogger('backend.BackendServer')
        self.message_bus = MessageBus()
        self._port = self.config.port

        # Connection server - Thread that listens incoming socket connections
        self.connection_server = None

        self.scheduler = None
        self.media_manager = None

        # The order of the initialize method calls is significant! Don't change
        # the order unless you know what you are doing!
        self.initialize_configuration()
        self.initialize_media_cache_manager()
        self.initialize_connection_server()
        self.initialize_scheduler()

    def initialize_configuration(self):
        """Initialize configuration"""
        cfg_dict = {
            MessageType.CONTENT_CONF_UPDATED : MessagePriority.VERY_HIGH,
            }
        self.message_bus.registerMessageHandler(self.config, cfg_dict)
        self.logger.debug("Configuration intialized successfully")

    def initialize_connection_server(self):
        """Initialize connection server."""
        self.connection_server = ConnectionServer(self._port, self.message_bus)
        # Start listening incoming connections
        self.connection_server.start()

    def initialize_scheduler(self):
        """Initialize message scheduler."""
        self.scheduler = MessageScheduler(self.message_bus)
        self.logger.debug("Message scheduler intialized successfully")

    def initialize_media_cache_manager(self):
        '''Initialize the media cache manager'''
        self.media_manager = MediaCacheManager()
        media_dict = {
            MessageType.CONTENT_CONF_UPDATED : MessagePriority.VERY_LOW,
            MessageType.REBUILD_IMAGE_CACHE : MessagePriority.HIGH,
            MessageType.REBUILD_MUSIC_CACHE : MessagePriority.HIGH,
            MessageType.REBUILD_VIDEO_CACHE : MessagePriority.HIGH
            }
        self.message_bus.registerMessageHandler(self.media_manager, media_dict)
        self.logger.debug("Media Manager intialized successfully")

