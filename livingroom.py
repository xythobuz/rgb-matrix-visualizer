#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

camp_pink = (251, 72, 196)
camp_green = (63, 255, 33)
pause = 2.0

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
from config import Config
import util

# Need to import InputWrapper before initializing RGB Matrix on Pi
i = util.getInput()
t = util.getTarget(i)

# Loading fonts and graphics takes a while.
# So show a splash screen while the user waits.
splash = SplashScreen(t)
t.loop_start()
splash.draw()
t.loop_end()

m = Manager(t, i, 2, True)

if not util.isPi():
    # TODO weather does not run on Pi yet unfortunately :(
    from weather import WeatherScreen
    m.add(WeatherScreen(t, i, Config.weather_latlon))
    m.add(Solid(t, pause))

m.add(GameOfLife(t, 20, (0, 255, 0), (0, 0, 0), None, 2.0))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "32_earth.gif", 0.2, 2))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "aphex-twin-logo.png", 0.2, 1, 10.0, None, None, False))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "cann.png", 0.2, 1, 10.0))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "cann2.png", 0.2, 1, 10.0))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "64_cloud.gif", 0.2, 1, 5.0, (0, 0, 0)))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "64_sephiroth.gif", 0.2, 4, 5.0, (0, 0, 0)))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "64_nlogospin.gif", 0.2, 2))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "64_snake.gif", 0.1, 2))
m.add(Solid(t, pause))

m.add(ImageScreen(t, "64_snake2.gif", 0.2, 1))
m.add(Solid(t, pause))

m.add(Breakout(t, i))
m.add(Solid(t, pause))

m.add(Tetris(t, i,))
m.add(Solid(t, pause))

m.add(Snake(t, i, camp_pink, camp_green))
m.add(Solid(t, pause))

m.restart()
util.loop(t, m.draw)
