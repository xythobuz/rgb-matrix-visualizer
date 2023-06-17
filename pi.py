#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

class PiMatrix:
    def __init__(self):
        # TODO configurable
        self.width = 32
        self.height = 32

        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 32
        options.chain_length = 1
        options.parallel = 1
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = 'RGB'
        #options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'
        options.gpio_slowdown = 2
        options.pixel_mapper_config = "Rotate:270"

        self.matrix = RGBMatrix(options = options)

        self.loop_start() # initialize with blank image for ScrollText constructor

    def loop_start(self):
        self.image = Image.new('RGB', (self.width, self.height))
        return False # no input, never quit on our own

    def loop_end(self):
        self.matrix.SetImage(self.image.convert('RGB'))

    def debug_loop(self, func = None):
        while True:
            if self.loop_start():
                break
            if func != None:
                func()
            self.loop_end()

    def set_pixel(self, x, y, color):
        if (x < 0) or (y < 0) or (x >= self.width) or (y >= self.height):
            return

        self.image.putpixel((int(x), int(y)), color)

if __name__ == "__main__":
    t = PiMatrix()
    t.debug_loop(lambda: t.set_pixel(15, 15, (255, 255, 255)))
