# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tools for pointer motion calculations"""

import math

class MotionBuffer(object):
    """
    Widgets with kinetic effect can use that Class to compute cursor's
    motion characteristics.

    NOTE :
    An exponential moving average of all characteristics is used as a
    numerical filter to avoid incoherent values.
    For more information : http://en.wikipedia.org/wiki/Moving_average
    '"""

    def __init__(self):
        self.dt_from_start = 0
        self.dx_from_start = 0
        self.dy_from_start = 0
        self.distance_from_start = 0

        self.dt_from_last_motion_event = 0
        self.dx_from_last_motion_event = 0
        self.dy_from_last_motion_event = 0
        self.distance_from_last_motion_event = 0
        self.speed_x_from_last_motion_event = 0
        self.speed_y_from_last_motion_event = 0
        self.speed_from_last_motion_event = 0

        self.dt_ema = 0
        self.dx_ema = 0
        self.dy_ema = 0
        self.distance_ema = 0
        self.speed_x_ema = 0
        self.speed_y_ema = 0
        self.speed_ema = 0

        self._start_x = 0
        self._start_y = 0
        self._start_time = 0

        self._last_motion_event_x = 0
        self._last_motion_event_y = 0
        self._last_motion_event_time = 0

        # Factors for exponential moving average calculation.
        self._rank = 5
        self._alpha = 2.0 / (self._rank + 1)
        self._beta = 1 - self._alpha

    def start(self, event):
        '''Buffer initialization.'''
        self._start_x = event.x
        self._start_y = event.y
        self._start_time = event.time

        self._last_motion_event_x = event.x
        self._last_motion_event_y = event.y
        self._last_motion_event_time = event.time

        self.dt_ema = 0
        self.dx_ema = 0
        self.dy_ema = 0
        self.distance_ema = 0
        self.speed_x_ema = 0
        self.speed_y_ema = 0
        self.speed_ema = 0

    def take_new_motion_event(self, event):
        '''To be called by every *motion-event* of an actor.'''
        self._last_motion_event_x = event.x
        self._last_motion_event_y = event.y
        self._last_motion_event_time = event.time

    def compute_from_start(self, event):
        '''Compute deltas and speeds from the beginning of the motion.'''
        self.dt_from_start = event.time - self._start_time
        self.dx_from_start = event.x - self._start_x
        self.dy_from_start = event.y - self._start_y
        self.distance_from_start = math.sqrt(self.dx_from_start * \
            self.dx_from_start + self.dy_from_start * self.dy_from_start)

    def compute_from_last_motion_event(self, event):
        '''Compute deltas and speeds from the last motion-event.'''
        self.dt_from_last_motion_event = event.time - \
            self._last_motion_event_time
        self.dx_from_last_motion_event = event.x - self._last_motion_event_x
        self.dy_from_last_motion_event = event.y - self._last_motion_event_y
        self.distance_from_last_motion_event = math.sqrt( \
            self.dx_from_last_motion_event * self.dx_from_last_motion_event + \
            self.dy_from_last_motion_event * self.dy_from_last_motion_event)

        if self.dt_from_last_motion_event != 0 :
            self.speed_x_from_last_motion_event = \
                float(self.dx_from_last_motion_event) / \
                float(self.dt_from_last_motion_event)
            self.speed_y_from_last_motion_event = \
                float(self.dy_from_last_motion_event) / \
                float(self.dt_from_last_motion_event)
            self.speed_from_last_motion_event = \
                float(self.distance_from_last_motion_event) / \
                float(self.dt_from_last_motion_event)
        else:
            self.speed_x_from_last_motion_event = 0
            self.speed_y_from_last_motion_event = 0
            self.speed_from_last_motion_event = 0

        # exponential moving average updates
        self.dt_ema = self._alpha * self.dt_from_last_motion_event + \
            self._beta * self.dt_ema
        self.dx_ema = self._alpha * self.dx_from_last_motion_event + \
            self._beta * self.dx_ema
        self.dy_ema = self._alpha * self.dy_from_last_motion_event + \
            self._beta * self.dy_ema
        self.distance_ema = self._alpha * self.distance_from_last_motion_event \
            + self._beta * self.distance_ema
        self.speed_x_ema = self._alpha * self.speed_x_from_last_motion_event + \
            self._beta * self.speed_x_ema
        self.speed_y_ema = self._alpha * self.speed_y_from_last_motion_event + \
            self._beta * self.speed_y_ema
        self.speed_ema = self._alpha * self.speed_from_last_motion_event + \
            self._beta * self.speed_ema

