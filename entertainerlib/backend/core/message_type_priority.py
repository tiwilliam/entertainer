# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Determines message types and priorities'''

class MessagePriority:
    """
    Simply determines Message priority constants.

    These are used when MessageHandlers are registered to the MessageBus.
    This definition makes code easy to read.
    """
    VERY_HIGH = 0
    HIGH = 10
    NORMAL = 20
    LOW = 30
    VERY_LOW = 40

class MessageType:
    """Determines all allowed Message types. MessageHandler should use these to
    determine type. This simply makes code more readable."""

    # Indicates that Content Management UI has been used to update contents.
    CONTENT_CONF_UPDATED = 0

    # Require to rebuild image cache
    REBUILD_IMAGE_CACHE = 1

    # Require to rebuild music cache
    REBUILD_MUSIC_CACHE = 2

    # Require to rebuild video cache
    REBUILD_VIDEO_CACHE = 3

