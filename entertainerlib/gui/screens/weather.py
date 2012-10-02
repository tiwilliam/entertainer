# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''WeatherScreen - Screen allows user to view current weather conditions'''

import clutter

from entertainerlib.gui.screens.screen import Screen
from entertainerlib.gui.widgets.label import Label
from entertainerlib.gui.widgets.texture import Texture
from entertainerlib.weather import Weather


class WeatherScreen(Screen):
    '''Screen to display the user's set weather location.'''

    def __init__(self):
        Screen.__init__(self, 'Weather')

        # Screen Title
        self.add(Label(0.13, "screentitle", 0, 0.87, _("Weather")))

        self.weather = Weather(self.config.weather_location)

        location = Label(0.04167, "text", 0.50, 0.13, self.weather.location,
            font_weight="bold")
        location.set_anchor_point_from_gravity(clutter.GRAVITY_CENTER)
        self.add(location)

        # Show today's weather
        self.create_day(self.weather.forecasts[0], 0.1, 0.15)

        # Show tomorrow's weather
        self.create_day(self.weather.forecasts[1], 0.1, 0.5)

        # Show day 3
        self.create_day(self.weather.forecasts[2], 0.4, 0.5)

        # Show day 4
        self.create_day(self.weather.forecasts[3], 0.7, 0.5)

    def create_day(self, day, x, y):
        """Create the Texture and labels for one day"""
        self.add(Texture(day["Image"], x, y))

        self.add(Label(0.04167, "text", x, y + 0.2, day["Day"],
            font_weight="bold"))

        conditions_text = \
            _("High: %(high)s   Low: %(low)s\nCondition: %(cond)s") % \
            {'high': day["High"], 'low': day["Low"], 'cond': day["Condition"]}
        self.add(Label(0.03, "text", x, y + 0.25, conditions_text))

