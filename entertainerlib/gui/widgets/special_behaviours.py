# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Implementation of special clutter behaviours'''

import math

import clutter

class LoopedPathBehaviour(clutter.Behaviour):
    """A custom PathBehaviour driven by an index"""
    __gtype_name__ = 'LoopedPathBehaviour'

    def __init__(self, alpha=None):
        clutter.Behaviour.__init__(self)
        self.set_alpha(alpha)
        self.start_index = 0.0
        self.end_index = 1.0
        self.start_knot = (0, 0)
        self.end_knot = (10, 10)

    def do_alpha_notify(self, alpha_value):
        """
        Actors are positioned on the Line defined by the 2 knots according to
        the alpha value.
        alpha = 0         positioned at start_index
        alpha = MAX_ALPHA positioned at end_index
        """
        raw_index = alpha_value * (self.end_index - self.start_index)
        raw_index += self.start_index

        # we rescale the raw_index to be inside [0, 1[
        if raw_index >= 0 :
            index = math.modf(raw_index)[0]
        else:
            index = 1 + math.modf(raw_index)[0]

        # Calculation of new coordinates.
        # Coordinates x & y are taken from the parametric equation of a line.
        # index is the parameter. start_knot and end_knot are the 2 points
        # defining the line.
        x = index * (self.end_knot[0] - self.start_knot[0]) + self.start_knot[0]
        y = index * (self.end_knot[1] - self.start_knot[1]) + self.start_knot[1]

        for actor in self.get_actors():
            actor.set_position(int(x), int(y))

    @ property
    def path_length(self):
        """Calculation of the path's length in pixels'"""
        dx = self.end_knot[0] - self.start_knot[0]
        dy = self.end_knot[1] - self.start_knot[1]
        return math.sqrt(dx * dx + dy * dy)

class FontSizeBehaviour(clutter.Behaviour):
    """A custom Behaviour to change the `font-size` property of Labels."""
    __gtype_name__ = 'FontSizeBehaviour'

    def __init__(self, alpha=None):
        clutter.Behaviour.__init__(self)
        self.set_alpha(alpha)
        self.start_size = 1.0
        self.end_size = 1.0

    def do_alpha_notify(self, alpha_value):
        """Alpha function changing the `font-size` property of Labels."""
        size = alpha_value * (self.end_size - self.start_size)
        size += self.start_size

        for actor in self.get_actors():
            actor.font_size = size
            actor.update()

