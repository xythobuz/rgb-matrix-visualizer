#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

from bdfparser import Font
from PIL import Image
import os
import time

class DrawText:
    def __init__(self, g):
        self.gui = g

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        fontDir = os.path.join(scriptDir, "fonts")
        self.fonts = {}
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
            elif filename == "ib8x8u.bdf":
                offset = 10

            data = (font, offset, {})
            self.fonts[filename[:-4]] = data

    def getGlyph(self, c, font):
        f, o, cache = self.fonts[font]

        # only render glyphs once, cache resulting image data
        if not c in cache:
            g = f.glyph(c).draw()

            # invert color
            g = g.replace(1, 2).replace(0, 1).replace(2, 0)

            # render to pixel data
            img = Image.frombytes('RGBA',
                                (g.width(), g.height()),
                                g.tobytes('RGBA'))

            cache[c] = img

        return (cache[c], o)

    def drawGlyph(self, g, xOff, yOff):
        if xOff >= self.gui.width:
            return

        for x in range(0, g.width):
            for y in range(0, g.height):
                xTarget = xOff + x
                if (xTarget < 0) or (xTarget >= self.gui.width):
                    continue

                p = g.getpixel((x, y))
                self.gui.set_pixel(xTarget, yOff + y, p)

    def text(self, s, f, offset = 0, earlyAbort = True, yOff = 0):
        w = 0
        for c in s:
            xOff = -offset + w
            if earlyAbort:
                if xOff >= self.gui.width:
                    break

            g, y = self.getGlyph(c, f)
            w += g.width

            if xOff >= -10: # some wiggle room so chars dont disappear
                self.drawGlyph(g, xOff, y + yOff)
        return w

class ScrollText:
    def __init__(self, g, t, f, i = 1, s = 75):
        self.gui = g
        self.drawer = DrawText(self.gui)
        self.text = t
        self.font = f
        self.iterations = i
        self.speed = 1.0 / s

        self.width = self.drawer.text(self.text, self.font, 0, False)
        self.restart()

    def restart(self):
        self.offset = -self.gui.width
        self.last = time.time()
        self.count = 0

    def finished(self):
        return (self.count >= self.iterations)

    def draw(self):
        if (time.time() - self.last) > self.speed:
            off = (time.time() - self.last) / self.speed
            self.offset += int(off)
            self.last = time.time()
            if self.offset >= self.width:
                self.offset = -self.gui.width
                self.count += 1

        self.drawer.text(self.text, self.font, self.offset, True)

if __name__ == "__main__":
    import util
    t = util.getTarget()

    #d = ScrollText(t, "This is a long scrolling text. Is it too fast or maybe too slow?", "iv18x16u")
    d = ScrollText(t, "This is a long scrolling text. Is it too fast or maybe too slow?", "ib8x8u")
    t.debug_loop(d.draw)
