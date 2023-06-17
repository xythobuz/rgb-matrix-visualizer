#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import requests

class CheckHTTP:
    def __init__(self, u, r = 600.0):
        self.url = u
        self.refresh = r
        self.successScreen = None
        self.failScreen = None
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
        if (self.response == None) or ((time.time() - self.start) >= self.refresh):
            self.start = time.time()
            try:
                r = requests.get(self.url)
                self.response = r.ok
            except:
                self.response = False

    def finished(self):
        self.request()
        if self.response:
            return self.successScreen.finished()
        else:
            return self.failScreen.finished()

    def draw(self):
        self.request()
        if self.response:
            return self.successScreen.draw()
        else:
            return self.failScreen.draw()

if __name__ == "__main__":
    from draw import ScrollText
    import util
    t = util.getTarget()

    d = CheckHTTP("http://xythobuz.de")
    d.success(ScrollText(t, "Success"))
    d.fail(ScrollText(t, "Failure"))

    t.debug_loop(d.draw)
