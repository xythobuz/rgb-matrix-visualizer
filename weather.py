#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import util
import time
from datetime import datetime, timezone, timedelta

from wetterdienst import Settings
from wetterdienst.provider.dwd.mosmix import (
    DwdForecastDate,
    DwdMosmixRequest,
    DwdMosmixType,
)
import polars

class WeatherScreen:
    def __init__(self, g, i, latlon, timestep = 5.0, refresh = (60.0 * 60.0)):
        self.gui = g
        self.input = i
        self.latlon = latlon
        self.timestep = timestep

        DrawText = util.getTextDrawer()
        self.t_head = DrawText(self.gui, (255, 255, 255), (0, 0, 0))
        self.t_sub = DrawText(self.gui, (0, 255, 255), (0, 0, 0))
        self.t_val = DrawText(self.gui, (255, 0, 255), (0, 0, 0))
        self.t_aux = DrawText(self.gui, (255, 255, 0), (0, 0, 0))

        self.params = [
            "weather_significant",
            "temperature_air_mean_200",
            "cloud_cover_effective",
        ]
        self.num_state = len(self.params) + 1

        self.find_station()
        self.restart()

    def restart(self):
        self.state = 0
        self.old_keys = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "a": False,
            "b": False,
            "x": False,
            "y": False,
            "l": False,
            "r": False,
            "start": False,
            "select": False,
        }
        self.last = time.time()

    def find_station(self):
        settings = Settings(ts_shape=True, ts_humanize=True)
        request = DwdMosmixRequest(
            parameter=self.params,
            start_issue=DwdForecastDate.LATEST,
            mosmix_type=DwdMosmixType.LARGE,
            settings=settings,
        )
        stations = request.filter_by_distance(latlon=self.latlon, distance=30)
        self.station = stations.df[0]

        print("Found station '{}' ({}) in {:.2f} km distance".format(
            self.station["name"][0],
            self.station["station_id"][0],
            self.station["distance"][0]
        ))

        self.forecast = request.filter_by_station_id(station_id=[
            self.station["station_id"][0],
        ])
        self.parse_forecast()

    def get_forecast(self):
        settings = Settings(ts_shape=True, ts_humanize=True)
        request = DwdMosmixRequest(
            parameter=self.params,
            start_issue=DwdForecastDate.LATEST,
            mosmix_type=DwdMosmixType.LARGE,
            settings=settings,
        )
        self.forecast = request.filter_by_station_id(station_id=[self.station["station_id"][0]])
        self.parse_forecast()

    def parse_forecast(self):
        self.last_forecast = time.time()

        response = next(self.forecast.values.query())
        response_subset = response.df.select(["date", "parameter", "value"])

        # only datapoints from -1h to +12h from now
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc) + timedelta(hours=12)
        self.data = response_subset.filter((polars.col("date") >= start_time) & (polars.col("date") <= end_time))

        #print(self.data)
        #for p in self.params:
        #    print(self.data.filter(polars.col("parameter") == p)[0])
        #for i in range(0, len(self.data)):
        #    print(self.data[i])

    def buttons(self):
        keys = self.input.get()

        if keys["up"] and (not self.old_keys["up"]) and (not self.old_keys["select"]):
            self.state = (self.state + 1) % self.num_state
            self.last = time.time()
        elif keys["down"] and (not self.old_keys["select"]):
            self.state = (self.state - 1) % self.num_state
            self.last = time.time()

        self.old_keys = keys.copy()

    def finished(self):
        return False # TODO

    def draw_station_info(self):
        # heading
        self.t_head.setText("Weather:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)

        # station info (2 lines)
        self.t_sub.setText(self.station["name"][0], "tom-thumb")
        self.t_sub.draw(0, -self.gui.height / 2 + 5 + 6 * 2)
        self.t_sub.draw(self.gui.width, -self.gui.height / 2 + 5 + 6 * 3)

        # distance
        self.t_val.setText("Distance:", "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 5)
        self.t_val.setText("{:.2f} km".format(self.station["distance"][0]), "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 6)

        # lat lon
        self.t_aux.setText("Lat: {:.2f}".format(self.station["latitude"][0]), "tom-thumb")
        self.t_aux.draw(0, -self.gui.height / 2 + 5 + 6 * 8)
        self.t_aux.setText("Lon: {:.2f}".format(self.station["longitude"][0]), "tom-thumb")
        self.t_aux.draw(0, -self.gui.height / 2 + 5 + 6 * 9)

    def draw_weather(self):
        # heading
        self.t_head.setText("Weather:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)

        val = self.data.filter(polars.col("parameter") == self.params[0])[0]["value"][0]
        self.t_val.setText("{:.0f}".format(val), "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 5)

    def draw_temperature(self):
        # heading
        self.t_head.setText("Temps:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)

        # current temperature
        self.t_sub.setText("Current:", "tom-thumb")
        self.t_sub.draw(0, -self.gui.height / 2 + 5 + 6 * 2)
        val = self.data.filter(polars.col("parameter") == self.params[1])[0]["value"][0]
        val = val - 273.15 # kelvin to celsius
        self.t_val.setText("{:.1f} °C".format(val), "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 3)

    def draw_cloud_cover(self):
        # heading
        self.t_head.setText("Clouds:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)

        val = self.data.filter(polars.col("parameter") == self.params[2])[0]["value"][0]
        self.t_val.setText("{:.1f} %".format(val), "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 5)

    def draw(self):
        # handle button input
        if self.input != None:
            self.buttons()

        # draw screen contents
        if self.state == 0:
            self.draw_station_info()
        elif self.state == 1:
            self.draw_weather()
        elif self.state == 2:
            self.draw_temperature()
        elif self.state == 3:
            self.draw_cloud_cover()

        # advance to next screen after time has passed
        if (time.time() - self.last) >= self.timestep:
            self.state = (self.state + 1) % self.num_state
            self.last = time.time()

        # draw progress bar on bottom most row
        elapsed = (time.time() - self.last)
        ratio = elapsed / self.timestep
        for i in range(0, int(ratio * self.gui.width)):
            self.gui.set_pixel(i, self.gui.height - 1, (255, 0, 0))

if __name__ == "__main__":
    from config import Config

    i = util.getInput()
    t = util.getTarget(i)

    s = WeatherScreen(t, i, Config.weather_latlon, 2.0, 60.0 * 10.0)
    util.loop(t, s.draw)
