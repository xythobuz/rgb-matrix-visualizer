#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import pygame

class TestGUI:
    def __init__(self, width = 32, height = 32, multiplier = 16):
        self.width = width
        self.height = height
        self.multiplier = multiplier

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

        self.screen.fill("black")
        return False

    def loop_end(self):
        pygame.display.flip()
        self.clock.tick(30)

    def debug_loop(self, func = None):
        while True:
            if self.loop_start():
                break
            if func != None:
                func()
            self.loop_end()
        self.exit()

    def set_pixel(self, x, y, color):
        if (x < 0) or (y < 0) or (x >= self.width) or (y >= self.height):
            return

        pygame.draw.rect(self.screen, color, pygame.Rect(x * self.multiplier, y * self.multiplier, self.multiplier, self.multiplier))

if __name__ == "__main__":
    t = TestGUI(32, 32)
    t.debug_loop(lambda: t.set_pixel(15, 15, (255, 255, 255)))
