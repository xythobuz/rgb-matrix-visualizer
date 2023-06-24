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

class Tetris:
    def __init__(self, g, i, ts = 0.5, to = 60.0):
        self.gui = g
        self.input = i
        self.timestep = ts
        self.timeout = to

        self.endText = ScrollText(self.gui, "Game Over!", "uushi",
                                   2, 75, (251, 72, 196))
        self.scoreText = ScrollText(self.gui, "Score:", "uushi",
                                    2, 75, (63, 255, 33))

        self.bg = (0, 0, 0)
        self.colors = [
            (251, 72, 196), # camp23 pink
            (63, 255, 33), # camp23 green
            (255, 0, 0),
            #(0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (0, 255, 255),
            (255, 0, 255),
            #(255, 255, 255),
        ]

        # all [y][x] sub-lists must be the same length
        self.pieces = [
            # "I"
            [
                [1],
                [1],
                [1],
                [1],
            ],

            # "L"
            [
                [1, 0],
                [1, 0],
                [1, 1],
            ],

            # "J"
            [
                [0, 1],
                [0, 1],
                [1, 1],
            ],

            # "T"
            [
                [1, 1, 1],
                [0, 1, 0],
            ],

            # "O"
            [
                [1, 1],
                [1, 1],
            ],

            # "S"
            [
                [0, 1, 1],
                [1, 1, 0],
            ],

            # "Z"
            [
                [1, 1, 0],
                [0, 1, 1],
            ],
        ]

        random.seed()
        self.restart()

    def restart(self):
        self.start = time.time()
        self.last = time.time()
        self.button = None
        self.score = 0
        self.done = False
        self.data = [[self.bg for y in range(self.gui.height)] for x in range(self.gui.width)]
        self.piece = None

    def finished(self):
        if self.input == None:
            # backup timeout for "AI"
            if (time.time() - self.start) >= self.timeout:
                return True

        if self.done:
            # game over screen
            return self.scoreText.finished()

        return False

    # TODO collision detection is broken
    # TODO not working for pixels outside of vertical center line???
    # TODO something like that...
    def collision(self):
        # check for collision of piece with data
        pos = (self.piece[2], self.piece[3])
        for y in range(0, len(self.piece[0])):
            for x in range(0, len(self.piece[0][y])):
                # only check where piece actually is
                if self.piece[0][y][x] == 0:
                    continue

                # check for collision with bottom wall
                if (y + pos[1]) >= self.gui.height:
                    return True

                # check for collision with previous pieces
                if self.data[x + pos[0]][y + pos[1]] != self.bg:
                    return True
        return False

    # copy piece into data buffer
    def put(self, clear, pos = None, pie = None):
        position = pos
        if position == None:
            position = (self.piece[2], self.piece[3])

        piece = pie
        if piece == None:
            piece = self.piece[0]

        for y in range(0, len(piece)):
            for x in range(0, len(piece[y])):
                remove = False
                if piece[y][x] == 0:
                    remove = True

                if clear or remove:
                    self.data[x + position[0]][y + position[1]] = self.bg
                else:
                    self.data[x + position[0]][y + position[1]] = self.piece[1]

    def step(self):
        if self.piece == None:
            justPlaced = True

            # select a new piece type and color
            self.piece = [
                self.pieces[random.randrange(0, len(self.pieces))], # piece
                self.colors[random.randrange(0, len(self.colors))], # color
                0, # x
                0, # y
            ]

            # center the piece on top of the playing board
            self.piece[2] = int((self.gui.width - len(self.piece[0][0])) / 2)

            if self.collision():
                # new piece immediately collided. game over!
                return False

            # copy piece into data buffer
            self.put(False)

            # don't move in the placement-step
            return True

        oldPosition = (self.piece[2], self.piece[3])
        oldPiece = [x[:] for x in self.piece[0]]

        # button input
        if self.button == "u":
            # rotate piece
            # https://stackoverflow.com/a/48444999
            self.piece[0] = [list(x) for x in zip(*self.piece[0][::-1])]
        elif self.button == "l":
            if self.piece[2] > 0:
                self.piece[2] -= 1
        elif self.button == "r":
            if self.piece[2] < (self.gui.width - 1):
                self.piece[2] += 1
        else:
            # one pixel down
            self.piece[3] += 1

        # clear out piece from its old location
        self.put(True, oldPosition, oldPiece)

        collision = self.collision()
        if collision:
            # piece collided, put it back
            self.put(False, oldPosition, oldPiece)
            self.piece[0] = oldPiece
            self.piece[2] = oldPosition[0]
            self.piece[3] = oldPosition[1]

            if (self.button != "l") and (self.button != "r"):
                # but only stop playing it if it was moving down
                self.piece = None
        else:
            # copy piece at new location into buffer
            self.put(False)

        # clear previous input
        self.button = None

        return True

    def buttons(self):
        keys = self.input.get()
        if keys["left"]:
            self.button = "l"
        elif keys["right"]:
            self.button = "r"
        elif keys["up"]:
            self.button = "u"
        elif keys["down"]:
            self.button = "d"

    def draw(self):
        if self.done:
            if self.endText.finished():
                self.scoreText.draw()
            else:
                self.endText.draw()
                self.scoreText.restart()
            return

        if self.input != None:
            self.buttons()
        else:
            # TODO "AI"
            self.button = None

        if (self.button != None) or ((time.time() - self.last) >= self.timestep):
            self.last = time.time()
            cont = self.step()
            if cont == False:
                self.done = True
                self.scoreText.setText("Score: " + str(self.score), "uushi")
                self.endText.restart()

        for x in range(0, self.gui.width):
            for y in range(0, self.gui.height):
                self.gui.set_pixel(x, y, self.data[x][y])

if __name__ == "__main__":
    import util
    t = util.getTarget()

    from gamepad import InputWrapper
    i = InputWrapper()

    d = Tetris(t, i, 0.1)
    t.loop(d.draw)
