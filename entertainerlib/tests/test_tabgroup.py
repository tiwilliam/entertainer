# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests TabGroup'''

from entertainerlib.gui.tabs.tab import Tab
from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.widgets.tab_group import TabGroup
from entertainerlib.tests import EntertainerTest

class TabGroupTest(EntertainerTest):
    '''Test for entertainerlib.gui.widgets.tab_goup.'''

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.tab_group = TabGroup(0.95, 0.13, 'title')

        tab1 = Tab("tab1", "title1", None)
        self.tab2 = Tab("foo", "title2", None)

        self.tab_group.add_tab(tab1)
        self.tab_group.add_tab(self.tab2)

    def test_create(self):
        '''Test correct TabGroup initialization.'''
        self.assertTrue(isinstance(self.tab_group, TabGroup))

    def test_active(self):
        '''Test the active property.'''
        self.tab_group.active = False
        self.assertEqual(self.tab_group.active, False)
        self.tab_group.active = True
        self.assertEqual(self.tab_group.active, True)

    def test_len(self):
        '''Test the use of len on a TabGroup.'''
        self.assertEqual(len(self.tab_group), 2)

    def test_tab(self):
        '''Test the use of the tab method.'''
        self.assertEqual(self.tab_group.tab("foo"), self.tab2)

    def test_add_tab(self):
        '''Test the use of the add_tab method.'''
        tabs = len(self.tab_group)
        self.tab_group.add_tab(Tab("tab3", "title3", None))
        self.assertEqual(len(self.tab_group), tabs + 1)

    def test_keyboard_navigation(self):
        '''Test the effect of keyboard navigation events.'''
        self.tab_group.active = True
        start_tab = self.tab_group.current_tab
        right_event = UserEvent(UserEvent.NAVIGATE_RIGHT)
        left_event = UserEvent(UserEvent.NAVIGATE_LEFT)
        self.tab_group.handle_user_event(right_event)
        self.tab_group.handle_user_event(left_event)
        self.assertEqual(self.tab_group.current_tab, start_tab)

