#!/usr/bin/env python3

# Uses the Python QR code image generator:
# https://github.com/lincolnloop/python-qrcode
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import qrcode
import util

class QRScreen:
    def __init__(self, g, d, t = 10.0, h = None, f = None, c1 = (0, 0, 0), c2 = (255, 255, 255)):
        self.gui = g
        self.time = t
        self.heading = h
        self.font = f
        self.c1 = c1
        self.c2 = c2

        qr = qrcode.QRCode(
            box_size = 1,
            border = 0,
        )
        qr.add_data(d)
        qr.make(fit = True)

        if util.isPi():
            # work-around for weird bug in old qrcode lib?
            if (self.c1 == (0, 0, 0)) and (self.c2 == (255, 255, 255)):
                self.image = qr.make_image(fill_color = "black", back_color = "white")
                self.c1 = (0, 0, 0)
                self.c2 = (255, 255, 255)
            elif (self.c1 == (255, 255, 255)) and (self.c2 == (0, 0, 0)):
                self.image = qr.make_image(fill_color = "white", back_color = "black")
                self.c1 = (255, 255, 255)
                self.c2 = (0, 0, 0)
            else:
                raise RuntimeError("QR colors other than black/white not supported on Pi")
        else:
            self.image = qr.make_image(fill_color = self.c1, back_color = self.c2)

        if self.heading != None:
            DrawText = util.getTextDrawer()
            self.text = DrawText(self.gui, self.c1, self.c2)
            self.yOff = self.gui.height - self.image.height
        else:
            self.yOff = int((self.gui.height - self.image.height) / 2)

        self.xOff = int((self.gui.width - self.image.width) / 2)

        self.restart()

    def restart(self):
        self.start = time.time()

    def finished(self):
        return (time.time() - self.start) >= self.time

    def draw(self):
        # fill border, if needed
        if self.c2 != (0, 0, 0):
            for x in range(0, self.gui.width):
                for y in range(0, self.yOff):
                    self.gui.set_pixel(x, y, self.c2)
                for y in range(0, self.gui.height - self.image.height - self.yOff):
                    self.gui.set_pixel(x, y + self.yOff + self.image.height, self.c2)
            for y in range(0, self.image.height):
                for x in range(0, self.xOff):
                    self.gui.set_pixel(x, y + self.yOff, self.c2)
                for x in range(0, self.gui.width - self.image.width - self.xOff):
                    self.gui.set_pixel(x + self.xOff + self.image.width, y + self.yOff, self.c2)

        if self.heading != None:
            self.text.text(self.heading, self.font, 0, True, -10)

        for x in range(0, self.image.width):
            for y in range(0, self.image.height):
                v = self.image.getpixel((x, y))
                if isinstance(v, int):
                    v = (v, v, v)
                self.gui.set_pixel(x + self.xOff, y + self.yOff, v)

if __name__ == "__main__":
    import util
    t = util.getTarget()

    d = QRScreen(t, "Hello World", 10.0, "Drinks:", "tom-thumb", (255, 255, 255), (0, 0, 0))
    t.loop(d.draw)
