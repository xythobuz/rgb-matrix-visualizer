#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

from draw import ScrollText
import time
import random

class Snake:
    def __init__(self, g, i, sc = (0, 255, 0), d = (0, 0, 255), bg = (0, 0, 0), ts = 0.3, su = 0.75, to = 60.0):
        self.gui = g
        self.input = i
        self.colors = [ bg, sc, d ]
        self.timestep = ts
        self.timeout = to
        self.speedup = su

        self.winText = ScrollText(self.gui, "You Won!", "uushi",
                                  2, 75, (0, 255, 0))
        self.loseText = ScrollText(self.gui, "Game Over!", "uushi",
                                   2, 75, (255, 0, 0))
        self.scoreText = ScrollText(self.gui, "Score:", "uushi",
                                    2, 75, sc)

        random.seed()
        self.restart()

    def restart(self):
        self.start = time.time()
        self.last = time.time()
        self.direction = "r"
        self.directionTmp = "r"
        self.score = 0
        self.data = [[0 for y in range(self.gui.height)] for x in range(self.gui.width)]

        self.player = [ (int(self.gui.width / 2), int(self.gui.height / 2)) ]
        self.data[self.player[0][0]][self.player[0][1]] = 1

        self.placeDot()

    def finished(self):
        if self.input == None:
            # backup timeout for "AI"
            if (time.time() - self.start) >= self.timeout:
                return True

        if self.direction == "":
            # game over screen
            return self.scoreText.finished()

        return False

    def placeDot(self):
        d = (random.randrange(0, self.gui.width), random.randrange(0, self.gui.height))
        while self.data[d[0]][d[1]] != 0:
            d = (random.randrange(0, self.gui.width), random.randrange(0, self.gui.height))
        self.data[d[0]][d[1]] = 2

    def buttons(self):
        keys = self.input.get()
        if keys["left"]:
            self.directionTmp = "l"
        elif keys["right"]:
            self.directionTmp = "r"
        elif keys["up"]:
            self.directionTmp = "u"
        elif keys["down"]:
            self.directionTmp = "d"

    def step(self):
        player = self.player[len(self.player) - 1]
        if self.direction == "r":
            player = (player[0] + 1, player[1])
        elif self.direction == "l":
            player = (player[0] - 1, player[1])
        elif self.direction == "u":
            player = (player[0], player[1] - 1)
        elif self.direction == "d":
            player = (player[0], player[1] + 1)

        if (player[0] < 0) or (player[1] < 0) or (player[0] >= self.gui.width) or (player[1] >= self.gui.height):
            return False

        if self.data[player[0]][player[1]] == 0:
            # remove last tail piece if not on dot
            self.data[self.player[0][0]][self.player[0][1]] = 0
            self.player.pop(0)
        elif self.data[player[0]][player[1]] == 1:
            # snake crashed into itself
            return False
        else:
            # collected a dot
            self.score += 1
            if self.score >= self.gui.width * self.gui.height:
                return False

            self.timestep = self.timestep * self.speedup
            self.placeDot()

        self.player.append(player)
        self.data[player[0]][player[1]] = 1
        return True

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
        if self.direction == "":
            if self.finishedEndScreen():
                self.drawScoreScreen()
            else:
                self.drawEndScreen()
                self.scoreText.restart()
            return

        if self.input != None:
            self.buttons()
        else:
            # TODO "AI"
            pass

        if (time.time() - self.last) >= self.timestep:
            self.last = time.time()

            # only allow valid inputs
            tmp = self.direction + self.directionTmp
            if (tmp != "lr") and (tmp != "rl") and (tmp != "ud") and (tmp != "du"):
                self.direction = self.directionTmp

            cont = self.step()
            if cont == False:
                self.direction = ""
                self.scoreText.setText("Score: " + str(self.score), "uushi")
                self.winText.restart()
                self.loseText.restart()
                self.scoreText.restart()

        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                self.gui.set_pixel(x, y, self.colors[self.data[x][y]])

if __name__ == "__main__":
    import util
    t = util.getTarget()

    from gamepad import InputWrapper
    i = InputWrapper()

    d = Snake(t, i)
    t.loop(d.draw)
