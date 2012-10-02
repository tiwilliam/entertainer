# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests GridMenu"""

import clutter

from entertainerlib.gui.widgets.grid_menu import GridMenu
from entertainerlib.gui.widgets.menu_item import MenuItem
from entertainerlib.tests import EntertainerTest

class GridMenuTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.grid_menu"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.menu = GridMenu(0, 0)

        self.cursor = clutter.Rectangle()

        self.item = MenuItem()
        self.item.userdata = "foo"

        self.menu.raw_add_item(MenuItem())
        self.menu.raw_add_item(MenuItem())
        self.menu.raw_add_item(self.item)
        self.menu.raw_add_item(MenuItem())

        self.menu.items_per_row = 2
        self.menu.items_per_col = 2
        self.menu.visible_rows = 2
        self.menu.visible_cols = 2

    def test_create(self):
        '''Test correct GridMenu initialization.'''
        self.assertTrue(isinstance(self.menu, GridMenu))

    def test_count(self):
        '''Test the use of the count property.'''
        self.assertEqual(self.menu.count, 4)

    def test_on_top_bottom_right_left(self):
        '''
        Test the use of the on_top, on_bottom, on_right and on_left
        properties.
        '''
        self.menu.selected_index = 0
        self.menu.stop_animation()
        self.assertTrue(self.menu.on_top)
        self.assertFalse(self.menu.on_bottom)
        self.assertFalse(self.menu.on_right)
        self.assertTrue(self.menu.on_left)

        self.menu.selected_index = 3
        self.menu.stop_animation()
        self.assertFalse(self.menu.on_top)
        self.assertTrue(self.menu.on_bottom)
        self.assertTrue(self.menu.on_right)
        self.assertFalse(self.menu.on_left)

    def test_selected_item(self):
        '''Test the use of the selected_item property.'''
        self.menu.selected_index = 2
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_item, self.item)

    def test_selected_userdata(self):
        '''Test the use of the selected_userdata property.'''
        self.menu.selected_index = 2
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_userdata, "foo")

    def test_active(self):
        '''Test the use of the active property.'''
        self.menu.active = True
        self.assertTrue(self.menu.active)
        self.menu.active = False
        self.assertFalse(self.menu.active)

    def test_horizontal_vertical(self):
        '''Test the use of the horizontal and vertical properties.'''
        self.menu.horizontal = True
        self.assertTrue(self.menu.horizontal)
        self.assertFalse(self.menu.vertical)
        self.menu.vertical = True
        self.assertFalse(self.menu.horizontal)
        self.assertTrue(self.menu.vertical)

    def test_selected_index(self):
        '''Test the use of the selected_index property.'''
        self.menu.selected_index = 2
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 2)

    def test_visible_rows_cols(self):
        '''Test the use of the visible_rows and visible_cols properties.'''
        self.menu.visile_rows = 20
        self.menu.visile_cols = 10
        self.assertEqual(self.menu.visile_rows, 20)
        self.assertEqual(self.menu.visile_cols, 10)
        # Restore previous state.
        self.menu.visile_rows = 2
        self.menu.visile_cols = 2

    def test_cursor(self):
        '''Test the use of the cursor property.'''
        self.assertEqual(self.menu.cursor, None)
        self.menu.cursor = self.cursor
        self.assertEqual(self.menu.cursor, self.cursor)

    def test_up_down_right_left(self):
        '''Test the use of the up, dow, right and left methods.'''
        self.menu.selected_index = 0
        self.menu.stop_animation()
        self.menu.items_per_row = 2
        self.menu.items_per_col = 2
        self.menu.visible_rows = 2
        self.menu.visible_cols = 2
        self.menu.right()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 1)
        self.menu.down()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 3)
        self.menu.left()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 2)
        self.menu.up()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 0)

        # Test of top/left limit.
        self.menu.up()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 0)
        self.menu.left()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 0)

        # Test of bottom/right limit.
        self.menu.selected_index = 3
        self.menu.stop_animation()
        self.menu.down()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 3)
        self.menu.right()
        self.menu.stop_animation()
        self.assertEqual(self.menu.selected_index, 3)

