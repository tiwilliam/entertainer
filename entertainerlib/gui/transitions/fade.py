# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Fade - Transition to fade out old screen and fade in the new screen'''

import clutter
from entertainerlib.gui.transitions.transition import Transition


class Fade(Transition):
    """
    Fade

    Fade out all components from the "from_screen" and fade in all components
    of the "to_screen". This class implements simple crossfade effect for
    screen changes.
    """

    def __init__(self, remove_from_stage_callback):
        Transition.__init__(self, remove_from_stage_callback)
        self.out_behaviour = None
        self.in_behaviour = None

    def forward_effect(self, from_screen, to_screen):
        """
        Fade out all components from the "from_screen" and fade in all
        components of the "to_screen".
        @param from_screen: Screen object (Currently displayed screen)
        @param to_screen: Screen object (Screen displayed after transition)
        """
        # Initialize to_screen for animation
        to_screen.set_opacity(0x00)
        to_screen.show()

        # Fade out current screen
        if from_screen is not None:
            fade_out = clutter.Timeline(20, 60)
            alpha_out = clutter.Alpha(fade_out, clutter.smoothstep_inc_func)
            self.out_behaviour = clutter.BehaviourOpacity(0xff, 0x00, alpha_out)
            self.out_behaviour.apply(from_screen)

            if self.direction == self.BACKWARD:
                self.direction = self.FORWARD # Reset value
                fade_out.connect('completed', self._remove_from_stage_callback,
                    from_screen)

        # Fade in timeline
        fade_in = clutter.Timeline(20, 60)
        alpha_in = clutter.Alpha(fade_in, clutter.smoothstep_inc_func)
        self.in_behaviour = clutter.BehaviourOpacity(0x00, 0xff, alpha_in)
        self.in_behaviour.apply(to_screen)

        # Start transition animation
        if from_screen is not None:
            fade_out.start()
        fade_in.start()

    def backward_effect(self, from_screen, to_screen):
        """
        Fade out all components from the "from_screen" and fade in all
        components of the "to_screen".
        @param from_screen: Screen object (Currently displayed screen)
        @param to_screen: Screen object (Screen displayed after transition)
        """
        self.direction = self.BACKWARD
        # Same effect. Direction doesn't make any difference
        self.forward_effect(from_screen, to_screen)

