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

    def exit(self):
        self.gui.exit()

    def loop_start(self):
        return self.gui.loop_start()

    def loop_end(self):
        self.gui.loop_end()

    def set_pixel(self, x, y, color):
        self.gui.set_pixel(x, y, color)

# For some reason the red and green LEDs on older Pimoroni panels
# are far brighter than on newer panels.
# Adjust this by multiplying rg channels with 0.75 and b channel
# with 0.85, depending on hard-corded coordinate ranges.
class MapperColorAdjust(MapperNull):
    def set_pixel(self, x, y, color):
        # second panel from the left, with 32 <= x,
        # is "old" type with brighter LEDs.
        # rest of panels to the left are less bright.
        # so adjust brightness of other panel channels down.
        if x >= self.gui.panelW:
            color = (int(color[0] * 0.75), int(color[1] * 0.75), color[2] * 0.85)

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
    def __init__(self, g, i = None):
        super().__init__(g)
        self.input = i
        self.last = None
        self.connected = False
        self.refresh = 60 * 60 * 6
        self.factor = 1.0
        self.user_mod = None
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

    def fetch(self):
        if useNTP:
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
        else:
            if self.last == None:
                self.last = time.time()
                print("Time: " + str(time.localtime()))

        # (year, month, day, hour, minute, second, ?, ?)
        now = time.localtime()

        # TODO ntptime is setting to UTC, host is on proper timezone
        if useNTP:
            # 8pm utc == 10pm cest germany
            night = (now[0], now[1], now[2], 20, 0, 0, 0, 0)

            # 5am utc == 7am cest germany
            morning = (now[0], now[1], now[2], 5, 0, 0, 0, 0)
        else:
            # 10pm cest germany
            night = (now[0], now[1], now[2], 22, 0, 0, 0, 0)

            # 7am cest germany
            morning = (now[0], now[1], now[2], 7, 0, 0, 0, 0)

        if (now > morning) and (now < night):
            self.factor = 1.0
        else:
            self.factor = 0.42

    def buttons(self):
        keys = self.input.get()

        if (keys["select"] and keys["up"] and (not self.old_keys["up"])) or (keys["up"] and keys["select"] and (not self.old_keys["select"])):
            self.factor += 0.05
            self.factor = min(self.factor, 0.95)
            self.user_mod = time.time()
        elif (keys["select"] and keys["down"] and (not self.old_keys["down"])) or (keys["down"] and keys["select"] and (not self.old_keys["select"])):
            self.factor -= 0.05
            self.factor = max(self.factor, 0.05)
            self.user_mod = time.time()

        self.old_keys = keys.copy()

    def adjust(self, color):
        return (int(color[0] * self.factor), int(color[1] * self.factor), int(color[2] * self.factor))

    def loop_start(self):
        if self.input != None:
            self.buttons()

        return super().loop_start()

    def loop_end(self):
        super().loop_end()

        if self.user_mod == None:
            self.fetch()
        elif (time.time() - self.user_mod) > self.refresh:
            # fall back from user-modified factor after 6h
            self.user_mod = None

    def set_pixel(self, x, y, color):
        color = self.adjust(color)
        self.gui.set_pixel(x, y, color)
