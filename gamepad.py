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
        self.keys = self.empty()

        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            c = device.capabilities(absinfo=False)
            keep = False

            # check for axis events
            if ecodes.EV_ABS in c:
                # check for gamepad
                if ecodes.ABS_X in c[ecodes.EV_ABS]:
                    print("Gamepad detected: ", device.name)
                    keep = True

            # check for key events
            if ecodes.EV_KEY in c:
                # check for arrow keys
                if ecodes.KEY_LEFT in c[ecodes.EV_KEY]:
                    print("Keyboard detected:", device.name)
                    keep = True

            if not keep:
                continue

            d = InputDevice(device.path)
            self.devices.append(d)
            self.selector.register(d, EVENT_READ)

    def empty(self):
        return {
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
            "l2": False,
            "r2": False,
        }

    def get(self, verbose = False):
        for key, mask in self.selector.select(0):
            device = key.fileobj
            for event in device.read():
                if event.type == ecodes.EV_KEY:
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
                    elif (event.code == ecodes.KEY_SPACE) or (event.code == ecodes.BTN_A) or (event.code == ecodes.BTN_THUMB):
                        self.keys["a"] = v
                    elif (event.code == ecodes.KEY_LEFTCTRL) or (event.code == ecodes.BTN_B) or (event.code == ecodes.BTN_THUMB2):
                        self.keys["b"] = v
                    elif (event.code == ecodes.KEY_LEFTALT) or (event.code == ecodes.BTN_X) or (event.code == ecodes.BTN_JOYSTICK) or (event.code == ecodes.BTN_TRIGGER):
                        self.keys["x"] = v
                    elif (event.code == ecodes.KEY_ENTER) or (event.code == ecodes.BTN_Y) or (event.code == ecodes.BTN_TOP):
                        self.keys["y"] = v
                    elif (event.code == ecodes.BTN_PINKIE) or (event.code == ecodes.KEY_D):
                        self.keys["r"] = v
                    elif (event.code == ecodes.BTN_TOP2) or (event.code == ecodes.KEY_A):
                        self.keys["l"] = v
                    elif event.code == ecodes.BTN_BASE:
                        self.keys["r2"] = v
                    elif event.code == ecodes.BTN_BASE2:
                        self.keys["l2"] = v
                    elif (event.code == ecodes.BTN_BASE4) or (event.code == ecodes.KEY_BACKSPACE):
                        self.keys["start"] = v
                    elif event.code == ecodes.BTN_BASE3:
                        self.keys["select"] = v
                elif event.type == ecodes.EV_ABS:
                    # TODO 8bit hardcoded
                    if event.code == ecodes.ABS_X:
                        if event.value > 200:
                            self.keys["right"] = True
                            self.keys["left"] = False
                        elif event.value < 100:
                            self.keys["right"] = False
                            self.keys["left"] = True
                        else:
                            self.keys["right"] = False
                            self.keys["left"] = False
                    elif event.code == ecodes.ABS_Y:
                        if event.value > 200:
                            self.keys["down"] = True
                            self.keys["up"] = False
                        elif event.value < 100:
                            self.keys["down"] = False
                            self.keys["up"] = True
                        else:
                            self.keys["down"] = False
                            self.keys["up"] = False
                elif event.type == ecodes.EV_SYN:
                    continue # don't print sync events

                if verbose:
                    print(categorize(event))
                    print(event)
                    print()

        return self.keys

if __name__ == "__main__":
    from pprint import pprint
    import sys

    if (len(sys.argv) > 1) and (sys.argv[1] == "list"):
        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            print(device.path, device.name, device.phys)
            pprint(device.capabilities(verbose=True))
            print()
    elif (len(sys.argv) > 1) and (sys.argv[1] == "events"):
        i = InputWrapper()
        last_keys = None
        while True:
            i.get(True)
    else:
        i = InputWrapper()
        last_keys = None
        while True:
            keys = i.get()
            if (last_keys == None) or (keys != last_keys):
                pprint(keys)
                print()
                last_keys = keys.copy()
