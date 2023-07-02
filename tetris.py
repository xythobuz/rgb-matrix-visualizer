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

class Tetris:
    def __init__(self, g, i, ts = 0.5, to = 60.0, w = 10, h = 22):
        self.gui = g
        self.input = i
        self.timestep = ts
        self.timeout = to
        self.width = min(w, self.gui.width)
        self.height = min(h, self.gui.height)

        self.x_off = int((self.gui.panelW - self.width - 2) / 2)
        self.y_off = int((self.gui.panelH - self.height - 2) / 2)

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
        self.data = [[self.bg for y in range(self.height)] for x in range(self.width)]
        self.piece = None
        self.old_keys = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

    def finished(self):
        if self.input == None:
            # backup timeout for "AI"
            if (time.time() - self.start) >= self.timeout:
                return True

        if self.done:
            # game over screen
            return self.scoreText.finished()

        return False

    def collision(self):
        # check for collision of piece with data
        pos = (self.piece[2], self.piece[3])
        for y in range(0, len(self.piece[0])):
            for x in range(0, len(self.piece[0][y])):
                # only check where piece actually is
                if self.piece[0][y][x] == 0:
                    continue

                # check for collision with bottom wall
                if (y + pos[1]) >= self.height:
                    return True

                # check for collision with right wall
                if (x + pos[0]) >= self.width:
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
                # only set or clear where piece actually is
                if piece[y][x] == 0:
                    continue

                if clear:
                    self.data[x + position[0]][y + position[1]] = self.bg
                else:
                    self.data[x + position[0]][y + position[1]] = self.piece[1]

    def checkWin(self):
        had_data = False
        for y in range(0, self.height):
            line_full = True
            for x in range(0, self.width):
                if self.data[x][y] == self.bg:
                    line_full = False
                else:
                    had_data = True

            if had_data and line_full:
                self.score += 1

                # move stuff above into this line
                for y2 in reversed(range(1, y + 1)):
                    for x in range(0, self.width):
                        self.data[x][y2] = self.data[x][y2 - 1]

                # clear out top line
                for x in range(0, self.width):
                    self.data[x][0] = self.bg

        # check for complete win
        board_clear = (self.piece == None)
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.data[x][y] != self.bg:
                    board_clear = False
                if board_clear == False:
                    break
            if board_clear == False:
                break
        return board_clear

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
            self.piece[2] = int((self.width - len(self.piece[0][0])) / 2)

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
            if self.piece[2] < (self.width - 1):
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

            if (self.button != "l") and (self.button != "r") and (self.button != "u"):
                # but only stop playing it if it was moving down
                self.piece = None

                # check for cleared line
                if self.checkWin():
                    return False
        else:
            # copy piece at new location into buffer
            self.put(False)

        # clear previous input
        self.button = None

        return True

    def buttons(self):
        keys = self.input.get()

        if keys["left"] and (not self.old_keys["left"]):
            self.button = "l"
        elif keys["right"] and (not self.old_keys["right"]):
            self.button = "r"
        elif keys["up"] and (not self.old_keys["up"]):
            self.button = "u"
        elif keys["down"]:
            self.button = "d"
        elif (keys["select"] and keys["start"] and (not self.old_keys["start"])) or (keys["start"] and keys["select"] and (not self.old_keys["select"])):
            self.restart()

        self.old_keys = keys.copy()

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

        now = time.time()
        if (self.button != None) or ((now - self.last) >= self.timestep) or (now < self.last):
            # don't let user stop falling pieces by moving/rotating endlessly
            if (self.button != "l") and (self.button != "r") and (self.button != "u"):
                self.last = now

            cont = self.step()
            if cont == False:
                self.done = True
                self.scoreText.setText("Score: " + str(self.score), "uushi")
                self.endText.restart()

        # TODO placement of play area
        for x in range(-1, self.width + 1):
            for y in range(-1, self.height + 1):
                c = (255, 255, 255)
                if (x >= 0) and (y >= 0) and (x < self.width) and (y < self.height):
                    c = self.data[x][y]

                self.gui.set_pixel(x + 1 + self.x_off, y + 1 + self.y_off, c)

if __name__ == "__main__":
    # Need to import InputWrapper before initializing RGB Matrix on Pi
    from gamepad import InputWrapper
    i = InputWrapper()

    import util
    t = util.getTarget()

    d = Tetris(t, i)
    t.loop(d.draw)
