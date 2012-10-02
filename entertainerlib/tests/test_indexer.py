'''Tests for the indexer.'''
from logging import Logger

from entertainerlib.configuration import Configuration
from entertainerlib.indexing.handlers import AviHandler
from entertainerlib.indexing.indexer import Indexer
from entertainerlib.tests import EntertainerTest


class IndexerTest(EntertainerTest):
    '''Tests for `entertainerlib.indexing.indexer`.'''

    def test_constructor(self):
        '''Test the Indexer constructor.'''
        indexer = Indexer()
        self.assertTrue(isinstance(indexer, Indexer))

        self.assertTrue(isinstance(indexer.logger, Logger))
        self.assertTrue(isinstance(indexer.configuration, Configuration))

    def test_supported_filetypes(self):
        '''Test Indexer.supported_filetypes.'''
        indexer = Indexer()
        self.assertEquals(len(indexer.supported_filetypes), 14)
        self.assertEquals(sorted(indexer.supported_filetypes),
            ['avi', 'jpeg', 'jpg', 'm4v', 'mkv', 'mov', 'mp3', 'mp4', 'mpeg',
                'mpg', 'ogg', 'ogm', 'png', 'wmv'])

    def test_valid_get_filetype_handler(self):
        '''Test Indexer.get_filetype_handler with a valid filetype.'''
        indexer = Indexer()
        self.assertTrue(type(indexer.get_filetype_handler('avi')),
            AviHandler)

    def test_invalid_get_filetype_handler(self):
        '''Test Indexer.get_filetype_handler with an invalid filetype.'''
        indexer = Indexer()
        self.assertEquals(indexer.get_filetype_handler('aeiou'), None)

    def test_is_supported_filetype(self):
        '''Test Indexer.is_supported_filetype with a supported filetype.'''
        indexer = Indexer()
        self.assertTrue(indexer.is_supported_filetype('foo.avi'))
        self.assertTrue(indexer.is_supported_filetype('baz.bar.mp3'))

    def test_is_not_supported_filetype(self):
        '''Test Indexer.is_supported_filetype with an unsupported filetype.'''
        indexer = Indexer()
        self.assertFalse(indexer.is_supported_filetype('not.aeiou'))

    def test_run(self):
        '''Test the indexer runs and indexes the proper media.'''
        indexer = Indexer()
        indexer.run()


