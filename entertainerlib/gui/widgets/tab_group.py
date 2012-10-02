# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''TabGroup is a group of tabs. It draws the tab bar.'''

import clutter
import gobject
import pango

from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.user_event import UserEvent


class TabGroup(Base, clutter.Group):
    '''
    This is a top level container for tabs.

    This widget contains graphics for tab bar, but content of the tabs are
    separated into Tab objects.
    '''
    __gsignals__ = {
        'activated' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        }

    def __init__(self, width, height, color):
        Base.__init__(self)
        clutter.Group.__init__(self)

        self._active = None

        # Size
        self.stage_w = self.config.stage_width
        self.stage_h = self.config.stage_height
        self.width_factor = width
        self.height_factor = height

        # Label text colors
        self.color = color
        self.selected_color = self.config.theme.get_color(color)
        self.unselected_color = (self.selected_color[0],
            self.selected_color[1], self.selected_color[2], 96)

        # Size of the tab bar (This includes label texts)
        self.rect = clutter.Rectangle()
        self.rect.set_size(
            int(self.stage_w * self.width_factor),
            int(self.stage_h * self.height_factor))
        self.rect.set_color(clutter.Color(255, 0, 0, 0))
        self.add(self.rect)

        # Tab object dictionary that stores tab names as the keys.
        self._tabs = {}

        # Tab objects will be held in this list but should only be used for
        # internal calculations in the TabGroup class
        self.tabs_list = []

        self.labels = []
        self.timelines = [] # Contains tuples (timeline, alpha, behaviour)
        self.current_tab = None

    def tab(self, name):
        '''Return the given tab that matches the provided name.'''
        return self._tabs[name]

    def __len__(self):
        '''Get TagGroup length.'''
        return len(self.tabs_list)

    def _get_active(self):
        '''active property getter.'''
        if self._active == None:
            self._active = False
        return self._active

    def _set_active(self, boolean):
        '''active property setter.'''
        if self._active == boolean:
            return

        self._active = boolean

        if boolean:
            self.emit('activated')
            self.set_opacity(255)
            if self.current_tab != None:
                self.tabs_list[self.current_tab].active = False
        else:
            self.set_opacity(128)

    active = property(_get_active, _set_active)

    def add_tab(self, tab):
        '''Add new tab to this tab group.'''
        # Add to the dictionary so that the tab can be called by name
        self._tabs[tab.name] = tab

        self.tabs_list.append(tab)

        tab.active = False

        # Set first tab visible
        if self.current_tab == None:
            self.current_tab = 0
            self.tabs_list[0].visible = True

        tab_title = Label(0.01, self.color, 0, 0, tab.title)
        self.labels.append(tab_title)
        tab_title.set_name(tab.name)

        self.add(tab_title)
        self._reposition_labels()

        tab_title.set_reactive(True)
        tab_title.connect('button-press-event', self._on_tab_title_button_press)

        timeline = clutter.Timeline(500)
        alpha = clutter.Alpha(timeline, clutter.EASE_IN_OUT_SINE)
        behaviour = clutter.BehaviourOpacity(255, 96, alpha)
        behaviour.apply(tab_title)
        self.timelines.append((timeline, alpha, behaviour))

    def _reposition_labels(self):
        '''
        This is called every time we need to calculate new positions to the
        labels.

        This is when we add or remove tabs from this TabGroup. This method
        calculates label positions and sizes and updates UI accordingly
        '''
        self.font_size = self.get_height() * 0.3
        count = len(self.labels)
        width = int(self.stage_w * self.width_factor)

        for i, label in enumerate(self.labels):
            if i != self.current_tab:
                label.set_color(self.unselected_color)
            label.set_font_name("Sans " + str(self.font_size) + "px")
            label.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            label.set_y(int(self.get_height() / 2))
            label.set_x(
                (width / len(self.labels) * (i + 1)) - (width / count / 2))
            label.set_line_wrap(False)
            label.set_ellipsize(pango.ELLIPSIZE_END)

    def _activate_tab(self, new_tab):
        '''Activation of new selected Tab.'''
        # Fade out of the previously selected title label.
        self.timelines[self.current_tab][0].set_direction(
            clutter.TIMELINE_FORWARD)
        self.timelines[self.current_tab][0].start()

        # Fade in of the selected title label.
        self.timelines[new_tab][0].set_direction(clutter.TIMELINE_BACKWARD)
        self.timelines[new_tab][0].start()

        # Change visible tab
        self.tabs_list[self.current_tab].visible = False
        self.tabs_list[new_tab].visible = True

    def _switch_tab_to_left(self):
        '''Switch one tab to left or nothing if there is no tab.'''
        if self.current_tab > 0 and self.current_tab is not None:
            self._activate_tab(self.current_tab - 1)
            self.current_tab = self.current_tab - 1

    def _switch_tab_to_right(self):
        '''Switch one tab to right or nothing if there is no tab.'''
        if self.current_tab < len(self.tabs_list) - 1 and (
            self.current_tab is not None):
            self._activate_tab(self.current_tab + 1)
            self.current_tab = self.current_tab + 1

    def _switch_tab_to_down(self):
        '''Switch down from current tab if allowed.'''
        if self.tabs_list[self.current_tab].can_activate():
            self.active = False
            self.tabs_list[self.current_tab].active = True

    def handle_user_event(self, event):
        '''Handle screen specific user events.'''
        if self.active:
            event_type = event.get_type()
            if event_type == UserEvent.NAVIGATE_LEFT:
                self._switch_tab_to_left()
            elif event_type == UserEvent.NAVIGATE_RIGHT:
                self._switch_tab_to_right()
            elif event_type == UserEvent.NAVIGATE_DOWN:
                self._switch_tab_to_down()
        else:
            result = self.tabs_list[self.current_tab].handle_user_event(event)
            if result:
                self.active = True
                self.tabs_list[self.current_tab].active = False

    def _on_tab_title_button_press(self, actor, event):
        '''Title Label button-press handler.'''
        self.active = True

        clicked_tab = self._tabs[actor.get_name()]
        clicked_tab_index = self.tabs_list.index(clicked_tab)

        if self.current_tab != clicked_tab_index:
            self._activate_tab(clicked_tab_index)
            self.current_tab = clicked_tab_index

