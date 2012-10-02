# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests Screen'''

import clutter

from entertainerlib.exceptions import ScreenException
from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.tab_group import TabGroup
from entertainerlib.tests import EntertainerTest

class ScreenTest(EntertainerTest):
    """Test for entertainerlib.gui.screens.screen"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.screen = Screen()
        self.tabs_screen = Screen(has_tabs=True)
        self.tab = Tab('test')
        self.tabs_screen.add_tab(self.tab)

        self.select = UserEvent(UserEvent.NAVIGATE_SELECT)

    def tearDown(self):
        '''Clean up after the test.'''
        EntertainerTest.tearDown(self)

    def test_create(self):
        '''Test correct Screen initialization.'''
        self.assertTrue(isinstance(self.screen, (Base, clutter.Group)))

    def test_size(self):
        '''Test that screen got set to the correct size'''
        self.assertEqual(self.screen.get_size(), (1366, 768))

    def test_has_tabs(self):
        '''Test that a screen with tabs contains a tab group.'''
        self.assertTrue(isinstance(self.tabs_screen.tab_group, TabGroup))

    def test_add_tab_for_tab_screen(self):
        '''Test adding a tab to a screen with tabs enabled.'''
        test_tab = Tab('another')
        self.tabs_screen.add_tab(test_tab)
        return_tab = self.tabs_screen.tab_group.tab('another')
        self.assertEqual(return_tab, test_tab)

    def test_add_tab_for_screen(self):
        '''Test adding a tab to a screen with no tabs enabled fails.'''
        self.assertRaises(ScreenException, self.screen.add_tab, self.tab)

    def test_tab_handle_user_event(self):
        '''Test screen correctly passes an event to the tab_group.'''
        self.assertFalse(self.tabs_screen.handle_user_event(self.select))

    def test_handle_user_event(self):
        '''Test the set of user events that are allowed by default.'''
        up = UserEvent(UserEvent.NAVIGATE_UP)
        down = UserEvent(UserEvent.NAVIGATE_DOWN)
        left = UserEvent(UserEvent.NAVIGATE_LEFT)
        right = UserEvent(UserEvent.NAVIGATE_RIGHT)
        not_handled = UserEvent(UserEvent.QUIT)

        self.assertFalse(self.screen.handle_user_event(self.select))
        self.assertFalse(self.screen.handle_user_event(up))
        self.assertFalse(self.screen.handle_user_event(down))
        self.assertFalse(self.screen.handle_user_event(left))
        self.assertFalse(self.screen.handle_user_event(right))
        self.assertFalse(self.screen.handle_user_event(not_handled))

    def test_kind(self):
        '''Test the kind property default and a set value.'''
        self.assertEqual(self.screen.kind, Screen.NORMAL)
        self.osd = Screen(kind=Screen.OSD)
        self.assertEqual(self.osd.kind, Screen.OSD)

    def test_name(self):
        '''Test the name property default and a set value.'''
        self.assertEqual(self.screen.name, '')
        self.named = Screen('Named')
        self.assertEqual(self.named.name, 'Named')

