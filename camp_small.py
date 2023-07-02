#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

camp_pink = (251, 72, 196)
camp_green = (63, 255, 33)

from splash import SplashScreen
from scroll import ScrollText
from solid import Solid
from life import GameOfLife
from net import CheckHTTP
from image import ImageScreen
from qr import QRScreen
from snake import Snake
from gamepad import InputWrapper
from manager import Manager
import util

url = "http://ubabot.frubar.net"

# Need to import InputWrapper before initializing RGB Matrix on Pi
i = InputWrapper()

t = util.getTarget()

# Loading fonts and graphics takes a while.
# So show a splash screen while the user waits.
splash = SplashScreen(t)
t.loop_start()
splash.draw()
t.loop_end()

# UbaBot is online
success = Manager(t)
success.add(ImageScreen(t, "drinka.gif", 0.2, 2, 20.0))
success.add(Solid(t, 1.0))
success.add(QRScreen(t, url, 30.0, "Drinks:", "tom-thumb", (255, 255, 255), (0, 0, 0)))
success.add(Solid(t, 1.0))

# UbaBot is offline
fail = Manager(t)
fail.add(ImageScreen(t, "attention.gif", 0.2, 2, 20.0, (0, 0, 0)))
fail.add(ScrollText(t, "The UbaBot Cocktail machine is currently closed. Please come back later for more drinks!", "lemon", 2, 75, camp_pink))
fail.add(Solid(t, 1.0))
fail.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), None, 2.0))
fail.add(Solid(t, 1.0))

# UbaBot status checker
d = CheckHTTP(url)
d.success(success)
d.fail(fail)

# Main "Menu"
m = Manager(t)
m.add(ScrollText(t, "#CCCAMP23", "lemon", 1, 75, camp_green))
m.add(Solid(t, 1.0))
m.add(ImageScreen(t, "Favicon.png", 0, 1, 10.0))
m.add(Solid(t, 1.0))
m.add(d) # HTTP Check, either "success" or "fail"
m.add(Solid(t, 1.0))
m.add(Snake(t, i, camp_pink, camp_green))
m.add(Solid(t, 1.0))
m.add(ScrollText(t, "Your advertisement could appear here. Open a Pull Request on git.xythobuz.de/thomas/rgb-matrix-visualizer or send an e-mail to thomas@xythobuz.de", "iv18x16u", 2, 70, camp_green))
m.add(Solid(t, 1.0))

m.restart()
t.loop(m.draw)
