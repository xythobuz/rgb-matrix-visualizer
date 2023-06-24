#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

# Does nothing. Take this as an example for new Mappers.
class MapperNull:
    def __init__(self, g):
        self.gui = g
        self.width = self.gui.width
        self.height = self.gui.height
        self.multiplier = self.gui.multiplier
        self.panelW = self.gui.panelW
        self.panelH = self.gui.panelH

    def loop_start(self):
        return self.gui.loop_start()

    def loop_end(self):
        self.gui.loop_end()

    def debug_loop(self, func = None):
        self.gui.debug_loop(func)

    def set_pixel(self, x, y, color):
        self.gui.set_pixel(x, y, color)

# For some reason the red and green LEDs on newer Pimoroni panels
# are far brighter than on older panels.
# Adjust this by multiplying rg channels with 0.75, depending
# on hard-corded coordinate ranges.
class MapperColorAdjust(MapperNull):
    def set_pixel(self, x, y, color):
        # right-most panel, with maximum x coordinates,
        # is "old" type with less bright LEDs.
        # rest of panels to the left are brighter.
        # so adjust brightness of left panel rg channels down.
        if x < self.gui.panelW:
            color = (int(color[0] * 0.75), int(color[1] * 0.75), color[2])

        self.gui.set_pixel(x, y, color)
