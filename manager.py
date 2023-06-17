#!/usr/bin/env python3

import time

class Manager:
    def __init__(self, g):
        self.gui = g
        self.screens = []
        self.index = 0
        self.restart()

    def restart(self):
        self.lastTime = time.time()

    def add(self, s, d = None):
        v = (s, d)
        self.screens.append(v)

    def loop(self):
        self.screens[self.index][0].draw()

        if self.screens[self.index][1] == None:
            # let screen decide when it is done
            if self.screens[self.index][0].finished():
                self.index = (self.index + 1) % len(self.screens)
                self.lastTime = time.time()
                self.screens[self.index][0].restart()
        else:
            # use given timeout
            if (time.time() - self.lastTime) > self.screens[self.index][1]:
                self.index = (self.index + 1) % len(self.screens)
                self.lastTime = time.time()
                self.screens[self.index][0].restart()

if __name__ == "__main__":
    from splash import SplashScreen
    #from weather import WeatherScreen
    from draw import ScrollText
    from solid import Solid
    from life import GameOfLife

    import platform
    t = None
    if platform.machine() == "armv7l":
        from pi import PiMatrix
        t = PiMatrix()
    else:
        from test import TestGUI
        t = TestGUI()

    m = Manager(t)

    m.add(SplashScreen(t), 2)
    m.add(Solid(t, 1.0))

    #m.add(WeatherScreen(t), 4)
    #m.add(Solid(t, 1.0))

    m.add(ScrollText(t, "This appears once"))
    m.add(Solid(t, 1.0))

    m.add(ScrollText(t, "And this twice...", 2))
    m.add(Solid(t, 1.0))

    m.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), 20.0))
    m.add(Solid(t, 1.0))

    m.restart()
    t.debug_loop(m.loop)
