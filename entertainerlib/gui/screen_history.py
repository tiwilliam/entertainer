# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Stack container for screen objects'''

from entertainerlib.configuration import Configuration

class ScreenHistory(object):
    '''ScreenHistory contains the latest screens in is a stack.'''

    def __init__(self, remove_from_stage_callback):
        self.config = Configuration()
        self.screens = []
        self.remove_from_stage_callback = remove_from_stage_callback

    def add_screen(self, screen):
        '''Push the provided screen onto the history stack.'''
        if len(self.screens) < self.config.history_size:
            self.screens.append(screen)
        else:
            self.remove_from_stage_callback(self.screens[0])
            del self.screens[0] # Drop the oldest screen from the history
            self.screens.append(screen)

    def get_screen(self):
        '''Get the latest screen and pop it from the stack.'''
        if len(self.screens) == 0:
            return None
        return self.screens.pop()

    @property
    def is_empty(self):
        '''Return a boolean indicating if the screen history is empty.'''
        if len(self.screens) == 0:
            return True
        else:
            return False

