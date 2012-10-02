# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests ListIndicator.'''

from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.tests import EntertainerTest


class ListIndicatorTest(EntertainerTest):
    '''Test for entertainerlib.gui.widgets.list_indicator.'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.indicator = ListIndicator(0.7, 0.8, 0.2, 0.045,
            ListIndicator.HORIZONTAL)

    def test_create(self):
        '''Test correct ListIndicator initialization.'''
        self.assertTrue(isinstance(self.indicator, ListIndicator))

    def test_currentmax(self):
        '''Test methods to handle the current and maximum attributes.'''
        self.indicator.set_current(10)
        self.assertEqual(self.indicator.get_current(), 1)
        self.indicator.set_current(-99)
        self.assertEqual(self.indicator.get_current(), 1)
        self.indicator.set_maximum(10)
        self.indicator.set_current(5)
        self.assertEqual(self.indicator.get_current(), 5)

    def test_setdelimiter(self):
        '''Test the set_delimiter method.'''
        self.indicator.set_maximum(100)
        self.indicator.set_current(50)
        self.indicator.set_delimiter(" * ")
        self.assertEqual(self.indicator.text.get_text(), "50 * 100")

