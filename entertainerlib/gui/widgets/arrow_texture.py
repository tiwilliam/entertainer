# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Displays text in rounded rectangle box'''

import clutter

from entertainerlib.gui.widgets.base import Base


class ArrowTexture(Base, clutter.CairoTexture):
    """Clutter CairoTexture which represents an arrow."""

    # Arrow direction (One of these should be passed as a paramter)
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3
    ARC_TO_BEZIER = 0.55228475

    def __init__(self, x, y, size, fg_color, bg_color, direction):
        Base.__init__(self)

        abs_size = self.get_abs_x(size)

        clutter.CairoTexture.__init__(self, abs_size, abs_size)

        context = self.cairo_create()
        context.scale(abs_size, abs_size)

        fg_cairo = self._color_to_cairo_color(fg_color)
        bg_cairo = self._color_to_cairo_color(bg_color)

        # Draw background
        context.set_line_width (0.15)
        context.set_source_rgba(bg_cairo[0], bg_cairo[1],
                                bg_cairo[2], bg_cairo[3])
        self._roundedrec(context, 0, 0, 1, 1, 0.08, 0.1)
        context.fill()

        # Draw arrow
        context.set_source_rgba(fg_cairo[0], fg_cairo[1],
                                fg_cairo[2], fg_cairo[3])
        if direction == ArrowTexture.DOWN:
            context.move_to(0.25, 0.33)
            context.line_to(0.50, 0.66)
            context.line_to(0.75, 0.33)
            context.stroke()
        elif direction == ArrowTexture.UP:
            context.move_to(0.25, 0.66)
            context.line_to(0.50, 0.33)
            context.line_to(0.75, 0.66)
            context.stroke()
        elif direction == ArrowTexture.RIGHT:
            context.move_to(0.33, 0.25)
            context.line_to(0.66, 0.50)
            context.line_to(0.33, 0.75)
            context.stroke()
        elif direction == ArrowTexture.LEFT:
            context.move_to(0.66, 0.25)
            context.line_to(0.33, 0.50)
            context.line_to(0.66, 0.75)
            context.stroke()

        del(context) # Updates texture

        # Create bounce effect
        self.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)

        in_time = clutter.Timeline(300)
        in_alpha = clutter.Alpha(in_time, clutter.EASE_OUT_SINE)
        self.in_behaviour = clutter.BehaviourScale(1.0, 1.0, 1.5, 1.5, in_alpha)
        self.in_behaviour.apply(self)

        out_time = clutter.Timeline(300)
        out_alpha = clutter.Alpha(out_time, clutter.EASE_OUT_SINE)
        self.out_behaviour = clutter.BehaviourScale(1.5, 1.5, 1.0, 1.0,
            out_alpha)
        self.out_behaviour.apply(self)

        self.score = clutter.Score()
        self.score.append(timeline=in_time)
        self.score.append(timeline=out_time, parent=in_time)

        self.set_position(self.get_abs_x(x), self.get_abs_y(y))

    def bounce(self):
        """Execute bounce effect for this array."""
        if not self.score.is_playing():
            self.score.start()

    def _color_to_cairo_color(self, color):
        """
        Transform from 0-255 to 0-1.
        @param color: (r, g, b, a) integer tuple
        """
        (int_r, int_g, int_b, int_a) = color
        r = float(int_r) / 255.0
        g = float(int_g) / 255.0
        b = float(int_b) / 255.0
        a = float(int_a) / 255.0
        return r, g, b, a

    def _roundedrec(self, cr, x_pos, y_pos, width, height, radius_x=5,
        radius_y=5):
        """
        from mono moonlight aka mono silverlight
        test limits (without using multiplications)
        http://graphics.stanford.edu/courses/cs248-98-fall/Final/q1.html
        """

        if radius_x > width - radius_x:
            radius_x = width / 2
        if radius_y > height - radius_y:
            radius_y = height / 2

        #approximate (quite close) the arc using a bezier curve
        c1 = ArrowTexture.ARC_TO_BEZIER * radius_x
        c2 = ArrowTexture.ARC_TO_BEZIER * radius_y

        cr.new_path()
        cr.move_to(x_pos + radius_x, y_pos)
        cr.rel_line_to(width - 2 * radius_x, 0.0)
        cr.rel_curve_to(c1, 0.0, radius_x, c2, radius_x, radius_y)
        cr.rel_line_to(0, height - 2 * radius_y)
        cr.rel_curve_to(0.0, c2, c1 - radius_x, radius_y, -radius_x, radius_y)
        cr.rel_line_to(-width + 2 * radius_x, 0)
        cr.rel_curve_to(-c1, 0, -radius_x, -c2, -radius_x, -radius_y)
        cr.rel_line_to(0, -height + 2 * radius_y)
        cr.rel_curve_to(0.0, -c2, radius_x - c1, -radius_y, radius_x, -radius_y)
        cr.close_path()

