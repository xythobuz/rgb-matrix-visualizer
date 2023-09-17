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

class TunnelRun:
    def __init__(self, g, i, t = 0.10, to = 60.0):
        self.gui = g
        self.input = i
        self.timestep = t
        self.timeout = to

        self.winText = ScrollText(self.gui, "You Won!", "uushi",
                                  1, 50, (0, 255, 0))
        self.loseText = ScrollText(self.gui, "Game Over!", "uushi",
                                   1, 50, (255, 0, 0))
        self.scoreText = ScrollText(self.gui, "Score:", "uushi",
                                    3, 50, (255, 0, 255))

        DrawText = util.getTextDrawer()
        self.text = DrawText(self.gui, (0, 0, 255))

        self.restart()

    def restart(self):
        self.start = time.time()
        self.last = time.time()
        self.direction = "r"
        self.directionTmp = "r"
        self.done = False

        self.player = [ int(self.gui.width / 2), int(self.gui.height / 2) ]

        self.old_keys = self.input.empty() # TODO support missing input

    def finished(self):
        if self.input == None:
            # backup timeout for "AI"
            if (time.time() - self.start) >= self.timeout:
                return True

        if self.done:
            # game over screen
            return self.scoreText.finished()

        return False

    def buttons(self):
        keys = self.input.get()

        if keys["left"] and (not self.old_keys["select"]):
            self.player[0] = self.player[0] - 1
        if keys["right"] and (not self.old_keys["select"]):
            self.player[0] = self.player[0] + 1
        if keys["up"] and (not self.old_keys["select"]):
            self.player[1] = self.player[1] - 1
        if keys["down"] and (not self.old_keys["select"]):
            self.player[1] = self.player[1] + 1
        if (keys["select"] and keys["start"] and (not self.old_keys["start"])) or (keys["start"] and keys["select"] and (not self.old_keys["select"])):
            self.restart()

        self.old_keys = keys.copy()

        if (self.player[0] < 0) or (self.player[1] < 0) or (self.player[0] >= self.gui.width) or (self.player[1] >= self.gui.height):
            return False

        return True

    def step(self):
        return True

    def finishedEndScreen(self):
        now = time.time()
        score = int(now - self.start)
        # TODO win condition
        if score >= self.gui.width * self.gui.height:
            return self.winText.finished()
        else:
            return self.loseText.finished()

    def drawEndScreen(self):
        now = time.time()
        score = int(now - self.start)
        # TODO win condition
        if score >= self.gui.width * self.gui.height:
            self.winText.draw()
        else:
            self.loseText.draw()

    def die(self):
        self.done = True
        now = time.time()
        score = int(now - self.start)
        self.scoreText.setText("Score: " + str(score), "uushi")
        self.winText.restart()
        self.loseText.restart()
        self.scoreText.restart()

    def draw(self):
        if self.done:
            if self.finishedEndScreen():
                self.scoreText.draw()
            else:
                self.drawEndScreen()
                self.scoreText.restart()
            return

        if self.input != None:
            cont = self.buttons()
            if cont == False:
                self.die()
        else:
            # TODO "AI"
            pass

        now = time.time()
        if (now - self.last) >= self.timestep:
            self.last = now
            cont = self.step()
            if cont == False:
                self.die()

        #for x in range(0, self.gui.width):
        #    for y in range(0, self.gui.height):
        #        self.gui.set_pixel(x, y, (0, 0, 0))

        # draw score
        now = time.time()
        score = int(now - self.start)
        self.text.setText(str(score), "tom-thumb")
        self.text.draw(-1, self.gui.height / 2 - 2)

        # draw player
        self.gui.set_pixel(self.player[0], self.player[1], (255, 0, 0))

if __name__ == "__main__":
    # Need to import InputWrapper before initializing RGB Matrix on Pi
    i = util.getInput()
    t = util.getTarget(i)

    d = TunnelRun(t, i)
    util.loop(t, d.draw)
