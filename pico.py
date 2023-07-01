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
from machine import Pin, ADC
import math

# https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/examples/interstate75/75W/clock.py
@micropython.native  # noqa: F821
def from_hsv(h, s, v):
    i = math.floor(h * 6.0)
    f = h * 6.0 - i
    v *= 255.0
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    i = int(i) % 6
    if i == 0:
        return int(v), int(t), int(p)
    if i == 1:
        return int(q), int(v), int(p)
    if i == 2:
        return int(p), int(v), int(t)
    if i == 3:
        return int(p), int(q), int(v)
    if i == 4:
        return int(t), int(p), int(v)
    if i == 5:
        return int(v), int(p), int(q)

def batt_to_color(batt):
    h = batt[0] / 100.0 * 0.3333
    r, g, b = from_hsv(h, 1.0, 1.0)
    return r, g, b

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
        self.ledRefresh = 0.5

        self.adc = ADC(26)
        self.battState = None
        self.battTime = time.time()
        self.battRefresh = 10

        self.loop_start() # initialize with blank image for ScrollText constructor

    def battery(self):
        n = const(10)
        bits = const(10)
        raw = 0
        for i in range(0, n):
            raw += self.adc.read_u16() >> (16 - bits)
            time.sleep(0.1 / n)
        raw /= n

        v_adc_ref = const(3.3) # V
        v_adc = (raw / ((1 << bits) - 1)) * v_adc_ref

        r1 = const(27.0) # kOhm
        r2 = const(5.6) # kOhm
        v_bat_uncal = (v_adc * (r1 + r2)) / r2

        # Calibration
        # TODO supports only 2 points
        cal_pts = [
            #  adc,   bat
            (13.65, 15.46),
            (13.60, 15.34),
            # TODO better values
        ]

        # https://www.ti.com/europe/downloads/f2810_12_calibration_10.pdf
        gain = (cal_pts[0][1] - cal_pts[1][1]) / (cal_pts[0][0] - cal_pts[1][0])
        offset = cal_pts[1][1] - cal_pts[1][0] * gain
        v_bat = v_bat_uncal * gain + offset

        # TODO auto-detect cell count
        n_lipo = const(4) # 4S
        v_cell = v_bat / n_lipo

        v_cell_min = const(3.25)
        v_cell_max = const(4.2)
        p_cell = (v_cell - v_cell_min) / (v_cell_max - v_cell_min) * 100.0
        p_cell = max(min(p_cell, 100.0), 0.0)

        ret = (p_cell, v_cell, v_bat)

        r, g, b = batt_to_color(ret)
        self.matrix.set_led(r, g, b)

        return ret

    def batteryCache(self, refresh = False):
        now = time.time()
        if (self.battState == None) or ((now - self.battTime) >= self.battRefresh) or (now < self.battTime) or refresh:
            self.battTime = now
            self.battState = self.battery()
        return self.battState

    def heartbeat(self):
        now = time.time()
        if ((now - self.ledTime) >= self.ledRefresh) or (now < self.ledTime):
            self.ledTime = now
            self.led.toggle()

    def loop_start(self):
        self.matrix.display.set_pen(self.black)
        self.matrix.display.clear()
        self.matrix.display.set_pen(self.white)

        return False # no input, never quit on our own

    def loop_end(self):
        self.matrix.update()

        # LED heartbeat blink
        self.heartbeat()

        # update battery if necessary
        self.batteryCache(False)

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

class PicoText:
    def __init__(self, g, fg = (255, 255, 255), bg = (0, 0, 0), c = (0, 255, 0)):
        self.gui = g
        self.fg = fg
        self.bg = bg
        self.color = c

    def text(self, s, f, offset = 0, earlyAbort = True, yOff = 0, compat = True):
        if not earlyAbort:
            self.gui.matrix.display.set_font(f)
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

class PicoBatt:
    def __init__(self, g, ti = 5.0, tt = 5.0):
        self.gui = g
        self.timeImage = ti
        self.timeText = tt
        self.text = PicoText(self.gui)
        self.restart()

    def restart(self):
        self.start = time.time()

    def finished(self):
        now = time.time()
        return ((now - self.start) >= (self.timeText + self.timeImage)) or (now < self.start)

    def drawText(self, refresh = False):
        batt = self.gui.batteryCache(refresh)
        c = batt_to_color(batt)

        self.text.fg = (255, 255, 255)
        self.text.text(                  "Batt:", "bitmap8", 0, True, 8 * 0, False)

        self.text.fg = c
        self.text.text("{:.2f}%".format(batt[0]), "bitmap8", 0, True, 8 * 1, False)
        self.text.text("{:.2f}V".format(batt[1]), "bitmap8", 0, True, 8 * 2, False)
        self.text.text("{:.2f}V".format(batt[2]), "bitmap8", 0, True, 8 * 3, False)

    def drawImage(self, refresh = False):
        x_off = const(1)
        y_off = const(16)
        nub_w = const(3)
        nub_h = const(6)

        w = self.gui.width - x_off * 2
        h = self.gui.height - y_off

        batt = self.gui.batteryCache(refresh)
        c = batt_to_color(batt)
        fill_w = int(batt[0] / 100.0 * (w - nub_w))

        s = "{:.0f}%".format(batt[0])
        s_w = self.text.text(s, "bitmap14_outline", 0, False)
        self.text.fg = (255, 255, 255)
        self.text.text(s, "bitmap14_outline", int((self.gui.width - s_w) / 2), True, 1, False)

        for x in range(0, w - nub_w):
            for y in range(0, h):
                if (x == 0) or (x == (w - nub_w - 1)) or (y == 0) or (y == (h - 1)) or (x < fill_w):
                    self.gui.set_pixel(x + x_off, y + y_off, c)

        for x in range(0, nub_w):
            for y in range(0, nub_h):
                self.gui.set_pixel(x + x_off + w - nub_w, y + y_off + int((h - nub_h) / 2), c)

    def draw(self, refresh = False):
        now = time.time()
        if (now - self.start) < self.timeImage:
            self.drawImage(refresh)
        else:
            self.drawText(refresh)

if __name__ == "__main__":
    import time

    t = PicoMatrix(32, 32)
    s = PicoText(t)
    b = PicoBatt(t, 10.0, 10.0)

    start = time.time()
    i = 0
    def helper():
        global s, start, i, b

        now = time.time()
        if ((now - start) > 5.0) or (now < start):
            start = now
            i = (i + 1) % 6
            if i == 0:
                b.restart()

        if i < 4:
            b.draw(True)
            time.sleep(1.0)
        elif i == 4:
            s.text("Abgj6", "bitmap6", 0, True, 0, False)
            s.text("Abdgj8", "bitmap8", 0, True, 6 + 2, False)
            s.text("Ag14", "bitmap14_outline", 0, True, 6 + 2 + 8 + 1, False)
        else:
            s.text("Drinks:", "bitmap8", 0)

    t.loop(helper)
