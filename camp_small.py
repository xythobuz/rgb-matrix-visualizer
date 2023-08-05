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

url_uba = "http://ubabot.frubar.net"
url_printer = "http://i3-am8.fritz.box"

scroll_speed = 50

# Need to import InputWrapper before initializing RGB Matrix on Pi
i = util.getInput()
t = util.getTarget(i)

# Loading fonts and graphics takes a while.
# So show a splash screen while the user waits.
splash = SplashScreen(t)
t.loop_start()
splash.draw()
t.loop_end()

# UbaBot is online
success_uba = Manager(t)
success_uba.add(ImageScreen(t, "drinka.gif", 0.2, 2, 20.0, (0, 0, 0)))
success_uba.add(Solid(t, 1.0))
success_uba.add(ScrollText(t, "Visit the UbaBot Cocktail machine at FruBar village for drinks!", "lemon", 2, scroll_speed, camp_green))
success_uba.add(Solid(t, 1.0))
success_uba.add(QRScreen(t, url_uba, 30.0, "Drinks:", "tom-thumb", camp_pink, (0, 0, 0)))
success_uba.add(Solid(t, 1.0))

# UbaBot is offline
fail_uba = Manager(t)
fail_uba.add(ImageScreen(t, "attention.gif", 0.2, 2, 20.0, (0, 0, 0)))
fail_uba.add(Solid(t, 1.0))
fail_uba.add(ScrollText(t, "The UbaBot Cocktail machine is currently closed. Please come back later for more drinks!", "lemon", 2, scroll_speed, camp_pink))
fail_uba.add(Solid(t, 1.0))
fail_uba.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), None, 2.0))
fail_uba.add(Solid(t, 1.0))

# UbaBot status checker
d = CheckHTTP(url_uba)
d.success(success_uba)
d.fail(fail_uba)

# 3D printer is online
success_printer = Manager(t)
success_printer.add(ScrollText(t, "Need to print something? FruBar village has a 3D printer. Come by!", "iv18x16u", 1, scroll_speed, camp_pink))
success_printer.add(Solid(t, 1.0))

# 3D printer is offline
fail_printer = Manager(t)
fail_printer.add(Solid(t, 1.0))
fail_printer.add(Solid(t, 1.0))

# Printer status checker
d2 = CheckHTTP(url_printer)
d2.success(success_printer)
d2.fail(fail_printer)

# Main "Menu"
m = Manager(t, i)
m.add(ScrollText(t, "#CCCAMP23", "lemon", 1, scroll_speed, camp_green))
m.add(Solid(t, 1.0))
m.add(ImageScreen(t, "Favicon.png", 0, 1, 10.0))
m.add(Solid(t, 1.0))
m.add(ScrollText(t, "Grab a cold draft beer at FruBar village!", "iv18x16u", 1, scroll_speed, camp_green))
m.add(d) # HTTP Check, either "success" or "fail"
m.add(Solid(t, 1.0))
m.add(d2) # HTTP Check, either "success" or "fail"
m.add(Solid(t, 1.0))
m.add(Snake(t, i, camp_pink, camp_green))
m.add(Solid(t, 1.0))
m.add(ScrollText(t, "Your advertisement could appear here. Open a Pull Request on git.xythobuz.de/thomas/rgb-matrix-visualizer or send an e-mail to thomas@xythobuz.de", "iv18x16u", 2, scroll_speed, camp_green))
m.add(Solid(t, 1.0))

m.restart()
util.loop(t, m.draw)
