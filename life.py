#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import random

class GameOfLife:
    def __init__(self, g, f = 20, c1 = (255, 255, 255), c2 = (0, 0, 0), t = 20.0, rc = None, bt = 45.0):
        self.gui = g
        self.interval = 1.0 / f
        self.setColors(c1, c2)
        self.timeout = t
        self.randomizeColors = rc
        self.backupTimeout = bt
        random.seed()
        self.restart()

        self.editDistFinish = 20

    def restart(self):
        self.data = self.init()
        self.start = time.time()
        self.last = time.time()
        self.lastColor = time.time()
        self.done = False
        self.lastDiff = 100

        if self.randomizeColors != None:
            self.randomize()

    def setColors(self, c1 = (255, 255, 255), c2 = (0, 0, 0)):
        self.colorFG = c1
        self.colorBG = c2

    def randomize(self):
        c1 = (random.randrange(0, 16) << 4, random.randrange(0, 16) << 4, random.randrange(0, 16) << 4)
        c2 = (random.randrange(0, 16) << 0, random.randrange(0, 16) << 0, random.randrange(0, 16) << 0)
        self.setColors(c1, c2)

    def init(self):
        data = []
        for x in range(0, self.gui.width):
            d = []
            for y in range(0, self.gui.height):
                v = False
                if random.randrange(0, 2) == 1:
                    v = True

                d.append(v)
            data.append(d)
        return data

    def finished(self):
        if self.done:
            return True

        if self.timeout != None:
            if (time.time() - self.start) > self.timeout:
                return True
        else:
            if self.lastDiff < self.editDistFinish:
                return True
            if (time.time() - self.start) > self.backupTimeout:
                return True

        return False

    def alive(self, data, x, y):
        if (x < 0) or (y < 0) or (x >= self.gui.width) or (y >= self.gui.height):
            return False
        return data[x][y]

    def live_neighbours(self, data, x, y):
        c = 0
        for xOff in range(-1, 2):
            for yOff in range(-1, 2):
                if (xOff == 0) and (yOff == 0):
                    continue
                if self.alive(data, x + xOff, y + yOff):
                    c += 1
                    if c == 4:
                        # 4 or more is not interesting for us
                        break
        return c

    def step(self):
        # deep copy
        old = [x[:] for x in self.data]

        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                ln = self.live_neighbours(old, x, y)
                if old[x][y] and ((ln == 2) or (ln == 3)):
                    # Any live cell with two or three live neighbours survives.
                    self.data[x][y] = True
                elif (not old[x][y]) and (ln == 3):
                    # Any dead cell with three live neighbours becomes a live cell.
                    self.data[x][y] = True
                else:
                    # All other live cells die in the next generation. Similarly, all other dead cells stay dead.
                    self.data[x][y] = False

        # compare new and old states
        diff = 0
        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                if self.data[x][y] != old[x][y]:
                    diff += 1
                    if self.timeout == None:
                        if diff >= self.editDistFinish:
                            break
                    else:
                        if diff >= 1:
                            break
        self.done = (diff == 0)
        self.lastDiff = diff

    def draw(self):
        now = time.time()
        if (now - self.last) > self.interval:
            self.last = now
            self.step()

        if (self.randomizeColors != None) and (self.randomizeColors != True):
            now = time.time()
            if (now - self.lastColor) > self.randomizeColors:
                self.lastColor = now
                self.randomize()

        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                if self.data[x][y]:
                    self.gui.set_pixel(x, y, self.colorFG)
                else:
                    self.gui.set_pixel(x, y, self.colorBG)

if __name__ == "__main__":
    import util
    t = util.getTarget()

    g = GameOfLife(t, 20, (255, 255, 255), (0, 0, 0), None, 2.0)

    def helper():
        if g.finished():
            g.restart()
        g.draw()

    t.loop(helper)
