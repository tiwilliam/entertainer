# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Menu widget that contains text items'''

import math

import clutter
import gobject

from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.motion_buffer import MotionBuffer
from entertainerlib.gui.widgets.special_behaviours import \
    LoopedPathBehaviour

class ScrollMenuItem(clutter.Group):
    """A Group containing a Label to which a LoopedPathBehaviour is applied."""
    __gtype_name__ = 'ScrollMenuItem'

    def __init__(self, alpha, text, item_height, font_size, color_name):
        clutter.Group.__init__(self)

        self.label = Label(font_size, color_name, 0, 0)
        self.label.set_text(text)

        self.behaviour = LoopedPathBehaviour(alpha)
        self.behaviour.apply(self)

        self.add(self.label)

class ScrollMenu(clutter.Group, object):
    """Menu widget that contains text items."""
    __gtype_name__ = 'ScrollMenu'
    __gsignals__ = {
        'activated' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'selected' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'moved' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        }

    MODE_SELECTION = 0
    MODE_MOTION = 1
    MODE_STOP = 2

    def __init__(self, item_gap, item_height, font_size, color_name):
        clutter.Group.__init__(self)
        self._motion_buffer = MotionBuffer()
        self._items = []
        self._item_gap = item_gap
        self._item_height = item_height
        self._item_font_size = font_size
        self._item_color_name = color_name
        self._selected_index = 1
        self._visible_items = 5
        self._event_mode = -1
        self._animation_progression = 0
        self._animation_start_index = 1
        self._animation_end_index = 1
        self._active = False
        self._motion_handler = 0

        self._timeline = clutter.Timeline(300)
        self._alpha = clutter.Alpha(self._timeline, clutter.EASE_IN_OUT_SINE)

        # preparation to pointer events handling
        self.set_reactive(True)
        self.connect('scroll-event', self._on_scroll_event)
        self.connect('button-press-event', self._on_button_press_event)
        self.connect('button-release-event', self._on_button_release_event)

    def refresh(self):
        """Refresh the menu: clip area dimensions and items positions"""
        self._set_selected_index(self._selected_index, 1)
        self._set_visible_items(self._visible_items)

    def add_item(self, text, name):
        """Creation of a new MenuItem and addition to the ScrollMenu"""
        item = ScrollMenuItem(self._alpha, text, self._item_height,
            self._item_font_size, self._item_color_name)

        item.set_name(name)
        item.connect('notify::y', self._update_item_opacity)
        self.add(item)

        self._items.append(item)
        self._update_item_opacity(item)

    def remove_item(self, name):
        """Remove an item from the menu"""
        index = self.get_index(name)

        if index != -1:
            # if item was found, we remove it from the item list, from the
            # group and finally we delete it.
            item = self._items[index]
            self._items.remove(item)
            self.remove(item)
            del item

    def _get_active(self):
        """Active property getter"""
        return self._active

    def _set_active(self, boolean):
        """Active property setter"""
        if self._active == boolean:
            return

        self._active = boolean
        if boolean:
            self.set_opacity(255)
            self.emit('activated')
        else:
            self.set_opacity(128)

    active = property(_get_active, _set_active)

    def stop_animation(self):
        '''Stops the timeline driving menu animation.'''
        self._timeline.stop()

    def _update_behaviours(self, target):
        """Preparation of behaviours applied to menu items before animation"""
        items_len = len(self._items)
        step = 1.0 / items_len
        step_pix = self._item_gap + self._item_height
        middle_index = int(self._visible_items / 2) + 1

        for x, item in enumerate(self._items):
            item.behaviour.start_index = (x + middle_index - \
                self._selected_index) * step
            item.behaviour.end_index = (x + middle_index - target) * step

            item.behaviour.start_knot = (0.0, -step_pix)
            item.behaviour.end_knot = (0.0, (items_len - 1.0) * step_pix)

    def _display_items_at_target(self, target):
        """Menu is displayed for a particular targeted index value"""
        step = 1.0 / len(self._items)
        middle_index = int(self._visible_items / 2) + 1

        for x, item in enumerate(self._items):
            raw_index = (x + middle_index - target) * step

            if raw_index >= 0 :
                index = math.modf(raw_index)[0]
            else:
                index = 1 + math.modf(raw_index)[0]

            # Calculation of new coordinates
            xx = index * (item.behaviour.end_knot[0] - \
                item.behaviour.start_knot[0]) + item.behaviour.start_knot[0]
            yy = index * (item.behaviour.end_knot[1] - \
                item.behaviour.start_knot[1]) + item.behaviour.start_knot[1]

            item.set_position(int(xx), int(yy))

    def _get_visible_items(self):
        """visible_items property getter"""
        return self._visible_items

    def _set_visible_items(self, visible_items):
        """visible_items property setter"""
        self._visible_items = visible_items
        height = visible_items * self._item_height + (visible_items - 1) * \
            self._item_gap
        self.set_clip(0, 0, self.get_width(), height)

    visible_items = property(_get_visible_items, _set_visible_items)

    def _get_selected_index(self):
        """selected_index property getter"""
        return self._selected_index

    def _set_selected_index(self, selected_index, duration=300):
        """selected_index property setter"""
        if not self._timeline.is_playing():
            items_len = len(self._items)
            self._update_behaviours(selected_index)

            # those 2 variables are used if we want to stop the timeline
            # we use them + timeline progression to calculate the current index
            # when (if) we stop
            self._animation_start_index = self._selected_index
            self._animation_end_index = selected_index

            # selected_index can be any desired value but in the end,
            # we have to rescale it to be between 0 and (items_len-1)
            if selected_index >= 0:
                self._selected_index = selected_index - \
                    math.modf(selected_index / items_len)[1] * items_len
            else:
                self._selected_index = selected_index + \
                    (math.modf(-(selected_index + 1) / items_len)[1] + 1) * \
                    items_len

            self._timeline.set_duration(duration)
            self._timeline.start()

            self.emit('moved')

    selected_index = property(_get_selected_index, _set_selected_index)

    def get_selected(self):
        """Get currently selected menuitem"""
        return self._items[int(self._selected_index)]

    def get_index(self, text):
        """Returns index of label with the text as passed or -1 if not found"""
        for item in self._items:
            if item.get_name() == text:
                return self._items.index(item)
        return -1

    def scroll_by(self, step, duration=300):
        """Generic scroll of menu items"""
        self._set_selected_index(self._selected_index + step, duration)

    def scroll_up(self, duration=300):
        """All menu items are scrolled up"""
        self.scroll_by(-1, duration)

    def scroll_down(self, duration=300):
        """All menu items are scrolled down"""
        self.scroll_by(1, duration)

    def get_opacity_for_y(self, y):
        """Calculation of actor's opacity as a function of its y coordinates"""
        opacity_first_item = 40
        opacity_selected_item = 255
        middle = int(self._visible_items / 2)

        y_medium_item = middle * (self._item_height + self._item_gap)
        a  = float(opacity_selected_item - opacity_first_item)
        a /= float(y_medium_item)

        if y <= y_medium_item :
            opacity = y * a + opacity_first_item
        else :
            opacity = opacity_selected_item * 2 - opacity_first_item - a * y

        if opacity < 0:
            opacity = 0

        return int(opacity)

    def _update_item_opacity(self, item, stage=None):
        """Set opacity to actors when they are moving. Opacity is f(y)"""
        opacity = self.get_opacity_for_y(item.get_y())
        item.set_opacity(opacity)

    def _on_button_press_event(self, actor, event):
        """button-press-event handler"""
        clutter.grab_pointer(self)
        if not self.handler_is_connected(self._motion_handler):
            self._motion_handler = self.connect('motion-event',
            self._on_motion_event)

        if self._timeline.is_playing():
            # before we stop the timeline, store its progression
            self._animation_progression = self._timeline.get_progress()

            # A click with an animation pending should stop the animation
            self._timeline.stop()

            # go to MODE_STOP to handle correctly next button-release event
            self._event_mode = self.MODE_STOP
        else:
            # no animation pending so we're going to do either a menu_item
            # selection or a menu motion. This will be decided later, right now
            # we just take a snapshot of this button-press-event as a start.
            self._motion_buffer.start(event)
            self._event_mode = self.MODE_SELECTION

        return False

    def _on_button_release_event(self, actor, event):
        """button-release-event handler"""
        items_len = len(self._items)

        clutter.ungrab_pointer()
        if self.handler_is_connected(self._motion_handler):
            self.disconnect_by_func(self._on_motion_event)
        self._motion_buffer.compute_from_last_motion_event(event)

        if not self.active:
            self.active = True
            return

        y = event.y - self.get_y()

        if self._event_mode == self.MODE_SELECTION:
            # if we are in MODE_SELECTION it means that we want to select
            # the menu item bellow the pointer

            for index, item in enumerate(self._items):
                item_y = item.get_y()
                item_h = item.get_height()
                if (y >= item_y) and (y <= (item_y + item_h)):
                    delta1 = index - self._selected_index
                    delta2 = index - self._selected_index + items_len
                    delta3 = index - self._selected_index - items_len

                    delta = 99999
                    for i in [delta1, delta2, delta3]:
                        if math.fabs(i) < math.fabs(delta):
                            delta = i

                    self.scroll_by(delta)

                    # if delta = 0 it means we've clicked on the selected item
                    if delta == 0:
                        self.emit('selected')

        elif self._event_mode == self.MODE_MOTION:
            speed = self._motion_buffer.speed_y_from_last_motion_event
            target = self._selected_index - \
                self._motion_buffer.dy_from_start / \
                self._items[0].behaviour.path_length * items_len

            new_index = int(target - 5 * speed)
            self._selected_index = target
            self._set_selected_index(new_index, 1000)

        else:
            # If we have stopped the pending animation. Now we have to do 
            # a small other one to select the closest menu-item
            current_index = self._animation_start_index + \
                (self._animation_end_index - self._animation_start_index) * \
                self._animation_progression
            self._selected_index = current_index
            target_index = int(current_index)
            self._set_selected_index(target_index, 1000)

        return False

    def _on_motion_event(self, actor, event):
        """motion-event handler"""
        # threshold in pixels = the minimum distance we have to move before we
        # consider a motion has started
        motion_threshold = 10

        self._motion_buffer.compute_from_start(event)
        if self._motion_buffer.distance_from_start > motion_threshold:
            self._motion_buffer.take_new_motion_event(event)
            self._event_mode = self.MODE_MOTION
            target = self._selected_index - \
                self._motion_buffer.dy_from_start / \
                self._items[0].behaviour.path_length * len(self._items)
            self._display_items_at_target(target)

        return False

    def _on_scroll_event(self, actor, event):
        """scroll-event handler (mouse's wheel)"""
        self.active = True

        if event.direction == clutter.SCROLL_DOWN:
            self.scroll_down(duration=150)
        else:
            self.scroll_up(duration=150)

        return False

