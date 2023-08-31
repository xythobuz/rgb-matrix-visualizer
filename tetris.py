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

class Tetris:
    def __init__(self, g, i, ts = 0.5, to = 60.0, w = 10, h = 22):
        self.gui = g
        self.input = i
        self.timestep = ts
        self.timeout = to
        self.width = min(w, self.gui.width)
        self.height = min(h, self.gui.height)

        self.endText = ScrollText(self.gui, "Game Over!", "uushi",
                                   1, 50, (251, 72, 196))
        self.scoreText = ScrollText(self.gui, "Score:", "uushi",
                                    3, 50, (63, 255, 33))

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

        DrawText = util.getTextDrawer()
        self.text = []
        self.text.append(DrawText(self.gui, self.colors[1])) # Green, "Score"
        self.text.append(DrawText(self.gui, self.colors[0])) # Pink, Score Number
        self.text.append(DrawText(self.gui, self.colors[4])) # Yellow, "Paused"
        self.text.append(DrawText(self.gui, self.colors[5])) # Blue, "next"
        self.text.append(DrawText(self.gui, self.colors[0])) # Pink, "Tetris"
        self.text.append(DrawText(self.gui, self.colors[5])) # Blue, "up"
        self.text[0].setText("Score:", "tom-thumb")
        self.text[1].setText("0", "tom-thumb")
        self.text[2].setText("Paused", "tom-thumb")
        self.text[3].setText("next", "tom-thumb")
        if self.gui.height > self.gui.panelH:
            self.text[4].setText("Tetris", "ib8x8u")
            self.text[5].setText("up:", "tom-thumb")
        else:
            self.text[4].setText("Tetris", "tom-thumb")
            self.text[5].setText("up", "tom-thumb")

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

        self.max_width = 0
        self.max_height = 0
        for piece in self.pieces:
            if len(piece) > self.max_height:
                self.max_height = len(piece)
            if len(piece[0]) > self.max_width:
                self.max_width = len(piece[0])
        self.max_width += 2
        self.max_height += 2


        self.fact = 1
        self.x_off = 1
        self.y_off = self.gui.height - self.height - 3
        self.next_x_off = self.gui.panelW - self.max_width + 24
        self.next_y_off = self.gui.panelH - self.max_height - 3

        if self.gui.height > self.gui.panelH:
            self.fact = 2
            self.y_off = self.gui.height - self.height * self.fact - 3
            self.next_y_off = self.gui.panelH - self.max_height * self.fact + 29

        random.seed()
        self.restart()

    def restart(self):
        self.start = time.time()
        self.last = time.time()
        self.button = None
        self.score = 0
        self.text[1].setText(str(self.score), "tom-thumb")
        self.done = False
        self.data = [[self.bg for y in range(self.height)] for x in range(self.width)]
        self.piece = None
        self.next_piece = None
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
        self.pause = False

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
                self.text[1].setText(str(self.score), "tom-thumb")

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
        if self.next_piece == None:
            # select a new piece type and color
            self.next_piece = [
                self.pieces[random.randrange(0, len(self.pieces))], # piece
                self.colors[random.randrange(0, len(self.colors))], # color
                0, # x
                0, # y
            ]

            # center the piece on top of the playing board
            self.next_piece[2] = int((self.width - len(self.next_piece[0][0])) / 2)

            # offsets for drawing the next piece
            self.piece_x_off = int((self.max_width - len(self.next_piece[0][0])) / 2)
            self.piece_y_off = int((self.max_height - len(self.next_piece[0])) / 2)

        if self.piece == None:
            justPlaced = True
            self.piece = self.next_piece
            self.next_piece = None

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

        if keys["left"] and (not self.old_keys["left"]) and (not self.old_keys["select"]):
            self.button = "l"
        elif keys["right"] and (not self.old_keys["right"]) and (not self.old_keys["select"]):
            self.button = "r"
        elif keys["up"] and (not self.old_keys["up"]) and (not self.old_keys["select"]):
            self.button = "u"
        elif keys["down"] and (not self.old_keys["select"]):
            self.button = "d"
        elif (keys["select"] and keys["start"] and (not self.old_keys["start"])) or (keys["start"] and keys["select"] and (not self.old_keys["select"])):
            self.restart()
        elif keys["start"] and (not self.old_keys["start"]) and (not self.old_keys["select"]):
            self.pause = not self.pause
        elif self.done and keys["start"] and (not self.old_keys["start"]):
            self.restart()
        elif self.done and keys["a"] and (not self.old_keys["a"]):
            self.restart()
        elif self.done and keys["b"] and (not self.old_keys["b"]):
            self.restart()
        elif self.done and keys["x"] and (not self.old_keys["x"]):
            self.restart()
        elif self.done and keys["y"] and (not self.old_keys["y"]):
            self.restart()

        self.old_keys = keys.copy()

    def draw_stats(self, off):
        x_off, y_off = off

        if self.fact > 1:
            self.text[0].draw(-x_off - 2, y_off - 6)
            self.text[1].draw(-x_off - 2, y_off)
        else:
            self.text[0].draw(-x_off - 2, y_off - 11)
            self.text[1].draw(-x_off - 2, y_off - 5)

        if self.pause:
            if self.fact > 1:
                self.text[2].draw(-x_off - 2 + 16, -y_off + 11 - 5)
            else:
                self.text[2].draw(-x_off - 2, -y_off + 11)

    def draw(self):
        if self.input != None:
            self.buttons()
        else:
            # TODO "AI"
            self.button = None

        if self.done:
            if self.endText.finished():
                self.scoreText.draw()
            else:
                self.endText.draw()
                self.scoreText.restart()
            return

        now = time.time()
        if (not self.pause) and ((self.button != None) or ((now - self.last) >= self.timestep) or (now < self.last)):
            # don't let user stop falling pieces by moving/rotating endlessly
            if (self.button != "l") and (self.button != "r") and (self.button != "u"):
                self.last = now

            cont = self.step()
            if cont == False:
                self.done = True
                self.scoreText.setText("Score: " + str(self.score), "uushi")
                self.endText.restart()

        # static text
        if self.fact > 1:
            self.text[4].draw(-2, -22)
            self.text[3].draw(-34, 13)
            self.text[5].draw(-34, 20)
        else:
            self.text[4].draw(-2, -11)
            self.text[3].draw(-14, 5)
            self.text[5].draw(-14, 12)

        # draw play area and border
        for x in range(-1, self.width + 1):
            for y in range(-1, self.height + 1):
                c = self.colors[1] # border color
                if (x >= 0) and (y >= 0) and (x < self.width) and (y < self.height):
                    c = self.data[x][y]

                for x1 in range(0, self.fact):
                    for y1 in range(0, self.fact):
                        self.gui.set_pixel(
                            self.fact * x + 1 + self.x_off + x1,
                            self.fact * y + 1 + self.y_off + y1,
                            c
                        )

        # draw next piece and border
        for x in range(-1, self.max_width + 1):
            for y in range(-1, self.max_height + 1):
                c = self.colors[0] # border color
                if (x >= 0) and (y >= 0) and (x < self.max_width) and (y < self.max_height):
                    if self.next_piece == None:
                        c = (0, 0, 0)
                    else:
                        if (y >= self.piece_y_off) and (y < (len(self.next_piece[0]) + self.piece_y_off)) and (x >= self.piece_x_off) and (x < (len(self.next_piece[0][0]) + self.piece_x_off)):
                            if self.next_piece[0][y - self.piece_y_off][x - self.piece_x_off] != 0:
                                c = self.next_piece[1]
                            else:
                                c = (0, 0, 0)
                        else:
                            c = (0, 0, 0)

                for x1 in range(0, self.fact):
                    for y1 in range(0, self.fact):
                        self.gui.set_pixel(
                            self.fact * x + 1 + self.next_x_off + x1,
                            self.fact * y + 1 + self.next_y_off + y1,
                            c
                        )

        # find position for stats
        stats_off = None
        if self.gui.width > self.gui.panelW:
            stats_off = (self.gui.panelW, 0)
        elif self.gui.height > self.gui.panelH:
            stats_off = (0, self.gui.panelH)

        # second screen with stats
        if stats_off != None:
            self.draw_stats(stats_off)

if __name__ == "__main__":
    # Need to import InputWrapper before initializing RGB Matrix on Pi
    i = util.getInput()
    t = util.getTarget(i)

    # show splash screen while initializing
    from splash import SplashScreen
    splash = SplashScreen(t)
    t.loop_start()
    splash.draw()
    t.loop_end()

    d = Tetris(t, i)
    util.loop(t, d.draw)
