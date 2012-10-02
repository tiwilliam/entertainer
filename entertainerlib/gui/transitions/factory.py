# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''TransitionFactory - create a transition object based on the configuration
that is in the user's preferences'''

from entertainerlib.gui.transitions.fade import Fade
from entertainerlib.gui.transitions.no_effect import NoEffect
from entertainerlib.gui.transitions.slide import Slide
from entertainerlib.gui.transitions.zoom_and_fade import ZoomAndFade
from entertainerlib.configuration import Configuration


class TransitionFactory:
    '''Generates a transition object based on the configuration setting'''

    def __init__(self, remove_from_stage_callback):
        '''Initialize the factory

        The remove_from_stage_callback is a callback that all transition
        objects require to remove a "from_screen" from the stage
        without having direct access to the stage.
        '''
        self.remove_from_stage_callback = remove_from_stage_callback

        self.config = Configuration()

    def generate_transition(self):
        '''Generate the proper transition and return it'''
        generate_methods = {
            'Crossfade' : self._generate_fade,
            'No effect' : self._generate_no_effect,
            'Slide' : self._generate_slide,
            'Zoom and fade' : self._generate_zoom_and_fade
        }

        if self.config.show_effects:
            kind = self.config.transition_effect
        else:
            kind = "No effect"

        return generate_methods[kind]()

    def _generate_slide(self):
        '''Generate a Slide transition'''
        return Slide(self.remove_from_stage_callback)

    def _generate_no_effect(self):
        '''Generate a NoEffect transition'''
        return NoEffect(self.remove_from_stage_callback)

    def _generate_fade(self):
        '''Generate a Fade transition'''
        return Fade(self.remove_from_stage_callback)

    def _generate_zoom_and_fade(self):
        '''Generate a ZoomAndFade transition'''
        return ZoomAndFade(self.remove_from_stage_callback)

