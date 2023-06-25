#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import util

class CheckHTTP:
    def __init__(self, u, r = 600.0):
        self.url = u
        self.refresh = r
        self.successScreen = None
        self.failScreen = None
        self.get = util.getRequests()

        self.restart()

    def success(self, s):
        self.successScreen = s

    def fail(self, f):
        self.failScreen = f

    def restart(self):
        self.start = time.time()
        self.response = None
        self.request()

        if self.successScreen != None:
            self.successScreen.restart()
        if self.failScreen != None:
            self.failScreen.restart()

    def request(self):
        if self.get == None:
            return

        if (self.response == None) or ((time.time() - self.start) >= self.refresh):
            self.start = time.time()
            try:
                r = self.get(self.url)
                self.response = (r.status_code < 400)
            except:
                self.response = False

    def finished(self):
        if self.get == None:
            return True

        self.request()
        if self.response:
            return self.successScreen.finished()
        else:
            return self.failScreen.finished()

    def draw(self):
        if self.get == None:
            return

        self.request()
        if self.response:
            self.successScreen.draw()
        else:
            self.failScreen.draw()

if __name__ == "__main__":
    from draw import ScrollText
    import util
    t = util.getTarget()

    d = CheckHTTP("http://xythobuz.de")
    d.success(ScrollText(t, "Success", "ib8x8u"))
    d.fail(ScrollText(t, "Failure", "ib8x8u"))

    t.loop(d.draw)
