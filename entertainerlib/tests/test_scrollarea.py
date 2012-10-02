# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests ScrollArea"""

from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.scroll_area import ScrollArea
from entertainerlib.tests import EntertainerTest

class ScrollAreaTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.scroll_area"""

    def setUp(self):
        """Set up the test."""
        EntertainerTest.setUp(self)

        # Get a workable amount of text
        text = "Here is the start. "
        # pylint: disable-msg=W0612
        for i in range(0, 100):
            text += "Here is sentence number "

        self.label = Label(0.1, "screentitle", 0.1, 0.2, text)
        self.scroll_area = ScrollArea(0.5, 0.6, 0.1, 0.1, self.label)

    def test_create(self):
        """Test correct ScrollArea initialization."""
        self.assertTrue(isinstance(self.scroll_area, ScrollArea))

    def test_active(self):
        '''Test the use of the active property.'''
        self.scroll_area.active = True
        self.assertTrue(self.scroll_area.active)
        self.scroll_area.active = False
        self.assertFalse(self.scroll_area.active)

    def test_on_top_bottom(self):
        '''Test the use of the on_top, on_bottom properties.'''
        self.scroll_area.offset = 0
        self.scroll_area.stop_animation()
        self.assertTrue(self.scroll_area.on_top)
        self.assertFalse(self.scroll_area.on_bottom)

        self.scroll_area.scroll_to_bottom()
        self.scroll_area.stop_animation()
        self.assertFalse(self.scroll_area.on_top)
        self.assertTrue(self.scroll_area.on_bottom)

    def test_offset(self):
        '''Test the use of the offset property.'''
        self.scroll_area.scroll_to_bottom()
        offset = self.scroll_area.offset
        self.scroll_area.offset = 0
        self.assertTrue(self.scroll_area.offset != offset)

    def test_set_content(self):
        '''Test the use of the set_content method.'''
        self.scroll_area.set_content(Label(0.1, "screentitle", 0.1, 0.2, "foo"))
        self.assertFalse(self.scroll_area.content == self.label)
        self.scroll_area.set_content(self.label)
        self.assertTrue(self.scroll_area.content == self.label)

    def test_scroll(self):
        '''Test the use of scroll methods.'''
        self.scroll_area.scroll_to_bottom()
        self.scroll_area.stop_animation()
        self.assertTrue(self.scroll_area.on_bottom)
        self.scroll_area.scroll_to_top()
        self.scroll_area.stop_animation()
        self.assertTrue(self.scroll_area.on_top)
        self.assertTrue(self.scroll_area.offset == 0)
        self.scroll_area.scroll_down()
        self.scroll_area.stop_animation()
        self.assertFalse(self.scroll_area.offset == 0)
        self.scroll_area.scroll_up()
        self.scroll_area.stop_animation()
        self.assertTrue(self.scroll_area.offset == 0)

