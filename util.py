#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

targetIsPi = None

def isPi():
    global targetIsPi

    if targetIsPi == None:
        getTarget()
    return targetIsPi

def getTarget():
    global targetIsPi

    target = None
    try:
        from pi import PiMatrix
        target = PiMatrix()

        if targetIsPi == None:
            # only print once
            print("Raspberry Pi Adafruit RGB LED Matrix detected")

        targetIsPi = True
    except ModuleNotFoundError:
        from test import TestGUI
        target = TestGUI()

        if targetIsPi == None:
            # only print once
            print("Falling back to GUI debug interface")

        targetIsPi = False
    return target
