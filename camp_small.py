#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    from splash import SplashScreen
    from draw import ScrollText
    from solid import Solid
    from life import GameOfLife
    from net import CheckHTTP
    from image import ImageScreen
    from qr import QRScreen
    from manager import Manager

    url = "http://ubabot.frubar.net"

    import util
    t = util.getTarget()

    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    success = Manager(t)
    success.add(ImageScreen(t, "drinka.gif", 0.2, 2, 20.0))
    success.add(Solid(t, 1.0))
    success.add(QRScreen(t, url, 30.0))
    success.add(Solid(t, 1.0))

    fail = Manager(t)
    fail.add(ImageScreen(t, "attention.gif", 0.2, 2, 20.0, (0, 0, 0)))
    fail.add(ScrollText(t, "The UbaBot Cocktail machine is currently closed. Please come back later for more drinks!", 2))
    fail.add(Solid(t, 2.0))
    fail.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), None, 2.0))
    fail.add(Solid(t, 2.0))

    d = CheckHTTP(url)
    d.success(success)
    d.fail(fail)

    t.debug_loop(d.draw)
