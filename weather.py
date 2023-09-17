#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import util
from image import ImageScreen

import time
from datetime import datetime, timezone, timedelta

from wetterdienst import Settings
from wetterdienst.provider.dwd.mosmix import (
    DwdForecastDate,
    DwdMosmixRequest,
    DwdMosmixType,
)
import polars

def get_first_capitalized_word(s):
    words = s.split()
    for w in words:
        if w[0].isupper():
            return w
    return None

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
        self.num_state = 4

        self.descriptions = [
            (95, 'leichtes oder mäßiges Gewitter mit Regen oder Schnee', 'weather_icon_95.png'),
            (57, 'mäßiger oder starker gefrierender Sprühregen', 'weather_icon_57.png'),
            (56, 'leichter gefrierender Sprühregen', 'weather_icon_56.png'),
            (67, 'mäßiger bis starker gefrierender Regen', 'weather_icon_67.png'),
            (66, 'leichter gefrierender Regen', 'weather_icon_66.png'),
            (86, 'mäßiger bis starker Schneeschauer', 'weather_icon_86.png'),
            (85, 'leichter Schneeschauer', 'weather_icon_85.png'),
            (84, 'mäßiger oder starker Schneeregenschauer', 'weather_icon_84.png'),
            (83, 'leichter Schneeregenschauer', 'weather_icon_83.png'),
            (82, 'äußerst heftiger Regenschauer', 'weather_icon_82.png'),
            (81, 'mäßiger oder starker Regenschauer', 'weather_icon_81.png'),
            (80, 'leichter Regenschauer', 'weather_icon_80.png'),
            (75, 'durchgehend starker Schneefall', 'weather_icon_75.png'),
            (73, 'durchgehend mäßiger Schneefall', 'weather_icon_73.png'),
            (71, 'durchgehend leichter Schneefall', 'weather_icon_71.png'),
            (69, 'mäßger oder starker Schneeregen', 'weather_icon_69.png'),
            (68, 'leichter Schneeregen', 'weather_icon_68.png'),
            (55, 'durchgehend starker Sprühregen', 'weather_icon_55.png'),
            (53, 'durchgehend mäßiger Sprühregen', 'weather_icon_53.png'),
            (51, 'durchgehend leichter Sprühregen', 'weather_icon_51.png'),
            (65, 'durchgehend starker Regen', 'weather_icon_65.png'),
            (63, 'durchgehend mäßiger Regen', 'weather_icon_63.png'),
            (61, 'durchgehend leichter Regen', 'weather_icon_61.png'),
            (49, 'Nebel mit Reifansatz, Himmel nicht erkennbar, unverändert', 'weather_icon_49.png'),
            (45, 'Nebel, Himmel nicht erkennbar', 'weather_icon_45.png'),
            (3, 'Bewölkung zunehmend', None),
            (2, 'Bewölkung unverändert', None),
            (1, 'Bewölkung abnehmend', None),
            (0, 'keine Bewölkungsentwicklung', None),
        ]

        self.find_station()
        self.restart()

    def restart(self):
        self.state = 0
        self.old_keys = self.input.empty() # TODO support missing input
        self.done = False
        self.last = time.time()

    def find_station(self):
        self.gui.loop_start()
        self.t_head.setText("Weather:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)
        self.t_sub.setText("Loading...", "tom-thumb")
        self.t_sub.draw(0, -self.gui.height / 2 + 5 + 6 * 4)
        self.t_val.setText("Station...", "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 6)
        self.gui.loop_end()

        settings = Settings(ts_shape=True, ts_humanize=True, cache_disable=False)
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
        self.gui.loop_start()
        self.t_head.setText("Weather:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)
        self.t_sub.setText("Loading...", "tom-thumb")
        self.t_sub.draw(0, -self.gui.height / 2 + 5 + 6 * 4)
        self.t_val.setText("Refresh...", "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 6)
        self.gui.loop_end()

        settings = Settings(ts_shape=True, ts_humanize=True, cache_disable=False)
        request = DwdMosmixRequest(
            parameter=self.params,
            start_issue=DwdForecastDate.LATEST,
            mosmix_type=DwdMosmixType.LARGE,
            settings=settings,
        )
        self.forecast = request.filter_by_station_id(station_id=[self.station["station_id"][0]])
        self.parse_forecast()

    def parse_forecast(self):
        self.gui.loop_start()
        self.t_head.setText("Weather:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)
        self.t_sub.setText("Parsing", "tom-thumb")
        self.t_sub.draw(0, -self.gui.height / 2 + 5 + 6 * 4)
        self.t_val.setText("Forecast", "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 6)
        self.gui.loop_end()

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
        elif keys["down"] and (not self.old_keys["down"]) and (not self.old_keys["select"]):
            self.state = (self.state - 1) % self.num_state
            self.last = time.time()

        self.old_keys = keys.copy()

    def finished(self):
        return self.done

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

        # convert weather id
        val = self.data.filter(polars.col("parameter") == self.params[0])[0]["value"][0]
        name = "ID {} Unknown".format(val)
        img = None
        for i, d in enumerate(self.descriptions):
            if d[0] != val:
                continue

            if d[2] == None:
                self.descriptions[i] = (d[0], d[1], "weather_unknown.png")

            if isinstance(d[2], str):
                w = 50
                target_size = (w, w)
                iscr = ImageScreen(self.gui, d[2], 0.2, 1, 5.0, None, target_size, False)
                self.descriptions[i] = (d[0], d[1], iscr)
                iscr.xOff = (self.gui.width - w) / 2
                iscr.yOff = self.gui.height - w + 5
                img = iscr
            else:
                img = d[2]

            name = get_first_capitalized_word(d[1])

        # print weather description text
        self.t_sub.setText(name, "tom-thumb")
        self.t_sub.draw(0, -self.gui.height / 2 + 5 + 6 * 1 + 2)
        #self.t_sub.draw(0, -self.gui.height / 2 + 5 + 6 * 2)
        #self.t_sub.draw(self.gui.width, -self.gui.height / 2 + 5 + 6 * 3)
        #self.t_sub.draw(self.gui.width * 2, -self.gui.height / 2 + 5 + 6 * 4)

        # show image if it exists
        if img != None:
            img.draw()

        # id of weather / image
        self.t_aux.setText("{}".format(int(val)), "tom-thumb")
        self.t_aux.draw(0, -self.gui.height / 2 + 5 + 6 * 9 + 3)

    def draw_temperature(self):
        # heading
        self.t_head.setText("Temps:", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)
        self.t_sub.setText("Current:", "lemon")
        self.t_sub.draw(3, -self.gui.height / 2 + 20)

        # current temperature
        val = self.data.filter(polars.col("parameter") == self.params[1])[0]["value"][0]
        val = val - 273.15 # kelvin to celsius
        self.t_val.setText("{:.1f}°C".format(val), "tom-thumb")
        self.t_val.draw(0, -self.gui.height / 2 + 5 + 6 * 5)

    def draw_cloud_cover(self):
        # heading
        self.t_head.setText("Cloud", "lemon")
        self.t_head.draw(3, -self.gui.height / 2 + 7)
        self.t_sub.setText("Coverage:", "lemon")
        self.t_sub.draw(3, -self.gui.height / 2 + 20)

        val = self.data.filter(polars.col("parameter") == self.params[2])[0]["value"][0]
        self.t_val.setText("{:.1f}%".format(val), "tom-thumb")
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
            if self.state == 0:
                self.done = True
            self.last = time.time()

        # draw progress bar on bottom most row
        elapsed = (time.time() - self.last)
        ratio = elapsed / self.timestep
        for i in range(0, int(ratio * self.gui.width) + 1):
            self.gui.set_pixel(i, self.gui.height - 1, (0, 255, 0))

if __name__ == "__main__":
    from config import Config

    i = util.getInput()
    t = util.getTarget(i)

    s = WeatherScreen(t, i, Config.weather_latlon, 5.0, 60.0 * 10.0)
    util.loop(t, s.draw)
