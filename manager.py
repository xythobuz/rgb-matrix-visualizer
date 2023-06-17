#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time

class Manager:
    def __init__(self, g):
        self.gui = g
        self.screens = []
        self.restart()

    def restart(self):
        self.index = 0
        self.done = False
        self.lastTime = time.time()
        if len(self.screens) > 0:
            self.screens[0][0].restart()

    def finished(self):
        return self.done

    def add(self, s, d = None):
        v = (s, d)
        self.screens.append(v)

    def draw(self):
        self.screens[self.index][0].draw()

        if self.screens[self.index][1] == None:
            # let screen decide when it is done
            if self.screens[self.index][0].finished():
                self.lastTime = time.time()
                self.index = (self.index + 1) % len(self.screens)
                self.done = (self.index == 0)
                self.screens[self.index][0].restart()
        else:
            # use given timeout
            if (time.time() - self.lastTime) > self.screens[self.index][1]:
                self.lastTime = time.time()
                self.index = (self.index + 1) % len(self.screens)
                self.done = (self.index == 0)
                self.screens[self.index][0].restart()

if __name__ == "__main__":
    from splash import SplashScreen
    from draw import ScrollText
    from solid import Solid
    from life import GameOfLife

    import util
    t = util.getTarget()

    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    m = Manager(t)

    m.add(ScrollText(t, "This appears once"))
    m.add(Solid(t, 1.0))

    m.add(ScrollText(t, "And this twice...", 2))
    m.add(Solid(t, 1.0))

    m.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), 20.0, True))
    m.add(Solid(t, 1.0))

    sub = Manager(t)
    sub.add(ScrollText(t, "Hello"))
    sub.add(Solid(t, 1.0, (0, 255, 0)))
    sub.add(ScrollText(t, "World"))
    sub.add(Solid(t, 1.0, (0, 0, 255)))
    m.add(sub)
    m.add(Solid(t, 1.0))

    m.restart()
    t.debug_loop(m.draw)
