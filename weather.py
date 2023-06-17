#!/usr/bin/env python

from pyowm.owm import OWM
from pyowm.utils.config import get_default_config

import time

api_key = "API_KEY_HERE"

class WeatherScreen:
    def __init__(self, gui, latitude = 47.7174, longitude = 9.3924, language = "de", refresh = 600, width = 32, height = 32):
        self.gui = gui
        self.latitude = latitude
        self.longitude = longitude
        self.language = language
        self.refresh = refresh
        self.width = width
        self.height = height

        self.lastTime = time.time()
        self.data = ""

        self.fetchData()

    def fetchData(self):
        config_dict = get_default_config()
        config_dict['language'] = self.language
        owm = OWM(api_key, config_dict)
        mgr = owm.weather_manager()

        observation = mgr.weather_at_place("Tuttlingen, DE")
        print(observation.weather.rain)
        print(observation.weather.snow)
        print(observation.weather.wind)
        print(observation.weather.humidity)
        print(observation.weather.pressure)
        print(observation.weather.temperature)
        print(observation.weather.clouds)
        print(observation.weather.status)
        print(observation.weather.detailed_status)
        print(observation.weather.weather_icon_name)
        print(observation.weather.precipitation_probability)

        #self.data = mgr.one_call(lat=self.latitude, lon=self.longitude)
        #print(self.data.forecast_hourly[0].wind().get("speed", 0))

    def draw(self):
        if (time.time() - self.lastTime) > self.refresh:
            self.fetchData()
            self.lastTime = time.time()

        # TODO text location
        # TODO text data

    def finished(self):
        return True

    def restart(self):
        pass

if __name__ == "__main__":
    from test import TestGUI
    t = TestGUI()
    s = WeatherScreen(t)
    s.draw()
    t.debug_loop(s.draw)
