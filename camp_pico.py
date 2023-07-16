#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

camp_pink = (251, 72, 196)
camp_green = (63, 255, 33)

# pre-converted images for Pico (required libraries not available)
from qr_tmp import qr_data
from img_tmp import img_data

from solid import Solid
from life import GameOfLife
from net import CheckHTTP
from qr import QRScreen
from scroll import ScrollText
from splash import SplashScreen
from manager import Manager
from pico import PicoBatt

#url = "http://ubabot.frubar.net"
url = "http://www.xythobuz.de"

import util
i = util.getInput()
t = util.getTarget(i)

# Loading fonts and graphics takes a while.
# So show a splash screen while the user waits.
splash = SplashScreen(t)
t.loop_start()
splash.draw()
t.loop_end()

# UbaBot is online
success = Manager(t)
success.add(ScrollText(t, "Visit UbaBot Cocktail machine at FruBar village for drinks!", "bitmap8", 1, 10, camp_green))
success.add(Solid(t, 1.0))
success.add(QRScreen(t, qr_data, 30.0, "Drinks", "bitmap6", camp_pink, (0, 0, 0)))
success.add(Solid(t, 1.0))

# UbaBot is offline
fail = Manager(t)
fail.add(ScrollText(t, "#CCCAMP23", "bitmap8", 1, 10, camp_green))
fail.add(Solid(t, 1.0))
fail.add(ScrollText(t, "The UbaBot Cocktail machine is closed. Please come back later!", "bitmap8", 1, 10, camp_green))
fail.add(Solid(t, 1.0))
fail.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), None, 2.0))
fail.add(Solid(t, 1.0))
fail.add(ScrollText(t, "Your advertisement could appear here. Open a Pull Request on git.xythobuz.de/thomas/rgb-matrix-visualizer or send an e-mail to thomas@xythobuz.de", "bitmap8", 1, 10, camp_green))
fail.add(Solid(t, 1.0))

# UbaBot status checker
d = CheckHTTP(url)
d.success(success)
d.fail(fail)

# Main "Menu"
m = Manager(t, i)
m.add(QRScreen(t, img_data, 15.0))
m.add(Solid(t, 1.0))
m.add(d) # HTTP Check, either "success" or "fail"
m.add(Solid(t, 1.0))
m.add(PicoBatt(t, 5.0, 5.0))
m.add(Solid(t, 1.0))

m.restart()
util.loop(t, m.draw)
