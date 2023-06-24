#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

# Does nothing. Take this as parent for new mappers.
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
