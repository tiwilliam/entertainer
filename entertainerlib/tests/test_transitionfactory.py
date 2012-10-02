# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests TransitionFactory'''
# pylint: disable-msg=W0212

from entertainerlib.gui.transitions.factory import TransitionFactory
from entertainerlib.gui.transitions.fade import Fade
from entertainerlib.gui.transitions.no_effect import NoEffect
from entertainerlib.gui.transitions.slide import Slide
from entertainerlib.gui.transitions.zoom_and_fade import ZoomAndFade
from entertainerlib.tests import EntertainerTest


class TransitionFactoryTest(EntertainerTest):
    '''Test for entertainerlib.gui.transitions.factory'''

    def setUp(self):
        '''Set up the test'''
        EntertainerTest.setUp(self)

        # Not testing the callback because it is used by the transitions only
        # so just provide None
        self.factory = TransitionFactory(None)

    def tearDown(self):
        '''Clean up after the test'''
        EntertainerTest.tearDown(self)

    def test_create(self):
        '''Test correct TransitionFactory initialization'''
        self.assertTrue(isinstance(self.factory, TransitionFactory))

    def test__generate_slide(self):
        '''Test _generate_slide returns a Slide transition'''
        transition = self.factory._generate_slide()
        self.assertTrue(isinstance(transition, Slide))

    def test__generate_no_effect(self):
        '''Test _generate_no_effect returns a NoEffect transition'''
        transition = self.factory._generate_no_effect()
        self.assertTrue(isinstance(transition, NoEffect))

    def test__generate_fade(self):
        '''Test _generate_fade returns a Fade transition'''
        transition = self.factory._generate_fade()
        self.assertTrue(isinstance(transition, Fade))

    def test__generate_zoom_and_fade(self):
        '''Test _generate_zoom_and_fade returns a ZoomAndFade transition'''
        transition = self.factory._generate_zoom_and_fade()
        self.assertTrue(isinstance(transition, ZoomAndFade))

    def test_generate_transition(self):
        '''Test that generate_transition returns all the proper types'''
        values_to_test = {
            'Crossfade' : Fade,
            'No effect' : NoEffect,
            'Slide' : Slide,
            'Zoom and fade' : ZoomAndFade
        }
        # Test all possible transitions
        for key in values_to_test.keys():
            self.config.write_content_value('General', 'transition_effect',
                key)
            self.config.update_configuration()
            transition = self.factory.generate_transition()
            self.assertTrue(isinstance(transition, values_to_test[key]))

        # Test the path when the user doesn't have effects
        self.config.write_content_value('General', 'show_effects', 'False')
        self.config.update_configuration()
        transition = self.factory.generate_transition()
        self.assertTrue(isinstance(transition, NoEffect))

