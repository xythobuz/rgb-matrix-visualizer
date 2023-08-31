#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import random

class Manager:
    def __init__(self, g, i = None, ss = 2, randomize = False):
        self.gui = g
        self.input = i
        self.step_size = ss
        self.randomize = randomize
        self.screens = []

        if self.randomize:
            random.seed()

        self.restart()

    def restart(self):
        if self.randomize and (len(self.screens) > 0):
            self.index = int(random.randrange(0, len(self.screens) / self.step_size) * self.step_size)
        else:
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
            self.switch_to(-1, False)
        elif keys["r"] and (not self.old_keys["r"]):
            self.switch_to(1, False)

        self.old_keys = keys.copy()

    def child_count(self, i, update_flag):
        if i > 0:
            if update_flag:
                index = self.index
                l = len(self.screens)
            else:
                index = int(self.index / self.step_size)
                l = int(len(self.screens) / self.step_size)
            #print(self.index, len(self.screens), index, l, (index >= (l - 1)))
            return index >= (l - 1)
        else:
            return self.index <= 0

    def switch_this_to(self, i, update_flag):
        self.lastTime = time.time()

        if update_flag:
            if self.randomize:
                if (self.index % self.step_size) == (self.step_size - 1):
                    # end of "segment", now go to random next segment
                    new_index = self.index
                    while (new_index == self.index) and (len(self.screens) > self.step_size):
                        new_index = int(random.randrange(0, len(self.screens) / self.step_size) * self.step_size)
                    self.index = new_index
                else:
                    # still in "segment", so just normal iteration
                    self.index = (self.index + i) % len(self.screens)
            else:
                # go through all for normal operation
                self.index = (self.index + i) % len(self.screens)
        else:
            # use step_size for button presses
            self.index = int((int(self.index / self.step_size) + i) * self.step_size) % len(self.screens)

        self.done = self.child_count(i, update_flag)

        #print("Manager ", len(self.screens), " switch to ", self.index, update_flag)

        self.screens[self.index][0].restart()

    def switch_to(self, i, update_flag):
        c = self.screens[self.index][0]
        if hasattr(c, "switch_to") and hasattr(c, "child_count"):
            if c.child_count(i, update_flag):
                self.switch_this_to(i, update_flag)
            else:
                c.switch_to(i, update_flag)
        else:
            self.switch_this_to(i, update_flag)

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
    i = util.getInput()
    t = util.getTarget(i)

    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    sub = Manager(t)
    sub.add(ScrollText(t, "Hello", "ib8x8u"))
    sub.add(Solid(t, 1.0, (0, 255, 0)))
    sub.add(ScrollText(t, "World", "ib8x8u"))
    sub.add(Solid(t, 1.0, (0, 0, 255)))

    m = Manager(t, i)
    m.add(sub)
    m.add(Solid(t, 1.0, (255, 255, 0)))

    m.add(ScrollText(t, "This appears once", "ib8x8u"))
    m.add(Solid(t, 1.0))

    m.add(ScrollText(t, "And this twice...", "ib8x8u", 2))
    m.add(Solid(t, 1.0))

    m.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), 5.0, True))
    m.add(Solid(t, 1.0))

    m.restart()
    util.loop(t, m.draw)
