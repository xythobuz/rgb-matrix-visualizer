#!/usr/bin/env python3

#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import interstate75


class PicoMatrix:
    def __init__(self, w = 32, h = 32):
        self.width = w # x-axis
        self.height = h # y-axis

        self.panelW = w # x-axis
        self.panelH = h # y-axis

        # compatibility to TestGUI
        self.multiplier = 1.0

        if (w != 32) or (h != 32):
            raise RuntimeError("TODO not yet supported")

        self.matrix = interstate75.Interstate75(display = interstate75.DISPLAY_INTERSTATE75_32X32)

        self.loop_start() # initialize with blank image for ScrollText constructor

    def loop_start(self):
        self.matrix.display.clear()
        return False # no input, never quit on our own

    def loop_end(self):
        self.matrix.update()

    def loop(self, func = None):
        while True:
            if self.loop_start():
                break
            if func != None:
                func()
            self.loop_end()
        self.matrix.stop()

    def set_pixel(self, x, y, color):
        if (x < 0) or (y < 0) or (x >= self.width) or (y >= self.height):
            return

        pen = self.matrix.display.create_pen(color[0], color[1], color[2])
        self.matrix.display.set_pen(pen)
        self.matrix.display.pixel(int(x), int(y))

if __name__ == "__main__":
    t = PicoMatrix(32, 32)
    t.loop(lambda: t.set_pixel(15, 15, (255, 255, 255)))
