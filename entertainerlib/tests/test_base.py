# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""Tests Base"""

from entertainerlib.gui.widgets.base import Base
from entertainerlib.tests import EntertainerTest


class BaseTest(EntertainerTest):
    """Test for entertainerlib.gui.widgets.base"""

    def setUp(self):
        """Set up the test"""
        EntertainerTest.setUp(self)

        self.base = Base()

    def test_create(self):
        """Test Base object creation."""
        self.assertTrue(isinstance(self.base, Base))

    def test_get_abs_x(self):
        """Test getting the absolute size of x based on the stage width."""
        self.assertEqual(self.base.get_abs_x(.25), 341)

    def test_get_abs_y(self):
        """Test getting the absolute size of y based on the stage height."""
        self.assertEqual(self.base.get_abs_y(.25), 192)

    def test_y_for_x(self):
        """Test of the y_for_x method."""
        self.assertAlmostEqual(self.base.y_for_x(.25), 0.44466145833333331)

