#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

from scroll import ScrollText
import time
import random
import math

class Breakout:
    def __init__(self, g, i, ts = 0.1, to = 60.0):
        self.gui = g
        self.input = i
        self.timestep = ts
        self.timeout = to

        self.paddle_width = 9

        self.winText = ScrollText(self.gui, "You Won!", "uushi",
                                  2, 50, (0, 255, 0))
        self.loseText = ScrollText(self.gui, "Game Over!", "uushi",
                                   2, 50, (255, 0, 0))
        self.scoreText = ScrollText(self.gui, "Score:", "uushi",
                                    2, 50, (255, 255, 255))

        random.seed()
        self.restart()

    def place(self):
        self.player = int(self.gui.width / 2)
        self.ball = [
            self.player, # x
            self.gui.height - 2, # y
            1, # v x
            -1, # v y
        ]

    def restart(self):
        self.start = time.time()
        self.last = time.time()
        self.lives = 3
        self.score = 0
        self.direction = ""

        self.data = [[(0, 0, 0) for y in range(self.gui.height)] for x in range(self.gui.width)]

        for x in range(self.gui.width - 2):
            for y in range(5):
                self.data[x + 1][y] = (0, 255, 0)

        self.place()

        self.old_keys = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "a": False,
            "b": False,
            "x": False,
            "y": False,
            "l": False,
            "r": False,
            "start": False,
            "select": False,
        }

    def finished(self):
        if self.input == None:
            # backup timeout for "AI"
            if (time.time() - self.start) >= self.timeout:
                return True

        if self.lives < 0:
            # game over screen
            return self.scoreText.finished()

        return False

    def buttons(self):
        keys = self.input.get()

        if keys["left"] and (not self.old_keys["left"]) and (not self.old_keys["select"]):
            self.direction = "l"
        elif keys["right"] and (not self.old_keys["right"]) and (not self.old_keys["select"]):
            self.direction = "r"
        elif (keys["select"] and keys["start"] and (not self.old_keys["start"])) or (keys["start"] and keys["select"] and (not self.old_keys["select"])):
            self.restart()

        self.old_keys = keys.copy()

    def step(self):
        # TODO check for collisions with pieces

        # move ball
        self.ball[0] += self.ball[2]
        self.ball[1] += self.ball[3]

        # check for collision with left wall
        if self.ball[0] <= 0:
            self.ball[2] = -self.ball[2]

        # check for collision with right wall
        if self.ball[0] >= self.gui.width - 1:
            self.ball[2] = -self.ball[2]

        # check for collision with ceiling
        if self.ball[1] <= 0:
            self.ball[3] = -self.ball[3]

        # check for collision with paddle
        if (self.ball[1] == self.gui.height - 2) and (self.ball[0] >= (self.player - int(self.paddle_width / 2))) and (self.ball[0] <= (self.player + int(self.paddle_width / 2))):
            # TODO angle
            self.ball[3] = -self.ball[3]

        # check for collision with floor
        if self.ball[1] >= self.gui.height - 1:
            self.place()
            self.lives -= 1

    def finishedEndScreen(self):
        if self.score >= self.gui.width * self.gui.height:
            return self.winText.finished()
        else:
            return self.loseText.finished()

    def drawEndScreen(self):
        if self.score >= self.gui.width * self.gui.height:
            self.winText.draw()
        else:
            self.loseText.draw()

    def drawScoreScreen(self):
        self.scoreText.draw()

    def draw(self):
        if self.input != None:
            self.buttons()
        else:
            # TODO "AI"
            pass

        if self.lives < 0:
            if self.finishedEndScreen():
                self.drawScoreScreen()
            else:
                self.drawEndScreen()
                self.scoreText.restart()
            return

        if self.direction == "l":
            self.player = max(self.player - 1, 0)
        elif self.direction == "r":
            self.player = min(self.player + 1, self.gui.width - 1)
        self.direction = ""

        now = time.time()
        if (now - self.last) >= self.timestep:
            self.last = now
            self.step()

            if self.lives < 0:
                self.scoreText.setText("Score: " + str(self.score), "uushi")
                self.winText.restart()
                self.loseText.restart()
                self.scoreText.restart()

        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                self.gui.set_pixel(x, y, self.data[x][y])

        for x in range(0, self.paddle_width):
            self.gui.set_pixel(x + self.player - int(self.paddle_width / 2), self.gui.height - 1, (255, 255, 255))

        self.gui.set_pixel(self.ball[0], self.ball[1], (255, 0, 0))

if __name__ == "__main__":
    import util
    # Need to import InputWrapper before initializing RGB Matrix on Pi
    i = util.getInput()
    t = util.getTarget(i)

    d = Breakout(t, i)
    util.loop(t, d.draw)
