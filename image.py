#!/usr/bin/env python3

# Uses the pillow Python Imaging Library:
# https://github.com/python-pillow/Pillow
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

from PIL import Image
import time
import os

# GIF images contain Palletes for each frame.
# These can be different between frames.
# So the library is converting them to RGB.
# This means we can not replace the background easily
# for all but the first frame in animations.
# This setting changes that to keep the same palette, as long as possible.
# This works with some GIFs, but not all of them.
from PIL import GifImagePlugin
GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY

class ImageScreen:
    def __init__(self, g, p, t = 0.2, i = 1, to = 5.0, bg = None):
        self.gui = g
        self.time = t
        self.iterations = i
        self.timeout = to
        self.background = bg

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(scriptDir, "images", p)
        self.image = Image.open(self.path)

        # for some reason non-animated images don't even have this attribute
        if not hasattr(self.image, "is_animated"):
            self.image.is_animated = False
            self.image.n_frames = 1

        # automatically crop and scale large images
        if not self.image.is_animated and ((self.image.width > self.gui.width) or (self.image.height > self.gui.height)):
            # crop to visible area
            self.image = self.image.crop(self.image.getbbox())

            # keep the aspect ratio and fit within visible area
            ratio = self.image.width / self.image.height
            max_width = int(ratio * self.gui.height)
            max_height = int(self.gui.width / ratio)
            if (max_height >= self.gui.height) or (((self.gui.width - max_width) < (self.gui.height - max_height)) and ((self.gui.width - max_width) >= 0)):
                width = max_width
                height = self.gui.height
            else:
                width = self.gui.width
                height = max_height

            # resize
            self.image = self.image.resize((width, height),
                                           Image.Resampling.NEAREST)

            # new image object is also missing these
            self.image.is_animated = False
            self.image.n_frames = 1

        print(p, self.image.width, self.image.height, self.image.is_animated, self.image.n_frames)

        self.xOff = int((self.gui.width - self.image.width) / 2)
        self.yOff = int((self.gui.height - self.image.height) / 2)

        self.restart()

    def restart(self):
        self.start = time.time()
        self.frame = time.time()
        self.count = 0
        self.done = 0
        self.image.seek(0)

    def finished(self):
        if self.done >= self.iterations:
            return True

        # only apply timeout for static images
        if self.image.is_animated:
            return False
        else:
            return (time.time() - self.start) >= self.timeout

    def draw(self):
        if self.image.is_animated:
            now = time.time()
            if (now - self.frame) >= self.time:
                self.frame = now
                self.count = (self.count + 1) % self.image.n_frames
                if self.count == 0:
                    self.done += 1

                self.image.seek(self.count)

        p = self.image.getpalette()
        for x in range(0, self.image.width):
            for y in range(0, self.image.height):
                v = self.image.getpixel((x, y))
                if isinstance(v, int):
                    c = None
                    if self.background != None:
                        if "transparency" in self.image.info:
                            if v == self.image.info["transparency"]:
                                c = self.background
                        else:
                            if v == self.image.info["background"]:
                                c = self.background
                    if c == None:
                        c = (p[v * 3 + 0], p[v * 3 + 1], p[v * 3 + 2])
                    self.gui.set_pixel(x + self.xOff, y + self.yOff, c)
                else:
                    self.gui.set_pixel(x + self.xOff, y + self.yOff, v)

if __name__ == "__main__":
    import sys

    import util
    t = util.getTarget()

    from manager import Manager
    m = Manager(t)

    scriptDir = os.path.dirname(os.path.realpath(__file__))
    imageDir = os.path.join(scriptDir, "images")
    for f in os.listdir(os.fsencode(imageDir)):
        filename = os.fsdecode(f)

        if len(sys.argv) > 1:
            if not sys.argv[1] in filename:
                continue

        d = ImageScreen(t, filename)
        m.add(d)

        if filename != "Favicon.png":
            continue

        try:
            # dump generated image to console, for embedding in Pico script
            print()
            print("Dumping image to img_tmp.py")
            with open("img_tmp.py", "w") as f:
                f.write("# Image \"" + filename + "\"" + os.linesep)
                f.write("# size:" + str(d.image.width) + "x" + str(d.image.height) + os.linesep)
                f.write("img_data = [" + os.linesep)
                for y in range(0, d.image.height):
                    f.write(" [" + os.linesep)
                    for x in range(0, d.image.width):
                        s = str(d.image.getpixel((x, y)))
                        f.write("  " + s + "," + os.linesep)
                    f.write(" ]," + os.linesep)
                f.write("]" + os.linesep)
            print()
        except Exception as e:
            print()
            if hasattr(sys, "print_exception"):
                sys.print_exception(e)
            else:
                print(e)
                print()

    m.restart()
    util.loop(t, m.draw)
