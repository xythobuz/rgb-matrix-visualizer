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

from bdfparser import Font
from PIL import Image
import os
import time

class DrawText:
    def __init__(self, g, fg = (255, 255, 255), bg = (0, 0, 0), c = (0, 255, 0)):
        self.gui = g
        self.fg = fg
        self.bg = bg
        self.color = c

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        fontDir = os.path.join(scriptDir, "fonts")
        self.fonts = {}
        for f in os.listdir(os.fsencode(fontDir)):
            filename = os.fsdecode(f)

            if not filename.lower().endswith(".bdf"):
                continue

            # TODO hard-coded per-font offsets and spacing adjustment
            offset = 0
            spacing = 0
            if filename == "iv18x16u.bdf":
                offset = 6
            elif filename == "ib8x8u.bdf":
                offset = 10
            elif filename == "lemon.bdf":
                offset = 8
                spacing = -3
            elif filename == "antidote.bdf":
                offset = 9
                spacing = -1
            elif filename == "uushi.bdf":
                offset = 8
                spacing = -2
            elif filename == "tom-thumb.bdf":
                offset = 12
                spacing = 2

            font = Font(os.path.join(fontDir, filename))
            data = (font, offset, {}, spacing)
            self.fonts[filename[:-4]] = data

    def getGlyph(self, c, font):
        if not isinstance(font, str):
            # fall-back to first available font
            f, offset, cache, spacing = next(iter(self.fonts))
        else:
            # users font choice
            f, offset, cache, spacing = self.fonts[font]

        # only render glyphs once, cache resulting image data
        if not c in cache:
            g = f.glyph(c).draw()

            # invert color
            g = g.replace(1, 2).replace(0, 1).replace(2, 0)

            # render to pixel data
            bytesdict = {
                0: int(self.fg[2] << 16 | self.fg[1] << 8 | self.fg[0]).to_bytes(4, byteorder = "little"),
                1: int(self.bg[2] << 16 | self.bg[1] << 8 | self.bg[0]).to_bytes(4, byteorder = "little"),
                2: int(self.color[2] << 16 | self.color[1] << 8 | self.color[0]).to_bytes(4, byteorder = "little"),
            }
            img = Image.frombytes('RGBA',
                                (g.width(), g.height()),
                                g.tobytes('RGBA', bytesdict))
            cache[c] = img

        return (cache[c], offset, spacing)

    def drawGlyph(self, g, xOff, yOff, spacing):
        if xOff >= self.gui.width:
            return

        for x in range(0, g.width):
            for y in range(0, g.height):
                xTarget = xOff + x
                if (xTarget < 0) or (xTarget >= self.gui.width):
                    continue

                p = g.getpixel((x, y))
                self.gui.set_pixel(xTarget, yOff + y, p)

        for x in range(0, spacing):
            for y in range(0, g.height):
                self.gui.set_pixel(xOff + x + g.width, yOff + y, self.bg)

    def text(self, s, f, offset = 0, earlyAbort = True, yOff = 0):
        w = 0
        for c in s:
            xOff = -offset + w
            if earlyAbort:
                if xOff >= self.gui.width:
                    break

            g, y, spacing = self.getGlyph(c, f)
            w += g.width + spacing

            if xOff >= -16: # some wiggle room so chars dont disappear
                self.drawGlyph(g, xOff, y + yOff, spacing)
        return w

class ScrollText:
    def __init__(self, g, t, f, i = 1, s = 75, fg = (255, 255, 255), bg = (0, 0, 0)):
        self.gui = g
        self.drawer = DrawText(self.gui, fg, bg)
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

    from splash import SplashScreen
    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    from manager import Manager
    m = Manager(t)

    m.add(ScrollText(t, "tom-thumb Abcdefgh tom-thumb", "tom-thumb",
                     1, 75, (0, 255, 0), (0, 0, 255)))
    m.add(ScrollText(t, "antidote Abcdefgh antidote", "antidote",
                     1, 75, (0, 255, 0), (0, 0, 255)))
    m.add(ScrollText(t, "uushi Abcdefgh uushi", "uushi",
                     1, 75, (0, 255, 0), (0, 0, 255)))
    m.add(ScrollText(t, "lemon Abcdefgh lemon", "lemon",
                     1, 75, (0, 255, 0), (0, 0, 255)))
    m.add(ScrollText(t, "ib8x8u Abcdefgh ib8x8u", "ib8x8u",
                     1, 75, (0, 255, 0), (0, 0, 255)))
    m.add(ScrollText(t, "iv18x16u Abcdefgh iv18x16u", "iv18x16u",
                     1, 75, (0, 255, 0), (0, 0, 255)))

    m.restart()
    t.debug_loop(m.draw)
