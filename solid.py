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
        self.color = c
        self.restart()

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

    d = Solid(t, 1.0, (0, 255, 0))
    t.debug_loop(d.draw)
