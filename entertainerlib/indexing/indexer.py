'''Indexer module.'''

# Pylint thinks that handlers isn't being used when it clearly is. Ignore it.
# pylint: disable-msg=W0611
from entertainerlib.indexing import handlers
from entertainerlib.configuration import Configuration
from entertainerlib.logger import Logger

__meta__ = type


class Indexer:
    '''Indexer class for indexing media.'''

    handlers = {
        'avi': handlers.AviHandler(),
        'jpg': handlers.JpegHandler(),
        'jpeg': handlers.JpegHandler(),
        'm4v': None,
        'mkv': None,
        'mov': None,
        'mp3': handlers.Mp3Handler(),
        'mp4': None,
        'mpeg': None,
        'mpg': None,
        'ogg': None,
        'ogm': None,
        'png': None,
        'wmv': None,
        }

    def __init__(self):
        self.configuration = Configuration()
        self.logger = Logger().getLogger(
            'entertainerlib.indexer.indexing.Indexer')

    def run(self):
        '''Run the indexer.

        The Indexer will iterate through media folders and find media that is
        supported by Entertainer.
        '''

    @property
    def supported_filetypes(self):
        '''Return a list of all support filetypes.'''
        return self.handlers.keys()

    def get_filetype_handler(self, filetype):
        '''Return the handler for a given filetype.'''
        try:
            return self.handlers[filetype]
        except KeyError:
            return None

    def is_supported_filetype(self, filename):
        '''Return whether or not a file is supported by the indexer.'''
        extension = filename.split('.')[-1]
        return extension in self.supported_filetypes

