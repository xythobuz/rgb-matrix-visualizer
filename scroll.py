#!/usr/bin/env python3

# Uses the Python BDF format bitmap font parser:
# https://github.com/tomchen/bdfparser
#
# And the pillow Python Imaging Library:
# https://github.com/python-pillow/Pillow
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import os
import time
import util

class ScrollText:
    def __init__(self, g, t, f, i = 1, s = 75, fg = (255, 255, 255), bg = (0, 0, 0)):
        DrawText = util.getTextDrawer()

        self.gui = g
        self.drawer = DrawText(self.gui, fg, bg)
        self.iterations = i
        self.speed = 1.0 / s

        self.setText(t, f)
        self.restart()

    def setText(self, t, f):
        self.text = t
        self.font = f
        self.drawer.setText(t, f)
        self.width, height = self.drawer.getDimensions()

    def restart(self):
        self.offset = -self.gui.width
        self.last = time.time()
        self.count = 0

    def finished(self):
        return (self.count >= self.iterations)

    def draw(self):
        now = time.time()
        if (now - self.last) > self.speed:
            off = (now - self.last) / self.speed
            self.offset += int(off)
            self.last = now
            if self.offset >= self.width:
                self.offset = -self.gui.width
                self.count += 1

        self.drawer.draw(self.offset)

if __name__ == "__main__":
    import util
    t = util.getTarget()

    # show splash screen while initializing
    from splash import SplashScreen
    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    from manager import Manager
    m = Manager(t)

    scriptDir = os.path.dirname(os.path.realpath(__file__))
    fontDir = os.path.join(scriptDir, "fonts")
    for f in os.listdir(os.fsencode(fontDir)):
        filename = os.fsdecode(f)
        if not filename.endswith(".bdf"):
            continue

        fontName = filename[:-4]
        s = fontName + " Abcdefgh " + fontName
        m.add(ScrollText(t, s, fontName, 1, 50, (0, 255, 0), (0, 0, 25)))

    m.restart()
    util.loop(t, m.draw)
