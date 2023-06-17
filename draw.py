#!/usr/bin/env python3

from bdfparser import Font
from PIL import Image
import os
import time

class DrawText:
    def __init__(self, g):
        self.gui = g

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        fontDir = os.path.join(scriptDir, "fonts")
        self.fonts = []
        for f in os.listdir(os.fsencode(fontDir)):
            filename = os.fsdecode(f)

            if not filename.lower().endswith(".bdf"):
                continue

            font = Font(os.path.join(fontDir, filename))
            #print(f"{filename} global size is "
            #    f"{font.headers['fbbx']} x {font.headers['fbby']} (pixel), "
            #    f"it contains {len(font)} glyphs.")

            # TODO hard-coded per-font offsets
            offset = 0
            if filename == "iv18x16u.bdf":
                offset = 6

            data = (font, offset)
            self.fonts.append(data)

    def getGlyph(self, c):
        f, o = self.fonts[0] # TODO selection of fonts
        g = f.glyph(c).draw()

        # invert color
        g = g.replace(1, 2).replace(0, 1).replace(2, 0)

        # render to pixel data
        img = Image.frombytes('RGBA',
                              (g.width(), g.height()),
                              g.tobytes('RGBA'))
        return (img, o)

    def drawGlyph(self, g, xOff, yOff):
        for x in range(0, g.width):
            for y in range(0, g.height):
                p = g.getpixel((x, y))
                self.gui.set_pixel(xOff + x, yOff + y, p)

    def text(self, s, offset = 0):
        w = 0
        for c in s:
            g, y = self.getGlyph(c)
            self.drawGlyph(g, -offset + w, y)
            w += g.width
        return w

class ScrollText:
    def __init__(self, g, t, i = 1, s = 100):
        self.gui = g
        self.drawer = DrawText(self.gui)
        self.text = t
        self.iterations = i
        self.speed = 1.0 / s

        self.width = self.drawer.text(self.text)
        self.restart()

    def restart(self):
        self.offset = -self.gui.width
        self.last = time.time()
        self.count = 0

    def finished(self):
        return (self.count >= self.iterations)

    def draw(self):
        if (time.time() - self.last) > self.speed:
            self.offset = (self.offset + 1)
            if self.offset >= self.width:
                self.offset = -self.gui.width
                self.count += 1

            self.last = time.time()

        self.drawer.text(self.text, self.offset)

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
