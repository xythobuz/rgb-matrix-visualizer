#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time

class Solid:
    def __init__(self, g, t = 1.0, c = (0, 0, 0)):
        self.gui = g
        self.time = t
        self.setColor(c)
        self.restart()

    def setColor(self, c):
        self.color = c

    def restart(self):
        self.start = time.time()

    def finished(self):
        return (time.time() - self.start) >= self.time

    def draw(self):
        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                self.gui.set_pixel(x, y, self.color)

if __name__ == "__main__":
    import util
    t = util.getTarget()

    d = Solid(t, 1.0, (0, 0, 0))

    colors = [
        (251, 72, 196), # camp23 pink
        (63, 255, 33), # camp23 green
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 255),
    ]

    s = time.time()
    ci = 0
    n = 0
    c = (0, 0, 0)
    def helper():
        global s, colors, ci, n, c

        if (time.time() - s) >= 0.1:
            s = time.time()
            n += 1
            if n >= 15:
                ci = (ci + 1) % len(colors)
                n = 0
                c = (0, 0, 0)
            elif n <= 10:
                c = colors[ci]
                c = (int(c[0] * (0.1 * n)), int(c[1] * (0.1 * n)), int(c[2] * (0.1 * n)))
            d.setColor(c)

        d.draw()

    t.loop(helper)
