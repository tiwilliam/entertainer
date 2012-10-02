'''Tests for entertainerlib.indexing.utilities.'''
import os

from entertainerlib.indexing.utilities import TagGetter
from entertainerlib.tests import EntertainerTest


class TestTagGetter(EntertainerTest):
    '''Test for entertainerlib.indexing.utilties.TagGetter.'''

    def test_constructor(self):
        '''Test TagGetter.__init__.'''
        tag_getter = TagGetter(os.path.join(self.data_dir, 'test.mp3'))
        self.assertTrue(isinstance(tag_getter, TagGetter))

    def test_get_tags(self):
        '''Test TagGetter.get_tags.'''
        tag_getter = TagGetter(os.path.join(self.data_dir, 'test.mp3'))
        self.assertEqual(tag_getter.artist, 'Iron and Wine')
        self.assertEqual(tag_getter.album, 'The Shephard\'s Dog')
        self.assertEqual(tag_getter.genre, 'Gangster Rap')
        self.assertEqual(tag_getter.title, 'Flightless Bird, American Mouth')
        self.assertEqual(tag_getter.comment, 'This is a comment')
        self.assertEqual(tag_getter.track_number, 12)
        self.assertEqual(tag_getter.album_disc_number, 1)
        #self.assertEqual(tag_getter.date, '2000-01-01')

    def test_get_invalid_tags(self):
        '''Test TagGetter.get_tags with nonexistent tags.'''
        tag_getter = TagGetter(os.path.join(self.data_dir, 'test.mp3'))
        self.assertEqual(tag_getter.yabba_dabba_doo, None)

