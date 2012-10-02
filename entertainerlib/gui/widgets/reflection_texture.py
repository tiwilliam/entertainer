# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Cairo based texture that can be used as reflection'''

import gtk
import cairo
import clutter

from entertainerlib.gui.widgets.base import Base


class ReflectionTexture(Base, clutter.CairoTexture):
    """
    Reflection texture

    This texture can be used as reflection to another texture. This texture
    is rendered with Cairo.
    """

    def __init__(self, x, y, width, height, pixbuf, ref_height=0.3, opacity=0.3,
        round_corners=False, margin=1, radius=15):
        Base.__init__(self)

        abs_width = self.get_abs_x(width)
        abs_height = self.get_abs_y(height)

        clutter.CairoTexture.__init__(self, abs_width, abs_height)

        context = self.cairo_create()
        ct = gtk.gdk.CairoContext(context)

        # Round corners
        if round_corners:
            x = 0 + margin
            y = 0 + margin
            w1 = abs_width - (margin * 2)
            h1 = abs_height - (margin * 2)
            self.roundedCorners(context, x, y, w1, h1, radius, radius)

        # Scale context area
        wr = abs_width / float(pixbuf.get_width())
        hr = abs_height / float(pixbuf.get_height())
        context.scale(wr, hr)

        # Create gradient mask
        self.gradient = cairo.LinearGradient(0, 0, 0, pixbuf.get_height())
        self.gradient.add_color_stop_rgba(1 - ref_height, 1, 1, 1, 0)
        self.gradient.add_color_stop_rgba(1, 0, 0, 0, opacity)

        ct.set_source_pixbuf(pixbuf, 0, 0)
        context.mask(self.gradient)

        del context # Update texture
        del ct

        self.set_anchor_point_from_gravity(clutter.GRAVITY_SOUTH_WEST)
        self.set_rotation(clutter.Z_AXIS, 180, 0, 0, 0)
        self.set_rotation(clutter.Y_AXIS, 180, 0, 0, 0)

        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

    def roundedCorners(self, context, x, y, w, h, radius_x, radius_y):
        """
        Clip cairo texture with rounded rectangle.
        """
        ARC_TO_BEZIER = 0.55228475
        if radius_x > w - radius_x:
            radius_x = w / 2
        if radius_y > h - radius_y:
            radius_y = h / 2

        #approximate (quite close) the arc using a bezier curve
        c1 = ARC_TO_BEZIER * radius_x
        c2 = ARC_TO_BEZIER * radius_y

        context.new_path()
        context.move_to ( x + radius_x, y)
        context.rel_line_to ( w - 2 * radius_x, 0.0)
        context.rel_curve_to ( c1, 0.0, radius_x, c2, radius_x, radius_y)
        context.rel_line_to ( 0, h - 2 * radius_y)
        context.rel_curve_to ( 0.0, c2, c1 - radius_x, radius_y, -radius_x,
            radius_y)
        context.rel_line_to ( -w + 2 * radius_x, 0)
        context.rel_curve_to ( -c1, 0, -radius_x, -c2, -radius_x, -radius_y)
        context.rel_line_to (0, -h + 2 * radius_y)
        context.rel_curve_to (0.0, -c2, radius_x - c1, -radius_y, radius_x,
            -radius_y)
        context.close_path()
        context.clip()

