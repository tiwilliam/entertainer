# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests MotionBuffer"""

from entertainerlib.gui.widgets.motion_buffer import MotionBuffer
from entertainerlib.tests import EntertainerTest
from entertainerlib.tests.mock import MockPointerEvent

class MotionBufferTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.motion_buffer"""

    def setUp(self):
        '''Set up the test.'''
        EntertainerTest.setUp(self)

        self.buffer = MotionBuffer()

    def tearDown(self):
        '''Clean up after the test.'''
        EntertainerTest.tearDown(self)

    def test_create(self):
        '''Test correct MotionBuffer initialization.'''
        self.assertTrue(isinstance(self.buffer, MotionBuffer))

    def test_computations_from_start(self):
        '''Test all values on a 3 events motion, computed from start.'''
        self.buffer.start(self._create_first_event())
        self.buffer.take_new_motion_event(self._create_second_event())
        self.buffer.compute_from_start(self._create_third_event())

        self.assertEqual(self.buffer.dt_from_start, 2)
        self.assertEqual(self.buffer.dx_from_start, 10)
        self.assertEqual(self.buffer.dy_from_start, 10)
        self.assertAlmostEqual(self.buffer.distance_from_start, 14.142135624)

    def test_computations_from_last_event(self):
        '''Test all values on a 3 events motion, computed from last event.'''
        self.buffer.start(self._create_first_event())
        self.buffer.take_new_motion_event(self._create_second_event())
        self.buffer.compute_from_last_motion_event(self._create_third_event())

        self.assertEqual(self.buffer.dt_from_last_motion_event, 1)
        self.assertEqual(self.buffer.dx_from_last_motion_event, 10)
        self.assertEqual(self.buffer.dy_from_last_motion_event, 0)
        self.assertEqual(self.buffer.distance_from_last_motion_event, 10.0)
        self.assertEqual(self.buffer.speed_x_from_last_motion_event, 10.0)
        self.assertEqual(self.buffer.speed_y_from_last_motion_event, 0.0)
        self.assertEqual(self.buffer.speed_from_last_motion_event, 10.0)
        self.assertAlmostEqual(self.buffer.dt_ema, 0.3333333333)
        self.assertAlmostEqual(self.buffer.dx_ema, 3.3333333333)
        self.assertAlmostEqual(self.buffer.dy_ema, 0.0)
        self.assertAlmostEqual(self.buffer.distance_ema, 3.3333333333)
        self.assertAlmostEqual(self.buffer.speed_x_ema, 3.3333333333)
        self.assertAlmostEqual(self.buffer.speed_y_ema, 0.0)
        self.assertAlmostEqual(self.buffer.speed_ema, 3.3333333333)

    def _create_first_event(self):
        '''Create a virtual pointer event.'''
        event = MockPointerEvent()
        event.x = 100
        event.y = 100
        event.time = 0
        return event

    def _create_second_event(self):
        '''Create a virtual pointer event.'''
        event = MockPointerEvent()
        event.x = 100
        event.y = 110
        event.time = 1
        return event

    def _create_third_event(self):
        '''Create a virtual pointer event.'''
        event = MockPointerEvent()
        event.x = 110
        event.y = 110
        event.time = 2
        return event

