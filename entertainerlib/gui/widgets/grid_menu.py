# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''GridMenu contains a grid of MenuItem based widgets.'''

import math

import clutter
import gobject

from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.motion_buffer import MotionBuffer

class GridMenu(Base, clutter.Group):
    """
    GridMenu widget.

    A core widget to handle MenuItem in a grid with a cursor.
    This widget provides all the necessary logic to move items and the cursor.
    """
    __gsignals__ = {
        'activated' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'moved' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'selected' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
    }

    MODE_NONE = 0
    MODE_SELECT = 1
    MODE_SEEK = 2

    def __init__(self, x=0, y=0, item_width=0.2, item_height=0.1):
        Base.__init__(self)
        clutter.Group.__init__(self)

        self.motion_duration = 100          # Default duration of animations ms.
        self.cursor_below = True            # Is the cursor below items?
        self._active = None
        self._is_vertical = True
        self.items = []

        # Items dimensions variable: relative, absolute, center
        self._item_width = item_width
        self._item_height = item_height
        self._item_width_abs = self.get_abs_x(item_width)
        self._item_height_abs = self.get_abs_y(item_height)
        self._dx = int(self._item_width_abs / 2)
        self._dy = int(self._item_height_abs / 2)

        # Default cursor's index.
        self._selected_index = 0

        # Grid dimensions: real, visible.
        self.items_per_row = 10
        self.items_per_col = 10
        self._visible_rows = 3
        self._visible_cols = 5

        # The moving_group is a Clutter group containing all the items.
        self._moving_group_x = 0
        self._moving_group_y = 0
        self._moving_group = clutter.Group()
        self.add(self._moving_group)

        # The moving_group is translated using a `BehaviourPath`.
        self._moving_group_timeline = clutter.Timeline(200)
        moving_group_alpha = clutter.Alpha(self._moving_group_timeline,
            clutter.EASE_IN_OUT_SINE)
        moving_group_path = clutter.Path()
        self._moving_group_behaviour = clutter.BehaviourPath(moving_group_alpha,
            moving_group_path)
        self._moving_group_behaviour.apply(self._moving_group)

        # The cursor is an Actor that can be added and moved on the menu.
        # The cusor is always located in the visible (clipped) area of the menu.
        self._cursor_x = 0
        self._cursor_y = 0
        self._cursor = None
        self._cursor_timeline = clutter.Timeline(200)
        cursor_alpha = clutter.Alpha(self._cursor_timeline,
            clutter.EASE_IN_SINE)
        cursor_path = clutter.Path()
        self._cursor_behaviour = clutter.BehaviourPath(cursor_alpha,
            cursor_path)

        # A MotionBuffer is used to compute useful information about the
        # cursor's motion. It's used when moving the cursor with a pointer.
        self._motion_buffer = MotionBuffer()
        self._event_mode = self.MODE_NONE
        self._motion_handler = 0
        self._seek_step_x = 0
        self._seek_step_y = 0
        gobject.timeout_add(200, self._internal_timer_callback)

        #XXX: Samuel Buffet
        # This rectangle is used to grab events as it turns out that their
        # might be a bug in clutter 0.8 or python-clutter 0.8.
        # It may be avoided with next release of clutter.
        self._event_rect = clutter.Rectangle()
        self._event_rect.set_opacity(0)
        self.add(self._event_rect)
        self._event_rect.set_reactive(True)
        self._event_rect.connect('button-press-event',
            self._on_button_press_event)
        self._event_rect.connect('button-release-event',
            self._on_button_release_event)
        self._event_rect.connect('scroll-event', self._on_scroll_event)

        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

    @property
    def count(self):
        """Return the number of items."""
        return len(self.items)

    @property
    def on_top(self):
        """Return True if the selected item is currently on the top."""
        selected_row = self._index_to_xy(self._selected_index)[1]
        if selected_row == 0:
            return True
        else:
            return False

    @property
    def on_bottom(self):
        """Return True if the selected item is currently on the bottom."""
        selected_row = self._index_to_xy(self._selected_index)[1]
        if self._is_vertical:
            end_row = self._index_to_xy(self.count - 1)[1]
            if selected_row == end_row:
                return True
            else:
                return False
        else:
            if selected_row == self.items_per_col - 1:
                return True
            else:
                return False

    @property
    def on_left(self):
        """Return True if the selected item is currently on the left."""
        selected_col = self._index_to_xy(self._selected_index)[0]
        if selected_col == 0:
            return True
        else:
            return False

    @property
    def on_right(self):
        """Return True if the selected item is currently on the right."""
        selected_col = self._index_to_xy(self._selected_index)[0]
        if not self._is_vertical:
            end_col = self._index_to_xy(self.count - 1)[0]
            if selected_col == end_col:
                return True
            else:
                return False
        else:
            if selected_col == self.items_per_row - 1:
                return True
            else:
                return False

    @property
    def selected_item(self):
        """Return the selected MenuItem."""
        if self.count == 0:
            return None
        else:
            return self.items[self._selected_index]

    @property
    def selected_userdata(self):
        """Return userdata of the MenuItem."""
        item = self.selected_item
        if item is None:
            return None
        else:
            return item.userdata

    def _get_active(self):
        """Active property getter."""
        return self._active

    def _set_active(self, boolean):
        """Active property setter."""
        if self._active == boolean:
            return

        self._active = boolean
        if boolean:
            if self._cursor is not None:
                self._cursor.show()
            if  self.selected_item is not None:
                self.selected_item.animate_in()
            self.emit('activated')
            self.set_opacity(255)
        else:
            if self._cursor is not None:
                self._cursor.hide()
            if  self.selected_item is not None:
                self.selected_item.animate_out()
            self.set_opacity(128)

    active = property(_get_active, _set_active)

    def _get_horizontal(self):
        """horizontal property getter."""
        return not self._is_vertical

    def _set_horizontal(self, boolean):
        """horizontal property setter."""
        self._is_vertical = not boolean

    horizontal = property(_get_horizontal, _set_horizontal)

    def _get_vertical(self):
        """vertical property getter."""
        return self._is_vertical

    def _set_vertical(self, boolean):
        """vertical property setter."""
        self._is_vertical = boolean

    vertical = property(_get_vertical, _set_vertical)

    def _get_selected_index(self):
        """selected_index property getter."""
        return self._selected_index

    def _set_selected_index(self, index, duration=None):
        """selected_index property setter."""
        # Xc, Yc : coordinates of the menu's cursor on the array of items.
        # xc, yc : coordinates of the menu's cursor relative to the menu.
        # xm, ym : coordinates of the moving_group relative to the menu.
        # Xc = xc - xm
        # Yc = yc - ym

        if self._selected_index == index or \
           index < 0 or \
           index > self.count - 1 or \
           self._moving_group_timeline.is_playing() or \
           self._cursor_timeline.is_playing():
            return

        # Start select/unselect animations on both items.
        self.items[self._selected_index].animate_out()
        self.items[index].animate_in()

        # Get the cursor's coordinate on the array.
        # /!\ Those coordinates are NOT pixels but refer to the array of items.
        (Xc, Yc) = self._index_to_xy(index)

        xm = self._moving_group_x
        ym = self._moving_group_y

        xc = Xc + xm
        yc = Yc + ym

        # If the targeted cursor's position is on the last visible column then
        # the moving_group is translated by -1 on the x axis and the translation
        # of the cursor is reduce by 1 to stay on the column before the last
        # one. This is not done if the last column has been selected.
        if xc == self.visible_cols - 1 and \
            xm > self.visible_cols -self.items_per_row:
            xc -= 1
            xm -= 1

        # If the targeted cursor's position is on the first visible column then
        # the moving_group is translated by +1 on the x axis and the translation
        # of the cursor is raised by 1 to stay on the column after the first
        # one. This is not done if the first column has been selected.
        if xc == 0 and xm < 0:
            xc += 1
            xm += 1

        # If the targeted cursor's position is on the last visible row then
        # the moving_group is translated by -1 on the y axis and the translation
        # of the cursor is reduce by 1 to stay on the row before the last
        # one. This is not done if the last row has been selected.
        if yc == self.visible_rows - 1 and \
            ym > self.visible_rows -self.items_per_col:
            yc -= 1
            ym -= 1

        # If the targeted cursor's position is on the first visible row then
        # the moving_group is translated by +1 on the y axis and the translation
        # of the cursor is raised by 1 to stay on the row after the first
        # one. This is not done if the last row has been selected.
        if yc == 0 and ym < 0:
            yc += 1
            ym += 1

        if duration is None:
            duration = self.motion_duration

        self._move_cursor(xc, yc, duration)
        self._move_moving_group(xm, ym, duration)
        self._selected_index = index

        self.emit('moved')

    selected_index = property(_get_selected_index, _set_selected_index)

    def _get_visible_rows(self):
        """visible_rows property getter."""
        return self._visible_rows

    def _set_visible_rows(self, visible_rows):
        """visible_rows property setter."""
        self._visible_rows = visible_rows
        self._clip()

    visible_rows = property(_get_visible_rows, _set_visible_rows)

    def _get_visible_cols(self):
        """visible_cols property getter."""
        return self._visible_cols

    def _set_visible_cols(self, visible_cols):
        """visible_cols property setter."""
        self._visible_cols = visible_cols
        self._clip()

    visible_cols = property(_get_visible_cols, _set_visible_cols)

    def _get_cursor(self):
        """cursor property getter."""
        return self._cursor

    def _set_cursor(self, cursor):
        """cursor property setter."""
        if self._cursor is not None:
            self.remove(self._cursor)

        self._cursor = cursor

        if self._cursor is not None:
            self.add(self._cursor)
            if self._active:
                self._cursor.show()
            else:
                self._cursor.hide()

            if self.cursor_below:
                self._cursor.lower_bottom()
            else:
                self._cursor.raise_top()

            self._cursor.set_size(int(self._item_width_abs),
                int(self._item_height_abs))
            self._cursor.set_anchor_point(self._dx, self._dy)
            self._cursor.set_position(self._dx, self._dy)

            self._cursor_behaviour.apply(self._cursor)

    cursor = property(_get_cursor, _set_cursor)

    def _clip(self):
        """Updates the clipping region."""
        self.set_clip(0, 0, self._visible_cols * self._item_width_abs,
            self._visible_rows * self._item_height_abs)

        self._event_rect.set_size(self._visible_cols * self._item_width_abs,
            self._visible_rows * self._item_height_abs)

    def stop_animation(self):
        """Stops the timelines driving menu animation."""
        self._moving_group_timeline.stop()
        self._cursor_timeline.stop()

    def raw_add_item(self, item):
        """A method to add an item in the menu."""
        self._moving_group.add(item)
        self.items.append(item)

        (x, y) = self._index_to_xy(self.count - 1)

        item.move_anchor_point(self._dx, self._dy)
        item.set_position(x * self._item_width_abs + self._dx,
            y * self._item_height_abs + self._dy)

        if self._is_vertical:
            self.items_per_col = y + 1
        else:
            self.items_per_row = x + 1

        if self.cursor_below:
            item.raise_top()
        else:
            item.lower_bottom()

    def _index_to_xy(self, index):
        """Return the coordinates of an element associated to its index."""
        if self._is_vertical:
            r = index / float(self.items_per_row)
            y = int(math.modf(r)[1])
            x = int(index - y * self.items_per_row)
        else:
            r = index / float(self.items_per_col)
            x = int(math.modf(r)[1])
            y = int(index - x * self.items_per_col)

        return (x, y)

    def _move_moving_group(self, x, y, duration):
        """Moves the moving_group to x, y coordinates."""
        if (x, y) == (self._moving_group_x, self._moving_group_y):
            return

        path = clutter.Path()
        path.add_move_to(
            self._moving_group_x * self._item_width_abs,
            self._moving_group_y * self._item_height_abs)
        path.add_line_to(
            x * self._item_width_abs,
            y * self._item_height_abs)
        self._moving_group_behaviour.set_path(path)

        self._moving_group_x, self._moving_group_y = x, y
        self._moving_group_timeline.set_duration(duration)
        self._moving_group_timeline.start()

    def _move_cursor(self, x, y, duration):
        """
        Moves the cursor to x, y coordinates.
        The motion is applied to the center of the cursor.
        """
        if (x, y) == (self._cursor_x, self._cursor_y):
            return

        path = clutter.Path()
        path.add_move_to(
            self._cursor_x * self._item_width_abs + self._dx,
            self._cursor_y * self._item_height_abs + self._dy)
        path.add_line_to(
            x * self._item_width_abs + self._dx,
            y * self._item_height_abs + self._dy)
        self._cursor_behaviour.set_path(path)

        self._cursor_x, self._cursor_y = x, y
        self._cursor_timeline.set_duration(duration)
        self._cursor_timeline.start()

    def up(self):
        """Move the menu's cursor up changing the selected_index property."""
        if not self.on_top:
            if self._is_vertical:
                self.selected_index -= self.items_per_row
            else:
                self.selected_index -= 1

    def down(self):
        """Move the menu's cursor down changing the selected_index property."""
        if not self.on_bottom:
            if self._is_vertical:
                self.selected_index += self.items_per_row
            else:
                self.selected_index += 1

    def right(self):
        """Move the menu's cursor right changing the selected_index property."""
        if not self.on_right:
            if self._is_vertical:
                self.selected_index += 1
            else:
                self.selected_index += self.items_per_col

    def left(self):
        """Move the menu's cursor left changing the selected_index property."""
        if not self.on_left:
            if self._is_vertical:
                self.selected_index -= 1
            else:
                self.selected_index -= self.items_per_col

    def _internal_timer_callback(self):
        """
        This callback is used to move the cursor if the SEEK mode is activated.
        """
        if self._event_mode == self.MODE_SEEK:
            if self._seek_step_x == 1:
                self.right()
            if self._seek_step_x == -1:
                self.left()
            if self._seek_step_y == 1:
                self.down()
            if self._seek_step_y == -1:
                self.up()

        return True

    def _on_button_press_event(self, actor, event):
        """button-press-event handler."""
        clutter.grab_pointer(self._event_rect)
        if not self._event_rect.handler_is_connected(self._motion_handler):
            self._motion_handler = self._event_rect.connect('motion-event',
                self._on_motion_event)

        (x_menu, y_menu) = self.get_transformed_position()
        (x_moving_group, y_moving_group) = self._moving_group.get_position()

        # Events coordinates are relative to the stage.
        # So they need to be computed relatively to the moving group.
        x = event.x - x_menu - x_moving_group
        y = event.y - y_menu - y_moving_group

        x_grid = int(x / self._item_width_abs)
        y_grid = int(y / self._item_height_abs)

        if self._is_vertical:
            new_index = y_grid * self.items_per_row + x_grid
        else:
            new_index = x_grid * self.items_per_col + y_grid

        (delta_x, delta_y) = self._index_to_xy(self._selected_index)

        delta_x -= x_grid
        delta_y -= y_grid

        # Correction factor due to the fact that items are not necessary square,
        # but most probably rectangles. So the distance in the grid coordinates
        # must be corrected by a factor to have a real distance in pixels on the
        # screen.
        correction = float(self._item_width_abs) / float(self._item_height_abs)
        correction *= correction
        distance = math.sqrt(delta_x ** 2 * correction + delta_y ** 2)

        # Computation of the duration of animations, scaling grid steps to ms.
        duration = int(distance * 50)

        if self.selected_index == new_index and \
            self.active and \
            not self._cursor_timeline.is_playing() and \
            not self._moving_group_timeline.is_playing():
            self._event_mode = self.MODE_SELECT
        else:
            self.active = True
            self._event_mode = self.MODE_NONE

        self._set_selected_index(new_index, duration)

        self._motion_buffer.start(event)

        return False

    def _on_button_release_event(self, actor, event):
        """button-release-event handler."""
        clutter.ungrab_pointer()
        if self._event_rect.handler_is_connected(self._motion_handler):
            self._event_rect.disconnect_by_func(self._on_motion_event)

        if self._event_mode == self.MODE_SELECT:
            self.emit('selected')

        self._event_mode = self.MODE_NONE

        return True

    def _on_motion_event(self, actor, event):
        """motion-event handler"""
        # threshold in pixels = the minimum distance we have to move before we
        # consider a motion has started
        motion_threshold = 20

        self._seek_step_x = 0
        self._seek_step_y = 0
        self._motion_buffer.compute_from_start(event)
        self._motion_buffer.compute_from_last_motion_event(event)

        if self._motion_buffer.distance_from_start > motion_threshold:
            self._event_mode = self.MODE_SEEK
            self._motion_buffer.take_new_motion_event(event)
            dx = self._motion_buffer.dx_from_last_motion_event
            dy = self._motion_buffer.dy_from_last_motion_event

            if math.fabs(dx) > math.fabs(dy):
                self._seek_step_x = dx > 0 and 1 or -1
            else:
                self._seek_step_y = dy > 0 and 1 or -1

        return False

    def _on_scroll_event(self, actor, event):
        """scroll-event handler (mouse's wheel)."""
        if not self.active:
            self.active = True
            return

        if event.direction == clutter.SCROLL_DOWN:
            self.down()
        else:
            self.up()

        return False

