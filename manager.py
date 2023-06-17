#!/usr/bin/env python

import time

class Manager:
    def __init__(self, g):
        self.gui = g
        self.screens = []
        self.index = 0
        self.lastTime = time.time()

    def add(self, s, d = None):
        v = (s, d)
        self.screens.append(v)

    def loop(self):
        self.screens[self.index][0].draw()

        if self.screens[self.index][1] == None:
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
    from test import TestGUI
    from splash import SplashScreen
    #from weather import WeatherScreen
    from draw import ScrollText
    from solid import Solid

    t = TestGUI(32, 32)
    m = Manager(t)

    m.add(SplashScreen(t), 2)
    m.add(Solid(t, 3.0))

    #m.add(WeatherScreen(t), 4)
    #m.add(Solid(t, 3.0))

    m.add(ScrollText(t, "This appears once"))
    m.add(Solid(t, 3.0))

    m.add(ScrollText(t, "And this twice...", 2))
    m.add(Solid(t, 3.0))

    t.debug_loop(m.loop)
