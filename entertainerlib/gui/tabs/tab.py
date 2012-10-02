# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tab - Tab is group of objects that are displayed on one tab.'''

import clutter
import gobject

from entertainerlib.gui.user_event import UserEvent
from entertainerlib.gui.widgets.base import Base
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.texture import Texture

class Tab(Base, clutter.Group):
    '''
    Tab can be used as part of the TabGroup.

    Tab is a very simple container that contains all the widgets and logic
    of the tab page.
    '''
    __gsignals__ = {
        'activated' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        'deactivated' : ( gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, () ),
        }

    def __init__(self, name, title="Untitled tab", callback=None):
        Base.__init__(self)
        clutter.Group.__init__(self)

        self.name = name
        self.title = title
        self.callback = callback
        self.theme = self.config.theme

        self.dispatch = {
            UserEvent.NAVIGATE_UP : self._handle_up,
            UserEvent.NAVIGATE_DOWN : self._handle_down,
            UserEvent.NAVIGATE_LEFT : self._handle_left,
            UserEvent.NAVIGATE_RIGHT : self._handle_right,
            UserEvent.NAVIGATE_SELECT : self._handle_select,
        }

        # show/hide animation on the Tab
        self.timeline = clutter.Timeline(500)
        self.timeline.connect('completed', self._on_timeline_completed)
        self.alpha = clutter.Alpha(self.timeline, clutter.EASE_IN_OUT_SINE)
        self.behaviour = clutter.BehaviourOpacity(0, 255, self.alpha)
        self.behaviour.apply(self)

        # Tabs are created deactivated and invisible
        self._active = None
        self._visible = False
        self.set_opacity(0)
        self.hide()

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
        else:
            self.emit('deactivated')

    active = property(_get_active, _set_active)

    def _get_visible(self):
        '''visible property getter.'''
        return self._visible

    def _set_visible(self, boolean):
        '''visible property setter.'''
        if self._visible == boolean:
            return

        self._visible = boolean

        if boolean:
            self.show()
            self.timeline.set_direction(clutter.TIMELINE_FORWARD)
            self.timeline.rewind()
            self.timeline.start()
        else:
            self.timeline.set_direction(clutter.TIMELINE_BACKWARD)
            self.timeline.start()

    visible = property(_get_visible, _set_visible)

    def _on_timeline_completed(self, timeline):
        """Hides the Tab on the end of the fade out animation."""
        if timeline.get_direction() == clutter.TIMELINE_BACKWARD:
            self.hide()

    def can_activate(self):
        '''
        Returns a boolean whether or not this tab can be activated. If tab
        doesn't have any controlling widgets it shouldn't activate ever.
        Default value is False. Override this method when implementing a new
        tab and add logic if needed.
        '''
        return False

    def show_empty_tab_notice(self, title=_("Empty tab"),
            message_body=_("This tab doesn't contain any elements.")):
        '''
        Create an information box that is displayed if there is no widgets in
        this tab. This method should be called only from child class as needed.
        '''

        # Create warning icon
        info_icon = Texture(self.theme.getImage("warning_icon"), 0.28, 0.27)
        self.add(info_icon)

        # Create warning title
        info_title = Label(0.0625, "title", 0.33, 0.27, title)
        self.add(info_title)

        # Create warning help text
        info = Label(0.042, "menuitem_inactive", 0.28, 0.4, message_body)
        info.width = 0.57
        self.add(info)

    def _handle_up(self):
        '''Dummy method for unimplemented handlers in subclass.'''
        return False

    def _handle_down(self):
        '''Dummy method for unimplemented handlers in subclass.'''
        return False

    def _handle_left(self):
        '''Dummy method for unimplemented handlers in subclass.'''
        return False

    def _handle_right(self):
        '''Dummy method for unimplemented handlers in subclass.'''
        return False

    def _handle_select(self, event=None):
        '''Dummy method for unimplemented handlers in subclass.'''
        return False

    def handle_user_event(self, event):
        '''Dispatch specific user events to the appropriate method.'''
        try:
            handle_method = self.dispatch[event.get_type()]
        except KeyError:
            # Must not be in the dispatch table, keep focus by returning False
            return False

        return handle_method()

