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
import util

class Snake:
    def __init__(self, g, i, sc = (0, 255, 0), d = (0, 0, 255), bg = (0, 0, 0), ts = 0.3, su = 0.75, to = 60.0):
        self.gui = g
        self.input = i
        self.colors = [ bg, sc, d ]
        self.timestepOriginal = ts
        self.timeout = to
        self.speedup = su

        self.winText = ScrollText(self.gui, "You Won!", "uushi",
                                  1, 50, (0, 255, 0))
        self.loseText = ScrollText(self.gui, "Game Over!", "uushi",
                                   1, 50, (255, 0, 0))
        self.scoreText = ScrollText(self.gui, "Score:", "uushi",
                                    3, 50, sc)

        self.text_c = (0, 0, 255)
        self.fact = int(self.gui.width / self.gui.panelW)

        random.seed()
        self.restart()

    def restart(self):
        self.timestep = self.timestepOriginal
        self.start = time.time()
        self.last = time.time()
        self.direction = "r"
        self.directionTmp = "r"
        self.score = 0
        self.data = [[0 for y in range(int(self.gui.height / self.fact))] for x in range(int(self.gui.width / self.fact))]

        self.player = [ (int(self.gui.width / 2 / self.fact), int(self.gui.height / 2 / self.fact)) ]
        self.data[self.player[0][0]][self.player[0][1]] = 1

        DrawText = util.getTextDrawer()
        self.text = DrawText(self.gui, self.text_c)

        self.old_keys = self.input.empty() # TODO support missing input

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
        d = (random.randrange(0, int(self.gui.width / self.fact)), random.randrange(0, int(self.gui.height / self.fact)))
        while (self.data[d[0]][d[1]] != 0) or (d[0] < 15) or (d[1] < 8):
            d = (random.randrange(0, int(self.gui.width / self.fact)), random.randrange(0, int(self.gui.height / self.fact)))
        self.data[d[0]][d[1]] = 2

    def buttons(self):
        keys = self.input.get()

        if keys["left"] and (not self.old_keys["left"]) and (not self.old_keys["select"]):
            self.directionTmp = "l"
        elif keys["right"] and (not self.old_keys["right"]) and (not self.old_keys["select"]):
            self.directionTmp = "r"
        elif keys["up"] and (not self.old_keys["up"]) and (not self.old_keys["select"]):
            self.directionTmp = "u"
        elif keys["down"] and (not self.old_keys["down"]) and (not self.old_keys["select"]):
            self.directionTmp = "d"
        elif (keys["select"] and keys["start"] and (not self.old_keys["start"])) or (keys["start"] and keys["select"] and (not self.old_keys["select"])):
            self.restart()

        self.old_keys = keys.copy()

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

        if (player[0] < 0) or (player[1] < 0) or (player[0] >= int(self.gui.width / self.fact)) or (player[1] >= int(self.gui.height / self.fact)):
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
            if self.score >= int(self.gui.width / self.fact) * int(self.gui.height / self.fact):
                return False

            self.timestep = self.timestep * self.speedup
            self.placeDot()

        self.player.append(player)
        self.data[player[0]][player[1]] = 1
        return True

    def finishedEndScreen(self):
        if self.score >= int(self.gui.width / self.fact) * int(self.gui.height / self.fact):
            return self.winText.finished()
        else:
            return self.loseText.finished()

    def drawEndScreen(self):
        if self.score >= int(self.gui.width / self.fact) * int(self.gui.height / self.fact):
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

        if self.direction == "":
            if self.finishedEndScreen():
                self.drawScoreScreen()
            else:
                self.drawEndScreen()
                self.scoreText.restart()
            return

        now = time.time()
        if (now - self.last) >= self.timestep:
            self.last = now

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

        for x in range(0, int(self.gui.width / self.fact)):
            for y in range(0, int(self.gui.height / self.fact)):
                for x1 in range(0, self.fact):
                    for y1 in range(0, self.fact):
                        self.gui.set_pixel(x * self.fact + x1, y * self.fact + y1, self.colors[self.data[x][y]])

        # draw score
        self.text.setText(str(self.score), "tom-thumb")
        self.text.draw(-1, self.gui.height / 2 - 2)

if __name__ == "__main__":
    # Need to import InputWrapper before initializing RGB Matrix on Pi
    i = util.getInput()
    t = util.getTarget(i)

    d = Snake(t, i)
    util.loop(t, d.draw)
