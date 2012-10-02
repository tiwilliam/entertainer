# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Simple selector texture to show current position in menu'''

import clutter

from entertainerlib.gui.widgets.texture import Texture

class Selector(clutter.Group):
    '''Selector is an animated texture that can be used to display current
    position in menus.'''

    def __init__(self, theme):
        clutter.Group.__init__(self)
        self.animate_selector = False

        selector_filename = theme.getImage("selector")
        glow_filename = theme.getImage("selector_glow")

        # Set selector base texture
        self.selector = Texture(selector_filename)
        self.selector.set_opacity(200)
        self.add(self.selector)

        # Set selector GLOW texture
        self.glow = Texture(glow_filename)
        self.glow.set_opacity(0)
        self.add(self.glow)

        # Animate selector (Glow effect with glow overlay texture)
        self.in_time = clutter.Timeline(1500)
        self.in_alpha = clutter.Alpha(self.in_time, clutter.EASE_IN_OUT_SINE)
        self.in_behaviour = clutter.BehaviourOpacity(0, 255, self.in_alpha)
        self.in_behaviour.apply(self.glow)

        self.out_time = clutter.Timeline(1500)
        self.out_alpha = clutter.Alpha(self.out_time, clutter.EASE_IN_OUT_SINE)
        self.out_behaviour = clutter.BehaviourOpacity(255, 0, self.out_alpha)
        self.out_behaviour.apply(self.glow)

        self.score = clutter.Score()
        self.score.set_loop(True)
        self.score.append(timeline=self.in_time)
        # Link the out Timeline so that there is a smooth fade out.
        self.score.append(timeline=self.out_time, parent=self.in_time)

    def set_size(self, width, height):
        """Overrides clutter.Actor.set_size()"""
        self.selector.set_size(width, height)
        self.glow.set_size(width, height)

    def stop_animation(self):
        """Stop selector animation"""
        self.score.stop()
        self.glow.set_opacity(0)

    def start_animation(self):
        """Start selector animation"""
        self.score.start()

    def hide(self):
        """Overrides clutter.Actor.hide()"""
        clutter.Group.hide(self)
        if self.animate_selector:
            self.stop_animation()

    def show(self):
        """Overrides clutter.Actor.show()"""
        clutter.Group.show(self)
        self.start_animation()

    def hide_all(self):
        """Overrides clutter.Actor.hide_all()"""
        clutter.Group.hide_all(self)
        self.stop_animation()

    def show_all(self):
        """Overrides clutter.Actor.show_all()"""
        clutter.Group.show_all(self)
        self.start_animation()

