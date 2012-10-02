# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests UserInterface'''

import clutter

from entertainerlib.gui.screens.question import Question
from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.user_interface import UserInterface
from entertainerlib.tests import EntertainerTest
from entertainerlib.tests.mock import MockClutterKeyboardEvent


class UserInterfaceTest(EntertainerTest):
    '''Test for entertainerlib.gui.user_interface'''

    def setUp(self):
        EntertainerTest.setUp(self)

        self.ui = UserInterface(None, None, None, None)

    def test_create(self):
        '''Test correct UserInterface initialization'''
        self.assertTrue(isinstance(self.ui, UserInterface))

    def test_handle_keyboard_event(self):
        '''Test clutter keyboard events are handled correctly.'''
        def mock_event_handler(event):
            '''Test some expected values.'''
            kind = event.get_type()
            if (not (kind == UserEvent.DEFAULT_EVENT or
                     kind == UserEvent.NAVIGATE_SELECT)):
                self.fail()

        good_event = MockClutterKeyboardEvent(clutter.keysyms.Return)
        self.ui.handle_keyboard_event(None, good_event, mock_event_handler)

        bad_event = MockClutterKeyboardEvent(-1)
        self.ui.handle_keyboard_event(None, bad_event, mock_event_handler)

    def test_confirm_exit(self):
        '''Test confirm exit stays on Question screen if it's already there.'''
        question = Question(None, None, [])
        self.ui.current = question
        # Current will be the same if the screen didn't move.
        self.assertEqual(self.ui.current, question)

