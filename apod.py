#!/usr/bin/env python3

# https://apod.nasa.gov/apod/
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import sys
import os

import util
from image import ImageScreen

class APOD:
    def __init__(self, g, i, to = 10.0, r = 6 * 60 * 60, ito = 30.0):
        self.gui = g
        self.input = i
        self.timeout = to
        self.refresh = r
        self.input_timeout = ito

        self.get = None
        self.path = "https://apod.nasa.gov/apod"
        self.img_url = None
        self.img_path = None
        self.image = None
        self.last = None
        self.restart()

    def reloadImage(self):
        if (self.last == None) or ((time.time() - self.last) >= self.refresh):
            try:
                print("APOD refresh")
                self.img_url, self.img_desc = self.get_image_metadata()
                self.img_path = self.download_image(self.img_url)
                self.image = ImageScreen(self.gui, self.img_path, 0.2, 1, 5.0, None, None, False)
                self.last = time.time()
            except Exception as e:
                print()
                if hasattr(sys, "print_exception"):
                    sys.print_exception(e)
                else:
                    print(e)
                print()

    def restart(self):
        self.reloadImage()
        self.old_keys = self.input.empty() # TODO support missing input
        self.lastInput = None
        self.drawingText = False
        self.show = time.time()

    def finished(self):
        if self.lastInput == None:
            # skip when no image could be loaded
            if self.image == None:
                return True

            # 10s show image timeout when no buttons have been pressed
            if (time.time() - self.show) >= self.timeout:
                return True
        else:
            # 30s button input timeout after last button press
            if (time.time() - self.lastInput) >= self.input_timeout:
                return True

        return False

    def fetch(self, url):
        # lazily initialize WiFi
        if self.get == None:
            self.get, post = util.getRequests()
            if self.get == None:
                return None

        try:
            #print("GET " + url)
            r = self.get(url)

            # explitic close on Response object not needed,
            # handled internally by r.content / r.text / r.json()
            # to avoid this automatic behaviour, first access r.content
            # to trigger caching it in response object, then close
            # socket.
            tmp = r.content
            if hasattr(r, "raw"):
                if r.raw != None:
                    r.raw.close()
                    r.raw = None

            return r
        except Exception as e:
            print()
            print(url)
            if hasattr(sys, "print_exception"):
                sys.print_exception(e)
            else:
                print(e)
            print()
            return None

    def get_image_metadata(self, path = ""):
        if len(path) == 0:
            print("Checking for new APOD")
        else:
            print("Checking out APOD '{}'".format(path))

        imgPath = None
        imgDesc = None

        r = self.fetch(self.path + "/" + path).text
        for line in r.splitlines():
            start = line.find('IMG SRC="')
            if start >= 0:
                start += 9
                end = line.find('"', start)
                img = line[start : end]
                imgPath = self.path + "/" + img
                break # TODO also check for description

        return imgPath, imgDesc

    def download_image(self, path):
        print("Loading " + path)
        r = self.fetch(path).content

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        imageDir = os.path.join(scriptDir, "images")
        imagePath = os.path.join(imageDir, "apod_" + os.path.basename(path))

        if os.path.isfile(imagePath):
            print("Image already loaded. Skip.")
            return imagePath

        print("Storing at " + imagePath)
        with open(imagePath, 'wb') as f:
            f.write(r)

        return imagePath

    def buttons(self):
        keys = self.input.get()

        if keys["up"] and (not self.old_keys["up"]) and (not self.old_keys["select"]):
            pass # TODO next picture
        elif keys["down"] and (not self.old_keys["down"]) and (not self.old_keys["select"]):
            pass # TODO previous picture
        elif keys["a"] and (not self.old_keys["a"]):
            self.drawingText = True
        elif (keys["select"] and keys["start"] and (not self.old_keys["start"])) or (keys["start"] and keys["select"] and (not self.old_keys["select"])):
            self.restart()

        self.old_keys = keys.copy()

    def draw(self):
        if self.input != None:
            self.buttons()

        if self.drawingText:
            pass # TODO
        else:
            if self.image != None:
                self.image.draw()

if __name__ == "__main__":
    i = util.getInput()
    t = util.getTarget(i)

    s = APOD(t, i)

    def helper():
        s.draw()
        if s.finished():
            s.restart()

    util.loop(t, helper)
