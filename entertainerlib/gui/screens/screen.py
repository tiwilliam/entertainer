# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Screen - Screen interface. All screens have to implement this interface!'''

from collections import defaultdict

import clutter

from entertainerlib.exceptions import ScreenException
from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.tab_group import TabGroup

class Screen(Base, clutter.Group):
    """
    Screen interface

    Screen represents a view. View includes all the widgets on the screen.
    There can be for example Photographs view, Music view, Feed view etc.
    """

    # Screen kind constants
    NORMAL = 0
    OSD = 1

    def __init__(self, name='', callback=None, has_tabs=False, kind=None):
        """
        You should never create a Screen object directly! This init is supposed
        to be called from child classes that inherit this class.
        """
        Base.__init__(self)
        clutter.Group.__init__(self)

        self.name = name
        self.callback = callback

        self.has_tabs = has_tabs
        if has_tabs:
            self.tab_group = TabGroup(0.95, 0.13, 'title')
            self.tab_group.set_y(self.get_abs_y(0.1))
            self.tab_group.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
            self.tab_group.set_x(self.get_abs_x(0.5))
            self.tab_group.active = True

            self.add(self.tab_group)

        if kind is None:
            self.kind = self.NORMAL
        else:
            self.kind = kind

        def handle_default():
            '''Return the default handler method.'''
            return self._handle_default

        self.event_handlers = defaultdict(handle_default, {
            UserEvent.NAVIGATE_UP : self._handle_up,
            UserEvent.NAVIGATE_DOWN : self._handle_down,
            UserEvent.NAVIGATE_LEFT : self._handle_left,
            UserEvent.NAVIGATE_RIGHT : self._handle_right,
            UserEvent.NAVIGATE_SELECT : self._handle_select
        })

        rect = clutter.Rectangle()
        rect.set_size(self.config.stage_width, self.config.stage_height)
        rect.hide()
        self.add(rect)

    def update(self, event=None):
        """
        Update screen widgets. This is called always when screen is poped from
        the screen history. Not all widgets need update. For performance
        reasons you should only update those widgets that might have been
        changed. For example main menu may or may not contain "Currently
        Playing" menuitem.
        """
        pass

    def is_interested_in_play_action(self):
        """
        See if screen wants to handle Play action itself. If inheriting screen
        wants to handle play action by user it should override this method to
        return True. This kind of behaviour is required, for exmaple, in music
        library. When user press Play action over certain album we want to play
        that album, not pause current playback.
        @return: boolean. True if screen wants to handle play action
        """
        return False

    def execute_play_action(self):
        """
        This function executes screen spesific play action. For example adds
        album to playlist and starts playback. This function should be
        overriden in inheriting class.
        """
        pass

    def _handle_up(self):
        '''Handle UserEvent.NAVIGATE_UP.'''
        pass

    def _handle_down(self):
        '''Handle UserEvent.NAVIGATE_DOWN.'''
        pass

    def _handle_left(self):
        '''Handle UserEvent.NAVIGATE_LEFT.'''
        pass

    def _handle_right(self):
        '''Handle UserEvent.NAVIGATE_RIGHT.'''
        pass

    def _handle_select(self, event=None):
        '''Handle UserEvent.NAVIGATE_SELECT.'''
        pass

    def _handle_default(self):
        '''Handle a user event that is not one of the handled screen events.'''
        pass

    def handle_user_event(self, event):
        '''Dispatch a user event to the proper handler method or to the tab
        group if this screen has tabs.'''
        if self.has_tabs:
            return self.tab_group.handle_user_event(event)

        kind = event.get_type()
        self.event_handlers[kind]()

    def add_tab(self, tab):
        '''Add a tab to a screen that is meant to hold tabs.'''
        if not self.has_tabs:
            raise ScreenException('This screen does not support tabs.')

        tab.tab_group = self.tab_group
        self.tab_group.add_tab(tab)
        # XXX: laymansterms - figure this out, why do we need to add directly
        # to the screen instead of the tab group, why is the positioning
        # messed up when these are commented out. This should be done in add_tab
        self.add(tab)

