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
import util

class Breakout:
    def __init__(self, g, i, ts = 0.1, to = 60.0):
        self.gui = g
        self.input = i
        self.timestep = ts
        self.timeout = to

        self.paddle_width = 43#9

        self.winText = ScrollText(self.gui, "You Won!", "uushi",
                                  2, 50, (0, 255, 0))
        self.loseText = ScrollText(self.gui, "Game Over!", "uushi",
                                   2, 50, (255, 0, 0))
        self.scoreText = ScrollText(self.gui, "Score:", "uushi",
                                    2, 50, (255, 255, 255))

        self.bg_c = (0, 0, 0)
        self.fg_c = (0, 255, 0)
        self.ball_c = (255, 0, 0)
        self.paddle_c = (255, 255, 255)
        self.text_c = (0, 0, 255)

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

        self.data = [[self.bg_c for y in range(self.gui.height)] for x in range(self.gui.width)]

        for x in range(self.gui.width - 2):
            for y in range(5):
                self.data[x + 1][y] = self.fg_c
        self.maxScore = 5 * (self.gui.width - 2)

        # TODO easy mode
        self.nothing_to_lose = True

        DrawText = util.getTextDrawer()
        self.text = DrawText(self.gui, self.text_c)

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
        # move ball
        self.ball[0] += self.ball[2]
        self.ball[1] += self.ball[3]

        # check for collision with left wall
        if self.ball[0] <= 0:
            self.ball[2] = -self.ball[2]
            self.ball[0] = 0

        # check for collision with right wall
        if self.ball[0] >= self.gui.width - 1:
            self.ball[2] = -self.ball[2]
            self.ball[0] = self.gui.width - 1

        # check for collisions with pieces
        if self.data[int(self.ball[0])][int(self.ball[1])] != self.bg_c:
            self.data[int(self.ball[0])][int(self.ball[1])] = self.bg_c
            self.score += 1

            # just invert Y travel direction
            # TODO inaccurate collision behaviour in "corners"
            self.ball[3] = -self.ball[3]

        # check for collision with ceiling
        if self.ball[1] <= 0:
            self.ball[3] = -self.ball[3]

        # check for collision with paddle
        if (self.ball[1] == self.gui.height - 2) and (self.ball[0] >= (self.player - int(self.paddle_width / 2))) and (self.ball[0] <= (self.player + int(self.paddle_width / 2))):
            # TODO angle for bounce from paddle
            #self.ball[3] = -self.ball[3]
            d = self.ball[0] - (self.player - (self.paddle_width / 2))
            angle = (d / self.paddle_width - 0.5) / 2 * 3.14159
            print(math.degrees(angle))
            self.ball[2] = math.cos(angle) * math.sqrt(2)
            self.ball[3] = math.sin(angle) * math.sqrt(2)

        # check for collision with floor
        if self.ball[1] >= self.gui.height - 1:
            if self.nothing_to_lose:
                # TODO should this bounce with an angle?
                self.ball[3] = -self.ball[3]
            else:
                self.place()
                self.lives -= 1

    def finishedEndScreen(self):
        if self.score >= self.maxScore:
            return self.winText.finished()
        else:
            return self.loseText.finished()

    def drawEndScreen(self):
        if self.score >= self.maxScore:
            self.winText.draw()
        else:
            self.loseText.draw()

    def drawScoreScreen(self):
        self.scoreText.draw()

    def draw(self):
        # handle / generate player inputs
        if self.input != None:
            self.buttons()
        else:
            # TODO "AI"
            pass

        # only draw end-cards when game is over
        if (self.lives < 0) or (self.score >= self.maxScore):
            if self.finishedEndScreen():
                self.drawScoreScreen()
            else:
                self.drawEndScreen()
                self.scoreText.restart()
            return

        # move paddle according to player input
        if self.direction == "l":
            self.player = max(self.player - 1, 0)
        elif self.direction == "r":
            self.player = min(self.player + 1, self.gui.width - 1)
        self.direction = ""

        # run next iteration
        now = time.time()
        if (now - self.last) >= self.timestep:
            self.last = now
            self.step()

            # end game when all lives lost or when won
            if (self.lives < 0) or (self.score >= self.maxScore):
                self.scoreText.setText("Score: " + str(self.score), "uushi")
                self.winText.restart()
                self.loseText.restart()
                self.scoreText.restart()

        # draw targets on playing area
        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                self.gui.set_pixel(x, y, self.data[x][y])

        # draw score
        self.text.setText(str(self.score), "tom-thumb")
        self.text.draw(-1, self.gui.height / 2 - 2)

        # draw lives
        self.text.setText(str(self.lives), "tom-thumb")
        self.text.draw(-self.gui.width + 4, self.gui.height / 2 - 2)

        # draw paddle
        for x in range(0, self.paddle_width):
            self.gui.set_pixel(x + self.player - int(self.paddle_width / 2), self.gui.height - 1, self.paddle_c)

        # draw ball
        self.gui.set_pixel(int(self.ball[0]), int(self.ball[1]), self.ball_c)

if __name__ == "__main__":
    # Need to import InputWrapper before initializing RGB Matrix on Pi
    i = util.getInput()
    t = util.getTarget(i)

    d = Breakout(t, i)

    # example color modifications
    d.fg_c = (0, 150, 0)
    d.ball_c = (150, 0, 0)
    d.paddle_c = (150, 150, 150)
    d.text_c = (0, 0, 150)
    d.restart() # re-gen with new colors

    util.loop(t, d.draw)
