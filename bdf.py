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

            # center vertically, in case of
            # multiple stacked panels
            if self.gui.height > self.gui.panelH:
                offset += int(self.gui.panelH / 2)

            font = Font(os.path.join(fontDir, filename))
            data = (font, offset, {}, spacing)
            self.fonts[filename[:-4]] = data

    # internal
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

    # internal
    def drawGlyph(self, g, xOff, yOff, spacing):
        for x in range(0, g.width + spacing):
            for y in range(0, g.height):
                pos = (xOff + x, yOff + y)
                if x >= g.width:
                    self.image.putpixel(pos, self.bg)
                else:
                    p = g.getpixel((x, y))
                    self.image.putpixel(pos, p)

    # text drawing API
    def setText(self, s, f):
        # calculate length of whole text
        w = 0
        h = 0
        for c in s:
            g, y, spacing = self.getGlyph(c, f)
            w += g.width + spacing
            if h < g.height:
                h = g.height

        # create new blank image buffer
        self.image = Image.new('RGBA', (w, h))

        # render glyphs into image
        w = 0
        for c in s:
            g, y, spacing = self.getGlyph(c, f)
            self.drawGlyph(g, w, 0, spacing)
            w += g.width + spacing
            self.yOffset = y

    # text drawing API
    def getDimensions(self):
        return (self.image.width, self.image.height)

    # text drawing API
    def draw(self, xOff = 0, yOff = 0):
        for x in range(0, self.image.width):
            xTarget = -xOff + x
            if xTarget < 0:
                continue
            if xTarget >= self.gui.width:
                break

            for y in range(0, self.image.height):
                yTarget = yOff + y + self.yOffset
                if yTarget < 0:
                    continue
                if yTarget >= self.gui.height:
                    break

                p = self.image.getpixel((x, y))
                self.gui.set_pixel(xTarget, yTarget, p)
