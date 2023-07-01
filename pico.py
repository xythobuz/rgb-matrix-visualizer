#!/usr/bin/env python3

# For the Pimoroni Interstate75 Raspberry Pi Pico RGB LED Matrix interface:
# https://github.com/pimoroni/pimoroni-pico
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import interstate75
import hub75
from mapper import MapperReduceBrightness
import time
from machine import Pin

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

        mode = interstate75.DISPLAY_INTERSTATE75_32X32
        self.matrix = interstate75.Interstate75(display = mode, panel_type = hub75.PANEL_FM6126A)

        self.black = self.matrix.display.create_pen(0, 0, 0)
        self.white = self.matrix.display.create_pen(255, 255, 255)

        self.ledTime = time.time()
        self.led = Pin("LED", Pin.OUT)

        self.loop_start() # initialize with blank image for ScrollText constructor

    def loop_start(self):
        self.matrix.display.set_pen(self.black)
        self.matrix.display.clear()
        self.matrix.display.set_pen(self.white)

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

            now = time.time()
            if ((now - self.ledTime) >= 0.5) or (now < self.ledTime):
                self.ledTime = now
                self.led.toggle()

        self.matrix.stop()

    def set_pixel(self, x, y, color):
        if (x < 0) or (y < 0) or (x >= self.width) or (y >= self.height):
            return

        pen = self.matrix.display.create_pen(color[0], color[1], color[2])
        self.matrix.display.set_pen(pen)

        self.matrix.display.pixel(int(x), int(y))

class PicoText:
    def __init__(self, g, fg = (255, 255, 255), bg = (0, 0, 0), c = (0, 255, 0)):
        self.gui = g
        self.fg = fg
        self.bg = bg
        self.color = c

    def text(self, s, f, offset = 0, earlyAbort = True, yOff = 0, compat = True):
        if not earlyAbort:
            return self.gui.matrix.display.measure_text(s, scale=1)

        color = self.fg
        if isinstance(self.gui, MapperReduceBrightness):
            color = self.gui.adjust(color)

        pen = self.gui.matrix.display.create_pen(color[0], color[1], color[2])
        self.gui.matrix.display.set_pen(pen)

        self.gui.matrix.display.set_font(f)

        if not compat:
            # absolute positioning
            x = offset
            y = yOff
        else:
            # centered, like BDF DrawText implementation
            fontOff = 0
            if f == "bitmap6":
                fontOff = 3
            elif f == "bitmap8":
                fontOff = 4
            elif f == "bitmap14_outline":
                fontOff = 7

            x = -offset
            y = int(self.gui.height / 2 - fontOff + yOff)

        self.gui.matrix.display.text(s, x, y, scale=1)

if __name__ == "__main__":
    import time

    t = PicoMatrix(32, 32)
    s = PicoText(t)

    start = time.time()
    i = 0
    def helper():
        global s, start, i

        now = time.time()
        if ((now - start) > 2.0) or (now < start):
            start = now
            i = (i + 1) % 2

        if i == 0:
            s.text("Abgj6", "bitmap6", 0, True, 0, False)
            s.text("Abdgj8", "bitmap8", 0, True, 6 + 2, False)
            s.text("Ag14", "bitmap14_outline", 0, True, 6 + 2 + 8 + 1, False)
        else:
            s.text("Drinks:", "bitmap8", 0)

    t.loop(helper)
