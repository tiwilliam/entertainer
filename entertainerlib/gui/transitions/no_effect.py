# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''NoEffect - Simple change transition from screen 1 to screen 2'''

from entertainerlib.gui.transitions.transition import Transition


class NoEffect(Transition):
    """
    NoEffect

    This is the most simple transition. It simply changes view from screen 1
    to screen 2 without any special effects.
    """

    def __init__(self, remove_from_stage_callback):
        Transition.__init__(self, remove_from_stage_callback)

    def forward_effect(self, from_screen, to_screen):
        """
        Change screen without effects. 'from_screen' is None when app starts up.
        @param from_screen: Screen object (Currently displayed screen)
        @param to_screen: Screen object (Screen displayed after transition)
        """
        if from_screen is not None:
            from_screen.hide()
        to_screen.show()

    def backward_effect(self, from_screen, to_screen):
        """
        Change to the previous screen.
        @param from_screen: Screen object (Currently displayed screen)
        @param to_screen: Screen object (Screen displayed after transition)
        """
        if from_screen is not None:
            from_screen.hide()
            self.remove_from_stage_callback(from_screen)
        to_screen.show()

