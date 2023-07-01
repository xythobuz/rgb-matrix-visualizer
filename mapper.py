#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import util
import time
import sys

useNTP = False
try:
    import ntptime
    useNTP = True
except:
    pass

# Does nothing. Take this as parent for new mappers.
class MapperNull:
    def __init__(self, g):
        self.gui = g
        self.width = self.gui.width
        self.height = self.gui.height
        self.multiplier = self.gui.multiplier
        self.panelW = self.gui.panelW
        self.panelH = self.gui.panelH

        if hasattr(self.gui, "matrix"):
            self.matrix = self.gui.matrix

    def batteryCache(self, refresh = False):
        return self.gui.batteryCache(refresh)

    def loop_start(self):
        return self.gui.loop_start()

    def loop_end(self):
        self.gui.loop_end()

    def loop(self, func = None):
        self.gui.loop(func)

    def set_pixel(self, x, y, color):
        self.gui.set_pixel(x, y, color)

# For some reason the red and green LEDs on older Pimoroni panels
# are far brighter than on newer panels.
# Adjust this by multiplying rg channels with 0.75, depending
# on hard-corded coordinate ranges.
class MapperColorAdjust(MapperNull):
    def set_pixel(self, x, y, color):
        # third panel from the left, with 64 <= x < 96,
        # is "old" type with brighter LEDs.
        # rest of panels to the left and right are less bright.
        # so adjust brightness of inner panel rg channels down.
        if (x >= (self.gui.panelW * 2)) and (x < (self.gui.panelW * 3)):
            color = (int(color[0] * 0.75), int(color[1] * 0.75), color[2])

        self.gui.set_pixel(x, y, color)

# This converts a long 128x32 strip to a 64x64 panel.
# The Pi is always connected to d, the last subpanel.
#
#     (0,  0)            (128, 0)
#             a  b  c  d
#     (0, 32)            (128, 32)
#
# on the hardware is converted to this for the effects:
#
#     (0,  0)      (64, 0)
#             a  b
#             c  d
#     (0, 64)      (64, 64)
class MapperStripToRect(MapperNull):
    def __init__(self, g):
        super().__init__(g)
        self.width = int(self.gui.width / 2)
        self.height = self.gui.height * 2

    def set_pixel(self, x, y, color):
        if y >= self.gui.height:
            x += self.width
            y -= self.panelH

        self.gui.set_pixel(x, y, color)

# Fetches current time via NTP.
# System time will be in UTC afterwards, not with local time-zone
# offset like when using rshell (eg. when using with a Pico).
#
# Brightness of display will be adjusted according to current time.
# To avoid being too bright at night.
#
# When used with the Interstate75 Pico implementation,
# this needs to be the "first" element of the mapper chain.
# Otherwise special handling for PicoText will not work.
class MapperReduceBrightness(MapperNull):
    def __init__(self, g):
        super().__init__(g)
        self.last = None
        self.connected = False
        self.refresh = 60 * 60 * 6
        self.factor = 1.0

    def fetch(self):
        self.factor = 1.0

        if not useNTP:
            return

        if not self.connected:
            self.connected = util.connectToWiFi()

        if self.connected:
            now = time.time()
            if (self.last == None) or ((now - self.last) >= self.refresh) or (now < self.last):
                self.last = now

                try:
                    print("Before sync： " + str(time.localtime()))
                    ntptime.settime()
                    print("After sync： "  + str(time.localtime()))
                except Exception as e:
                    print()
                    if hasattr(sys, "print_exception"):
                        sys.print_exception(e)
                    else:
                        print(e)
                    print()

                    return

        # (year, month, day, hour, minute, second, ?, ?)
        now = time.localtime()

        # 8pm utc == 22pm dst germany
        night = (now[0], now[1], now[2], 20, 0, 0, 0, 0)

        # 5am utc == 7am dst germany
        morning = (now[0], now[1], now[2], 5, 0, 0, 0, 0)

        if (now > morning) and (now < night):
            self.factor = 1.0
        else:
            self.factor = 0.42

    def adjust(self, color):
        return (int(color[0] * self.factor), int(color[1] * self.factor), int(color[2] * self.factor))

    def loop_end(self):
        super().loop_end()
        self.fetch()

    def set_pixel(self, x, y, color):
        color = self.adjust(color)
        self.gui.set_pixel(x, y, color)
