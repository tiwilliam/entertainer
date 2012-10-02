# Copyright (c) 2009 Entertainer Developers - See COPYING - GPLv2
'''Tests Weather'''

from datetime import datetime, timedelta, tzinfo

from entertainerlib.tests import EntertainerTest
from entertainerlib.weather import Weather

class WeatherTest(EntertainerTest):
    """
    WeatherTest class
    Tests for the weather module.
    """
    def setUp(self):
        """Sets up everything for the test"""
        EntertainerTest.setUp(self)

        self.weather = Weather("Bath,England")

    def tearDown(self):
        """Clean up after the test"""
        EntertainerTest.tearDown(self)

    def testWeatherFindRemote(self):
        """Tests the weather code using a call to the outside world"""
        class EnglandTimeZone(tzinfo):
            '''An implementation of tzinfo specific to England.'''
            def __init__(self):
                tzinfo.__init__(self)
                self.stdoffset = timedelta(hours=0)
                self.reprname = 'England'
                self.stdname = 'WET' # Western Europe Time
                self.dstname = 'BST' # British Summer Time

            def __repr__(self):
                return self.reprname

            def _first_sunday_on_or_after(self, dt):
                '''Figure out the DST date.'''
                days_to_go = 6 - dt.weekday()
                if days_to_go:
                    dt += timedelta(days_to_go)
                return dt

            def tzname(self, dt):
                '''See `tzinfo.tzname`.'''
                if self.dst(dt):
                    return self.dstname
                else:
                    return self.stdname

            def utcoffset(self, dt):
                '''See `tzinfo.utcoffset`.'''
                return self.stdoffset + self.dst(dt)

            def dst(self, dt):
                '''See `tzinfo.dst`.'''
                DSTSTART = datetime(1, 4, 1, 2)
                DSTEND = datetime(1, 10, 25, 1)
                ZERO = timedelta(0)
                HOUR = timedelta(hours=1)
                if dt is None or dt.tzinfo is None:
                    return ZERO
                assert dt.tzinfo is self

                start = self._first_sunday_on_or_after(
                    DSTSTART.replace(year=dt.year))
                end = self._first_sunday_on_or_after(
                    DSTEND.replace(year=dt.year))

                if start <= dt.replace(tzinfo=None) < end:
                    return HOUR
                else:
                    return ZERO
        england = EnglandTimeZone()

        self.weather.location = 'Bath,England'
        self.weather.refresh()

        today = self.weather.forecasts[0]
        day = datetime.now(england).strftime('%a')
        self.assertEqual(str(today["Day"]), day)

    def testWeatherLocationLatinEncoding(self):
        """Tests whether code can handle Latin-1 encoding back from google"""
        #Check for Montreal which gets info back from google in Latin-1
        self.weather.location = "Montreal"
        self.weather.refresh()
        results = self.weather.forecasts
        #if there are results then it's working
        self.assertTrue(len(results) > 0)

    def test_yuma_conditions(self):
        """Tests that there's no 'weather-na' in Yuma."""
        # Here we expect sun http://en.wikipedia.org/wiki/Yuma,_Arizona.
        # `Yuma is the sunniest place on earth` (90% of the time)
        self.weather.location = "Yuma"
        self.weather.refresh()
        forecasts = self.weather.forecasts
        for day in forecasts:
            self.assertFalse(day["Image"] == 'weather-na')

    def test_london_conditions(self):
        """Tests that there's no 'weather-na' in London."""
        self.weather.location = "London"
        self.weather.refresh()
        forecasts = self.weather.forecasts
        for day in forecasts:
            self.assertFalse(day["Image"] == 'weather-na')

    def test_perth_conditions(self):
        """Tests that there's no 'weather-na' in Perth."""
        self.weather.location = "Perth"
        self.weather.refresh()
        forecasts = self.weather.forecasts
        for day in forecasts:
            self.assertFalse(day["Image"] == 'weather-na')

    def test_nyc_conditions(self):
        """Tests that there's no 'weather-na' in New York."""
        self.weather.location = "New York"
        self.weather.refresh()
        forecasts = self.weather.forecasts
        for day in forecasts:
            self.assertFalse(day["Image"] == 'weather-na')

    def test_north_pole_conditions(self):
        """Tests that there's no 'weather-na' in North Pole."""
        self.weather.location = "North Pole"
        self.weather.refresh()
        forecasts = self.weather.forecasts
        for day in forecasts:
            self.assertFalse(day["Image"] == 'weather-na')

    def test_no_location(self):
        """Tests the output if there's no location specified."""
        self.weather.location = ""
        self.weather.refresh()
        forecasts = self.weather.forecasts
        for day in forecasts:
            self.assertFalse(day["Day"] == _("NA"))
            self.assertFalse(day["Low"] == _("NA"))
            self.assertFalse(day["High"] == _("NA"))
            self.assertFalse(day["Condition"] == _("NA"))
            self.assertFalse(day["Image"] == 'weather-na')

