#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

class SplashScreen:
    def __init__(self, g):
        self.gui = g
        self.width = self.gui.panelW
        self.height = self.gui.panelH

    def draw(self):
        # repeat the image on each available panel
        for x in range(0, int(self.gui.width / self.width)):
            for y in range(0, int(self.gui.height / self.height)):
                self.drawOnce(x * self.width, y * self.height)

    def drawOnce(self, x, y):
        self.gui.set_pixel(             x,               y, (255, 255, 255))
        self.gui.set_pixel(             x, self.height - 1 + y, (  0,   0, 255))
        self.gui.set_pixel(self.width - 1 + x,               y, (255,   0,   0))
        self.gui.set_pixel(self.width - 1 + x, self.height - 1 + y, (  0, 255,   0))

        for i in range(0, int(min(self.width, self.height) / 3)):
            self.gui.set_pixel((self.width / 2) - 1 + i + x, (self.height / 2) - 1 + i + y, (255, 255, 255))
            self.gui.set_pixel((self.width / 2) - 1 - i + x, (self.height / 2) - 1 - i + y, (255, 255, 255))
            self.gui.set_pixel((self.width / 2) - 1 + i + x, (self.height / 2) - 1 - i + y, (255, 255, 255))
            self.gui.set_pixel((self.width / 2) - 1 - i + x, (self.height / 2) - 1 + i + y, (255, 255, 255))

    def finished(self):
        return True

    def restart(self):
        pass

if __name__ == "__main__":
    import util
    t = util.getTarget()
    s = SplashScreen(t)
    t.loop(s.draw)
