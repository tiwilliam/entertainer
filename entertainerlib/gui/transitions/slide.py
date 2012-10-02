# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Slide - Transition to slide out old screen and slide in the new screen'''

import clutter

from entertainerlib.gui.transitions.transition import Transition
from entertainerlib.configuration import Configuration

class Slide(Transition):
    '''Move screens on and off the stage through horizontal movements.'''

    def __init__(self, remove_from_stage_callback):
        Transition.__init__(self, remove_from_stage_callback)
        self.config = Configuration()
        self.out_behaviour = None
        self.in_behaviour = None

    def forward_effect(self, from_screen, to_screen):
        '''Slide from_screen and to_screen to the right.'''
        self._do_slide(from_screen, to_screen, direction=1, remove_screen=False)

    def backward_effect(self, from_screen, to_screen):
        '''Slide from_screen and to_screen to the left.'''
        self._do_slide(from_screen, to_screen, direction=-1, remove_screen=True)

    def _do_slide(self, from_screen, to_screen, direction, remove_screen):
        '''Execute the common sliding logic needed by each direction.

        Direction will set the sign of width to determine which way to slide.'''
        width = self.config.stage_width * direction

        # Initialize to_screen for animation
        to_screen.set_position(-width, 0)
        to_screen.show()

        # Slide out timeline
        if from_screen is not None:
            slide_out = clutter.Timeline(500)
            alpha_out = clutter.Alpha(slide_out, clutter.EASE_IN_OUT_SINE)
            out_path = clutter.Path()
            out_path.add_move_to(0, 0)
            out_path.add_line_to(width, 0)
            self.out_behaviour = clutter.BehaviourPath(alpha_out, out_path)
            self.out_behaviour.apply(from_screen)

            if remove_screen:
                slide_out.connect('completed', self._remove_from_stage_callback,
                    from_screen)

        # Slide in timeline
        slide_in = clutter.Timeline(500)
        alpha_in = clutter.Alpha(slide_in, clutter.EASE_IN_OUT_SINE)
        in_path = clutter.Path()
        in_path.add_move_to(-width, 0)
        in_path.add_line_to(0, 0)
        self.in_behaviour = clutter.BehaviourPath(alpha_in, in_path)
        self.in_behaviour.apply(to_screen)

        # Start transition animating
        if from_screen is not None:
            slide_out.start()
        slide_in.start()

