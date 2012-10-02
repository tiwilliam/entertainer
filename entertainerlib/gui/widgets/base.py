# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Base for widgets"""

from entertainerlib.configuration import Configuration


class Base(object):
    """Inherited class that allows for transforms from relative to absolute for
    user interface elements"""

    def __init__(self):
        """Set up by creating config object to get the stage and offset data"""
        self.config = Configuration()

    def get_abs_x(self, percentage):
        """Transform percentage to an abs length based on the stage width"""
        result = int(self.config.stage_width * percentage)
        return result

    def get_abs_y(self, percentage):
        """Transform percentage to an abs length based on the stage height"""
        result = int(self.config.stage_height * percentage)
        return result

    def y_for_x(self, percentage):
        """
        Returns the percentage of stage height giving the same number of pixels
        equivalent to `percentage` applied to the stage width.
        """
        stage_ratio = float(self.config.stage_width)
        stage_ratio /= self.config.stage_height
        return stage_ratio * percentage

