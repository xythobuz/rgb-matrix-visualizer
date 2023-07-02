#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time

class Manager:
    def __init__(self, g, i = None, ss = 2):
        self.gui = g
        self.input = i
        self.step_size = ss
        self.screens = []
        self.restart()

    def restart(self):
        self.index = 0
        self.done = False
        self.lastTime = time.time()
        self.old_keys = {
            "l": False,
            "r": False,
        }

        #print("Manager ", len(self.screens), " reset to ", self.index)

        if len(self.screens) > 0:
            self.screens[0][0].restart()

    def finished(self):
        return self.done

    def add(self, s, d = None):
        v = (s, d)
        self.screens.append(v)

    def buttons(self):
        keys = self.input.get()

        if keys["l"] and (not self.old_keys["l"]):
            c = self.screens[self.index][0]
            if hasattr(c, "switch_to") and hasattr(c, "child_count"):
                if c.child_count(-1):
                    self.switch_to(-1, False)
                else:
                    c.switch_to(-1, False)
            else:
                self.switch_to(-1, False)
        elif keys["r"] and (not self.old_keys["r"]):
            c = self.screens[self.index][0]
            if hasattr(c, "switch_to") and hasattr(c, "child_count"):
                if c.child_count(1):
                    self.switch_to(1, False)
                else:
                    c.switch_to(1, False)
            else:
                self.switch_to(1, False)

        self.old_keys = keys.copy()

    def child_count(self, i):
        if i > 0:
            index = int(self.index / self.step_size)
            l = int(len(self.screens) / self.step_size)
            return index >= (l - 1)
        else:
            return self.index <= 0

    def switch_to(self, i, update_flag):
        self.lastTime = time.time()
        self.index = int((int(self.index / self.step_size) + i) * self.step_size) % len(self.screens)

        #print("Manager ", len(self.screens), " switch to ", self.index, update_flag)

        if update_flag:
            self.done = (self.index == 0)

        self.screens[self.index][0].restart()

    def draw(self):
        if self.input != None:
            self.buttons()

        self.screens[self.index][0].draw()

        if self.screens[self.index][1] == None:
            # let screen decide when it is done
            if self.screens[self.index][0].finished():
                self.switch_to(1, True)
        else:
            # use given timeout
            now = time.time()
            if ((now - self.lastTime) > self.screens[self.index][1]) or (now < self.lastTime):
                self.switch_to(1, True)

if __name__ == "__main__":
    from splash import SplashScreen
    from scroll import ScrollText
    from solid import Solid
    from life import GameOfLife

    import util
    t = util.getTarget()

    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    m = Manager(t)

    m.add(ScrollText(t, "This appears once", "ib8x8u"))
    m.add(Solid(t, 1.0))

    m.add(ScrollText(t, "And this twice...", "ib8x8u", 2))
    m.add(Solid(t, 1.0))

    m.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), 20.0, True))
    m.add(Solid(t, 1.0))

    sub = Manager(t)
    sub.add(ScrollText(t, "Hello", "ib8x8u"))
    sub.add(Solid(t, 1.0, (0, 255, 0)))
    sub.add(ScrollText(t, "World", "ib8x8u"))
    sub.add(Solid(t, 1.0, (0, 0, 255)))
    m.add(sub)
    m.add(Solid(t, 1.0))

    m.restart()
    t.loop(m.draw)
