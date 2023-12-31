#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import util
import sys

class CheckHTTP:
    def __init__(self, u, r = 600.0):
        self.url = u
        self.refresh = r
        self.successScreen = None
        self.failScreen = None
        self.response = None
        self.get, post = util.getRequests()

        self.restart()

    def success(self, s):
        self.successScreen = s

    def fail(self, f):
        self.failScreen = f

    # Compatibility to Manager button events
    def child_count(self, i, update_flag):
        self.request()
        if self.response:
            if hasattr(self.successScreen, "child_count"):
                return self.successScreen.child_count(i, update_flag)
        else:
            if hasattr(self.failScreen, "child_count"):
                return self.failScreen.child_count(i, update_flag)
        return True

    # Compatibility to Manager button events
    def switch_to(self, i, update_flag):
        self.request()
        if self.response:
            if hasattr(self.successScreen, "switch_to"):
                self.successScreen.switch_to(i, update_flag)
        else:
            if hasattr(self.failScreen, "switch_to"):
                self.failScreen.switch_to(i, update_flag)

    def restart(self):
        self.start = time.time()

        # when set to None here, manager will cause re-request every time
        # we don't do it, caching the response for the full refresh time.
        # this assumes the URL never changes, of course.
        #self.response = None

        self.request()

        if self.successScreen != None:
            self.successScreen.restart()
        if self.failScreen != None:
            self.failScreen.restart()

    def request(self):
        if self.get == None:
            return

        now = time.time()
        if (self.response == None) or ((now - self.start) >= self.refresh) or (now < self.start):
            self.start = now
            try:
                print("Refreshing " + self.url)
                r = self.get(self.url)
                r.close()
                print("Response: " + str(r.status_code))
                self.response = (r.status_code < 400)
            except Exception as e:
                print()
                if hasattr(sys, "print_exception"):
                    sys.print_exception(e)
                else:
                    print(e)
                print()

                self.response = False

    def finished(self):
        if self.get == None:
            return self.failScreen.finished()

        self.request()
        if self.response:
            return self.successScreen.finished()
        else:
            return self.failScreen.finished()

    def draw(self):
        if self.get == None:
            self.failScreen.draw()
            return

        self.request()
        if self.response:
            self.successScreen.draw()
        else:
            self.failScreen.draw()

if __name__ == "__main__":
    from solid import Solid
    import util
    t = util.getTarget()

    # show splash screen while connecting to WiFi on Pico
    from splash import SplashScreen
    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    d = CheckHTTP("http://xythobuz.de")
    d.success(Solid(t, 1.0, (0, 255, 0)))
    d.fail(Solid(t, 1.0, (255, 0, 0)))

    util.loop(t, d.draw)
