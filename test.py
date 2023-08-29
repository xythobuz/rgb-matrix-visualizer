#!/usr/bin/env python3

# Uses the pygame SDL wrapper:
# https://github.com/pygame/pygame
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import pygame

class TestGUI:
    def __init__(self, width = 32 * 2, height = 32 * 2, multiplier = 8):
        self.width = width
        self.height = height
        self.multiplier = multiplier

        # compatibility to PiMatrix
        self.panelW = 32
        self.panelH = 32

        pygame.display.init()
        self.screen = pygame.display.set_mode((self.width * self.multiplier, self.height * self.multiplier))
        self.clock = pygame.time.Clock()
        self.running = True

    def exit(self):
        pygame.quit()

    def loop_start(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYUP:
                if (event.key == pygame.K_q) or (event.key == pygame.K_ESCAPE):
                    return True

        self.screen.fill("black")
        return False

    def loop_end(self):
        pygame.display.flip()
        self.clock.tick(30)

    def set_pixel(self, x, y, color):
        if (x < 0) or (y < 0) or (x >= self.width) or (y >= self.height):
            return

        pygame.draw.rect(self.screen, color, pygame.Rect(x * self.multiplier, y * self.multiplier, self.multiplier, self.multiplier))

if __name__ == "__main__":
    t = TestGUI(32, 32)
    util.loop(t, lambda: t.set_pixel(15, 15, (255, 255, 255)))
