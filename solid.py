#!/usr/bin/env python3

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
    import platform
    t = None
    if platform.machine() == "armv7l":
        from pi import PiMatrix
        t = PiMatrix()
    else:
        from test import TestGUI
        t = TestGUI()
    d = ScrollText(t, "Hello, World!")
    t.debug_loop(d.draw)
