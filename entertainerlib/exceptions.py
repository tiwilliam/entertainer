# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Various Exceptions for Entertainer.'''


class ThumbnailerException(Exception):
    '''Abstract thumbnailer exception'''


class ImageThumbnailerException(ThumbnailerException):
    '''An exception specific to the ImageThumbnailer'''


class VideoThumbnailerException(ThumbnailerException):
    '''An exception specific to the video thumbnailer'''


class ScreenException(Exception):
    '''An exception specific to the Screen class'''


