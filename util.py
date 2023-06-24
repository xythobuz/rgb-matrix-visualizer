#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

targetPlatform = None

def isPi():
    global targetPlatform

    if targetPlatform == None:
        getTarget()

    return targetPlatform == "pi"

def isPico():
    global targetPlatform

    if targetPlatform == None:
        getTarget()

    return targetPlatform == "pico"

def getTarget():
    global targetPlatform

    target = None
    try:
        # First we try the Raspberry Pi interface
        from pi import PiMatrix
        pi = PiMatrix()

        # TODO hard-coded adjustments
        from mapper import MapperColorAdjust, MapperStripToRect
        col = MapperColorAdjust(pi)
        target = MapperStripToRect(col)

        if targetPlatform == None:
            # only print once
            print("Raspberry Pi Adafruit RGB LED Matrix detected")
        targetPlatform = "pi"
    except:
        try:
            # Next we try the Pico Interstate75 interface
            from pico import PicoMatrix
            target = PicoMatrix()

            if targetPlatform == None:
                # only print once
                print("Raspberry Pi Pico Interstate75 RGB LED Matrix detected")
            targetPlatform = "pico"
        except:
            # If this fails fall back to the SDL/pygame GUI
            from test import TestGUI
            target = TestGUI()

            if targetPlatform == None:
                # only print once
                print("Falling back to GUI debug interface")
            targetPlatform = "tk"

    return target
