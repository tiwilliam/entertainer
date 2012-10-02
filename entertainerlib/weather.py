# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
"""
Weather Class
  Uses google weathers api to get a weather forecast for the next
  4 days.
"""

import locale
import os
import urllib2
from xml.dom import minidom

from entertainerlib.configuration import Configuration

#The lookup url for the google weather API
WEATHER_LOOKUP_URL = "http://www.google.co.uk/ig/api?weather="

WEATHER_IMAGES = {'mostly_sunny.gif': 'weather-sun-mostly',
                  'chance_of_rain.gif': 'weather-rain-chance',
                  'partly_cloudy.gif': 'weather-sun-clouds',
                  'mostly_cloudy.gif': 'weather-clouds-mostly',
                  'rain.gif': 'weather-rain',
                  'storm.gif': 'weather-lightning',
                  'fog.gif': 'weather-fog',
                  'sunny.gif': 'weather-sun',
                  'icy.gif': 'weather-ice',
                  'cloudy.gif': 'weather-clouds',
                  'snow.gif': 'weather-snow'}

class Weather:
    """Weather class."""

    def __init__(self, location=""):
        self.location = location
        self.forecasts = []
        self.theme = Configuration().theme
        self.locale = self._get_locale()
        self.refresh()

    def _get_locale(self):
        """Get locale information from user's machine."""
        default = locale.getdefaultlocale()[0]
        if default:
            lang = default.split("_")[0]
        else:
            lang = 'en'

        return lang

    def find_forecast(self, search):
        """Returns the search results page for the search."""
        url = WEATHER_LOOKUP_URL + search + "&hl=" + self.locale
        url = url.replace(" ", "%20")

        try:
            raw_data = urllib2.urlopen(url)
        except urllib2.URLError:
            self.location = _("Couldn't get weather reports from the internet!")
            self.forecasts_are_NA()
            return

        # We get the charset from the content-type of the http answer.
        conent_type = raw_data.info()["Content-Type"]
        encoding = conent_type.split("=")[1]

        # We read data according to the relevant charset and then we
        # prepare it to be parsed by minidom.
        data = unicode(raw_data.read(), encoding)
        data = data.encode("utf8")
        dom = minidom.parseString(data)

        in_forecast = 0
        day = ''
        low = ''
        high = ''
        condition = ''
        imagename = ''
        image = ''
        self.forecasts = []

        for node in dom.getElementsByTagNameNS('*', '*'):
            # a problem occured so bail out
            if (node.nodeName == 'problem_cause'):
                print _('Location not found or network problem')
                break

            if (node.nodeName == 'forecast_conditions'):
                in_forecast = 1

            if (in_forecast):
                if node.nodeName == 'day_of_week':
                    day = node.getAttribute('data')
                if node.nodeName == 'low':
                    low = node.getAttribute('data')
                    converted_low = int(low)
                if node.nodeName == 'high':
                    high = node.getAttribute('data')
                    converted_high = int(high)
                if node.nodeName == 'condition':
                    condition = node.getAttribute('data')
                if node.nodeName == 'icon':
                    imagename = os.path.split(node.getAttribute('data'))[-1]
                    image = self.set_image(imagename)

                # Condition is the last element of the forecast we are
                # interested in so write out the forecast if this is set.
                if (condition):
                    forecast = {"Day":day,
                                "Low":str(converted_low),
                                "High":str(converted_high),
                                "Condition":condition,
                                "Image":image}
                    self.forecasts.append(forecast)
                    in_forecast = 0
                    day = ''
                    low = ''
                    high = ''
                    condition = ''
                    imagename = ''
                    image = ''

        return self.forecasts

    def set_image(self, condition):
        """Returns an image for a given weather condition."""
        try:
            image_name = WEATHER_IMAGES[condition]
        except KeyError:
            image_name = 'weather-na'

        image = self.theme.getImage(image_name)
        return image

    def forecasts_are_NA(self):
        """Fills forecast with `NA` data."""
        self.forecast = []
        forecast = {"Day": _("NA"),
                    "Low": _("NA"),
                    "High": _("NA"),
                    "Condition": _("NA"),
                    "Image":self.theme.getImage('weather-na')}
        while len(self.forecasts) < 4:
            self.forecasts.append(forecast)

    def refresh(self):
        """Clear current weather and forecasts and then loads new data."""
        if self.location:
            self.find_forecast(self.location)
        else:
            self.location = _("No weather location defined!")
            self.forecasts_are_NA()

