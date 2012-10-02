# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Container that has scrollbars and allows content to be scrolled.'''

import clutter
import gobject

from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.list_indicator import ListIndicator
from entertainerlib.gui.widgets.motion_buffer import MotionBuffer
from entertainerlib.gui.widgets.special_behaviours import LoopedPathBehaviour

class ScrollArea(Base, clutter.Group):
    """Wrapper of a clutter Group that allows for scrolling. ScrollArea
    modifies the width of the content and it assumes that the content uses
    percent modification (read: not default clutter objects)."""
    __gsignals__ = {
        'activated' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'moving' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        }

    MODE_SELECTION = 0
    MODE_MOTION = 1
    MODE_STOP = 2
    STEP_SIZE_PERCENT = 0.04

    def __init__(self, x, y, width, height, content):
        Base.__init__(self)
        clutter.Group.__init__(self)

        self._motion_buffer = MotionBuffer()
        self._offset = 0        # Drives the content motion.
        self._offset_max = 0    # Maximum value of offset (equal on bottom).
        self._old_offset = 0    # Stores the old value of offset on motions.
        self._motion_handler = 0
        self._active = None

        self.step_size = self.get_abs_y(self.STEP_SIZE_PERCENT)

        # Allowed area for the widget's scrolling content.
        self.area_width = self.get_abs_x(width)
        self.area_height = self.get_abs_y(height)

        # Create content position indicator
        self.indicator = ListIndicator(3 * width / 4, height, 0.2, 0.045,
            ListIndicator.VERTICAL)
        self.indicator.hide_position()
        self.indicator.set_maximum(2)
        self.add(self.indicator)

        # A clipped Group to receive the content.
        self._fixed_group = clutter.Group()
        self._fixed_group.set_clip(0, 0, self.area_width, self.area_height)
        self.add(self._fixed_group)
        self.content = None

        self._motion_timeline = clutter.Timeline(500)
        self._motion_timeline.connect('completed',
            self._motion_timeline_callback, None)
        self._motion_alpha = clutter.Alpha(self._motion_timeline,
            clutter.EASE_OUT_SINE)
        self._motion_behaviour = LoopedPathBehaviour(self._motion_alpha)

        self.set_content(content)

        self.active = None

        # Preparation to pointer events handling.
        self.set_reactive(True)
        self.connect('button-press-event', self._on_button_press_event)
        self.connect('button-release-event', self._on_button_release_event)
        self.connect('scroll-event', self._on_scroll_event)

        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

    @property
    def on_top(self):
        """True if we're on top."""
        return self._offset == 0

    @property
    def on_bottom(self):
        """True if we're on bottom."""
        return self._offset == self._offset_max

    def _get_active(self):
        """Active property getter."""
        return self._active

    def _set_active(self, boolean):
        """Active property setter."""
        if self._active == boolean:
            return

        self._active = boolean
        if boolean:
            # Show indicator if there is need for scrolling.
            if self._offset_max >= 0:
                self.indicator.show()

            self.set_opacity(255)
            self.emit('activated')
        else:
            self.indicator.hide()
            self.set_opacity(128)

    active = property(_get_active, _set_active)

    def _get_offset(self):
        """Get current offset value."""
        return self._offset

    def _set_offset(self, integer):
        """Set current offset value."""
        if self._offset == integer:
            return

        self._offset = integer

        if self._offset < 0:
            self._offset = 0
        elif self._offset > self._offset_max:
            self._offset = self._offset_max

        self.content.set_position(0, - self._offset)

        # Indicator updates.
        if self.on_top:
            self.indicator.set_current(1)
        elif self.on_bottom:
            self.indicator.set_current(2)

    offset = property(_get_offset, _set_offset)

    def set_content(self, content):
        """Set content into scroll area."""
        if self.content is not None:
            self._fixed_group.remove(self.content)
            self._motion_behaviour.remove(self.content)

        self.content = content
        self._fixed_group.add(content)

        self._offset_max = self.content.get_height() - self.area_height

        self._motion_behaviour.apply(self.content)

    def stop_animation(self):
        """Stops the timeline driving animation."""
        self._motion_timeline.stop()

    def scroll_to_top(self):
        """Scroll content back to top."""
        self.offset = 0

    def scroll_to_bottom(self):
        """Scroll content as much as possible."""
        self.offset = self._offset_max

    def scroll_up(self):
        """Scroll up by one step size."""
        self.offset -= self.step_size

    def scroll_down(self):
        """Scroll down by one step size."""
        self.offset += self.step_size

    def scroll_page_up(self):
        """Scroll up by one page. Page is a scroll area height."""
        self.offset -= self.area_height

    def scroll_page_down(self):
        self.offset += self.area_height

    def _update_motion_behaviour(self, target):
        """Preparation of looped behaviour applied to the content."""
        self._motion_behaviour.start_knot = (0.0, -self.offset)
        self._motion_behaviour.end_knot = (0.0, -target)
        self._motion_behaviour.start_index = 0.0
        # Need to set the end index to 0.9999. Indeed the LoopedPathBehaviour
        # uses an index in [0, 1[. So index = 1 is equivalent to index = 0, the
        # Actor will the be placed on the start_knot.
        self._motion_behaviour.end_index = 0.9999

    def _on_button_press_event(self, actor, event):
        """button-press-event handler."""
        clutter.grab_pointer(self)
        if not self.handler_is_connected(self._motion_handler):
            self._motion_handler = self.connect('motion-event',
                self._on_motion_event)

        if self._motion_timeline.is_playing():
            # A click with an animation pending should stop the animation.
            self._motion_timeline.stop()

            # Go to MODE_STOP to handle correctly next button-release event.
            self._event_mode = self.MODE_STOP
            self.offset = -self.content.get_y()
        else:
            # No animation pending so we're going to do nothing or to move
            # all the content.
            self._old_offset = self.offset
            self._motion_buffer.start(event)
            self._event_mode = self.MODE_SELECTION

        return False

    def _on_button_release_event(self, actor, event):
        """button-release-event handler."""
        clutter.ungrab_pointer()
        if self.handler_is_connected(self._motion_handler):
            self.disconnect_by_func(self._on_motion_event)

        self._motion_buffer.compute_from_last_motion_event(event)

        if not self.active:
            self.active = True
            return

        if self._event_mode == self.MODE_MOTION:
            speed = self._motion_buffer.speed_y_from_last_motion_event

            # Calculation of the new target according to vertical speed.
            target = self.offset - speed * 200

            if target < 0:
                target = 0
            elif target > self._offset_max:
                target = self._offset_max

            self._update_motion_behaviour(target)
            self._motion_timeline.start()

        return False

    def _on_motion_event(self, actor, event):
        """motion-event handler."""
        # Minimum distance we to move before we consider a motion has started.
        motion_threshold = 10

        self._motion_buffer.compute_from_start(event)
        if self._motion_buffer.distance_from_start > motion_threshold:
            self._motion_buffer.take_new_motion_event(event)
            self._event_mode = self.MODE_MOTION
            self.offset = self._old_offset - self._motion_buffer.dy_from_start

        return False

    def _on_scroll_event(self, actor, event):
        """scroll-event handler (mouse's wheel)."""
        if not self.active:
            self.active = True
            return

        # Do not scroll if there is no need.
        if self._offset_max < 0:
            return False

        if event.direction == clutter.SCROLL_DOWN:
            self.scroll_down()
        else:
            self.scroll_up()

        self.emit('moving')

        return False

    def _motion_timeline_callback(self, timeline, screen):
        """Code executed when the animation is finished."""
        self.offset = -self.content.get_y()

