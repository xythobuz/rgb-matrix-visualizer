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
from tetris import Tetris
from breakout import Breakout
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

# Main "Menu"
m = Manager(t, i)
m.add(Breakout(t, i))
m.add(Solid(t, 1.0))
m.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), None, 2.0))
m.add(Solid(t, 1.0))
m.add(Tetris(t, i,))
m.add(Solid(t, 1.0))
m.add(Snake(t, i, camp_pink, camp_green))
m.add(Solid(t, 1.0))

m.restart()
util.loop(t, m.draw)
