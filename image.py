#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

from PIL import Image
import time
import os

class ImageScreen:
    def __init__(self, g, p, t = 0.2, i = 1, to = 20.0, bg = None):
        self.gui = g
        self.time = t
        self.iterations = i
        self.timeout = to
        self.background = bg

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(scriptDir, "images", p)
        self.image = Image.open(self.path)
        print(p, self.image.width, self.image.height, self.image.is_animated, self.image.n_frames)

        self.restart()

    def restart(self):
        self.start = time.time()
        self.frame = time.time()
        self.count = 0
        self.done = 0
        self.image.seek(0)

    def finished(self):
        if self.done >= self.iterations:
            return True
        return (time.time() - self.start) >= self.timeout

    def draw(self):
        if self.image.is_animated:
            if (time.time() - self.frame) >= self.time:
                self.frame = time.time()
                self.count = (self.count + 1) % self.image.n_frames
                if self.count == 0:
                    self.done += 1

                self.image.seek(self.count)

        p = self.image.getpalette()
        for x in range(0, self.image.width):
            for y in range(0, self.image.height):
                v = self.image.getpixel((x, y))
                if isinstance(v, int):
                    c = None
                    if self.background != None:
                        if "transparency" in self.image.info:
                            if v == self.image.info["transparency"]:
                                c = self.background
                        else:
                            if v == self.image.info["background"]:
                                c = self.background
                    if c == None:
                        c = (p[v * 3 + 0], p[v * 3 + 1], p[v * 3 + 2])
                    self.gui.set_pixel(x, y, c)
                else:
                    self.gui.set_pixel(x, y, v)

if __name__ == "__main__":
    import util
    t = util.getTarget()

    from manager import Manager
    m = Manager(t)

    scriptDir = os.path.dirname(os.path.realpath(__file__))
    imageDir = os.path.join(scriptDir, "images")
    for f in os.listdir(os.fsencode(imageDir)):
        filename = os.fsdecode(f)
        m.add(ImageScreen(t, os.path.join(imageDir, filename)))

    m.restart()
    t.debug_loop(m.draw)
