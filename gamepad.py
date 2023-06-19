#!/usr/bin/env python3

# Uses the Python evdev wrapper:
# https://github.com/gvalkov/python-evdev
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

from evdev import InputDevice, list_devices, ecodes, categorize
from selectors import DefaultSelector, EVENT_READ

class InputWrapper:
    def __init__(self):
        self.devices = []
        self.selector = DefaultSelector()
        self.keys = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "a": False,
            "b": False,
            "x": False,
            "y": False,
        }

        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            c = device.capabilities()
            keep = False

            # check for key events
            if ecodes.EV_KEY in c:
                # check for gamepad
                if ecodes.BTN_A in c[ecodes.EV_KEY]:
                    print("Gamepad detected: ", device.name)
                    keep = True

                # check for arrow keys
                elif ecodes.KEY_LEFT in c[ecodes.EV_KEY]:
                    print("Keyboard detected:", device.name)
                    keep = True

            if not keep:
                continue

            d = InputDevice(device.path)
            self.devices.append(d)
            self.selector.register(d, EVENT_READ)

    def get(self, verbose = False):
        for key, mask in self.selector.select(0):
            device = key.fileobj
            for event in device.read():
                if event.type != ecodes.EV_KEY:
                    continue

                v = False
                if event.value != 0:
                    v = True

                if (event.code == ecodes.KEY_LEFT) or (event.code == ecodes.BTN_WEST):
                    self.keys["left"] = v
                elif (event.code == ecodes.KEY_RIGHT) or (event.code == ecodes.BTN_EAST):
                    self.keys["right"] = v
                elif (event.code == ecodes.KEY_UP) or (event.code == ecodes.BTN_NORTH):
                    self.keys["up"] = v
                elif (event.code == ecodes.KEY_DOWN) or (event.code == ecodes.BTN_SOUTH):
                    self.keys["down"] = v
                elif (event.code == ecodes.KEY_SPACE) or (event.code == ecodes.BTN_A):
                    self.keys["a"] = v
                elif (event.code == ecodes.KEY_LEFTCTRL) or (event.code == ecodes.BTN_B):
                    self.keys["b"] = v
                elif (event.code == ecodes.KEY_LEFTALT) or (event.code == ecodes.BTN_X):
                    self.keys["x"] = v
                elif (event.code == ecodes.KEY_ENTER) or (event.code == ecodes.BTN_Y):
                    self.keys["y"] = v
                else:
                    return self.keys

                if verbose:
                    print(categorize(event), event)

        return self.keys

if __name__ == "__main__":
    from pprint import pprint
    import sys

    if len(sys.argv) > 1:
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            print(device.path, device.name, device.phys)
            pprint(device.capabilities(verbose=True))
            print()
    else:
        i = InputWrapper()
        while True:
            i.get(True)
