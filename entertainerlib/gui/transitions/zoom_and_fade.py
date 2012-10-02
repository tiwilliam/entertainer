# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''ZoomAndFade - Transition to zoom and fade between screens'''

import clutter
from entertainerlib.gui.transitions.transition import Transition


class ZoomAndFade(Transition):
    """
    ZoomAndFade

    Fade out all components from the "from_screen" and fade in all components
    of the "to_screen". This class implements simple crossfade effect for
    screen changes.
    """

    def __init__(self, remove_from_stage_callback):
        Transition.__init__(self, remove_from_stage_callback)
        self.out_fade = None
        self.out_zoom = None
        self.in_behaviour = None
        self.in_zoom = None

    def forward_effect(self, from_screen, to_screen):
        """
        Fade+zoom out all components from the "from_screen" and fade+zoom in
        all components of the "to_screen".
        @param from_screen: Screen object (Currently displayed screen)
        @param to_screen: Screen object (Screen displayed after transition)
        """
        # Initialize to_screen for animation
        to_screen.set_opacity(0)
        to_screen.show()

        # Fade out current screen
        if from_screen is not None:
            fade_out = clutter.Timeline(22, 85)
            alpha_out = clutter.Alpha(fade_out, clutter.smoothstep_inc_func)
            self.out_fade = clutter.BehaviourOpacity(255, 0, alpha_out)
            self.out_fade.apply(from_screen)
            #from_screen.set_anchor_point_from_gravity(
            #                                       clutter.GRAVITY_CENTER)
            self.out_zoom = clutter.BehaviourScale(1.0, 1.0, 1.2, 1.2,
                                                    alpha_out)
            #from_screen.set_anchor_point(0,0)
            self.out_zoom.apply(from_screen)

        # Fade in timeline
        fade_in = clutter.Timeline(22, 85)
        alpha_in = clutter.Alpha(fade_in, clutter.smoothstep_inc_func)
        self.in_behaviour = clutter.BehaviourOpacity(0, 255, alpha_in)
        self.in_behaviour.apply(to_screen)
        #to_screen.set_anchor_point_from_gravity(
        #                                           clutter.GRAVITY_CENTER)
        self.in_zoom = clutter.BehaviourScale(0.8, 0.8, 1.0, 1.0, alpha_in)
        #to_screen.set_anchor_point(0,0)
        self.in_zoom.apply(to_screen)

        # Start transition animation
        if from_screen is not None:
            fade_out.start()
        fade_in.start()

    def backward_effect(self, from_screen, to_screen):
        """ 
        Do the same as forward_effect, but zoom backwards. This gives an
        illusion of going back.
        @param from_screen: Screen object (Currently displayed screen)
        @param to_screen: Screen object (Screen displayed after transition)
        """
        # Initialize to_screen for animation
        to_screen.set_opacity(0x00)
        to_screen.show()

        # Fade out current screen
        fade_out = clutter.Timeline(22, 85)
        alpha_out = clutter.Alpha(fade_out, clutter.smoothstep_inc_func)
        self.out_fade = clutter.BehaviourOpacity(255, 0, alpha_out)
        self.out_fade.apply(from_screen)
        #from_screen.set_anchor_point_from_gravity(
        #                                           clutter.GRAVITY_CENTER)
        self.out_zoom = clutter.BehaviourScale(1.0, 1.0, 0.8, 0.8, alpha_out)
        self.out_zoom.apply(from_screen)
        fade_out.connect('completed', self._remove_from_stage_callback,
                                                    from_screen)

        # Fade in timeline
        fade_in = clutter.Timeline(22, 85)
        alpha_in = clutter.Alpha(fade_in, clutter.smoothstep_inc_func)
        self.in_behaviour = clutter.BehaviourOpacity(0, 255, alpha_in)
        self.in_behaviour.apply(to_screen)
        #to_screen.set_anchor_point_from_gravity(
        #                                           clutter.GRAVITY_CENTER)
        self.in_zoom = clutter.BehaviourScale(1.2, 1.2, 1.0, 1.0, alpha_in)
        self.in_zoom.apply(to_screen)

        # Start transition animation
        if from_screen is not None:
            fade_out.start()
        fade_in.start()

