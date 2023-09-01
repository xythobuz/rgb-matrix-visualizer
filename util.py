#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import sys

cachedTarget = None
targetPlatform = None
wifiConnected = False

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

def getTarget(i = None):
    global targetPlatform, cachedTarget

    if cachedTarget != None:
        return cachedTarget

    target = None
    try:
        # First we try the Raspberry Pi interface
        from pi import PiMatrix
        pi = PiMatrix()

        # TODO hard-coded adjustments
        from mapper import MapperReduceBrightness, MapperColorAdjust, MapperStripToRect
        bright = MapperReduceBrightness(pi, i)
        #col = MapperColorAdjust(bright)
        #target = col
        #target = MapperStripToRect(col)
        target = MapperStripToRect(bright)

        if targetPlatform == None:
            # only print once
            print("Raspberry Pi Adafruit RGB LED Matrix detected")
        targetPlatform = "pi"
    except Exception as e:
        target = None

        print()
        if hasattr(sys, "print_exception"):
            sys.print_exception(e)
        else:
            print(e)
        print()

        try:
            # Next we try the Pico Interstate75 interface
            from pico import PicoMatrix
            pico = PicoMatrix(i)

            # TODO hard-coded adjustments
            from mapper import MapperReduceBrightness
            target = MapperReduceBrightness(pico, i)

            if targetPlatform == None:
                # only print once
                print("Raspberry Pi Pico Interstate75 RGB LED Matrix detected")
            targetPlatform = "pico"
        except Exception as e:
            target = None

            print()
            if hasattr(sys, "print_exception"):
                sys.print_exception(e)
            else:
                print(e)
            print()

            # If this fails fall back to the SDL/pygame GUI
            from test import TestGUI
            ui = TestGUI()

            # TODO hard-coded adjustments
            #from mapper import MapperReduceBrightness
            #target = MapperReduceBrightness(ui, i)
            target = ui

            if targetPlatform == None:
                # only print once
                print("Falling back to GUI debug interface")
            targetPlatform = "tk"

    cachedTarget = target
    return target

# https://github.com/raspberrypi/pico-examples/blob/master/pico_w/wifi/python_test_tcp/micropython_test_tcp_client.py
def connectToWiFi():
    global wifiConnected

    if wifiConnected:
        return True

    # only use WiFi on Pico
    try:
        from pico import PicoMatrix
    except Exception as e:
        print()
        if hasattr(sys, "print_exception"):
            sys.print_exception(e)
        else:
            print(e)
        print()

        wifiConnected = True
        return True

    import network
    import time
    from config import Config

    # Check if wifi details have been set
    if len(Config.networks) == 0:
        print('Please set wifi ssid and password in config.py')
        wifiConnected = False
        return False

    # Start WiFi hardware
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Look for known networks
    visible = wlan.scan()
    ssid = None
    user = None
    password = None

    print(visible)
    if len(visible) == 0:
        print("No networks visible at all")
        wifiConnected = False
        return False

    for name, a, b, c, d, e in visible:
        for net in Config.networks:
            if len(net) == 2:
                t_ssid, t_password = net
            elif len(net) == 3:
                t_ssid, t_user, t_password = net

            if name.decode("utf-8") == t_ssid:
                ssid = t_ssid
                if len(net) == 3:
                    user = t_user
                password = t_password
                break
    if (ssid == None) or (password == None):
        print("No known network found")
        wifiConnected = False
        return False

    # Start connection
    if user != None:
        wlan.seteap(user, password)
        wlan.connect(ssid)
    else:
        wlan.connect(ssid, password)

    # Wait for connect success or failure
    max_wait = 40
    error_count = max_wait
    while max_wait > 0:
        if wlan.status() >= 3:
            break
        elif wlan.status() < 0:
            wlan.connect(ssid, password)
            error_count -= 1
            if error_count <= 0:
                break
        else:
            max_wait -= 1
        print('waiting for connection...')
        time.sleep(0.5)

    # Handle connection error
    if wlan.status() != 3:
        print('wifi connection failed %d' % wlan.status())
        wifiConnected = False
        return False
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

    wifiConnected = True
    return True

def getRequests():
    global wifiConnected

    try:
        # try to get normal python lib
        import requests
        return requests.get, requests.post
    except Exception as e:
        print()
        if hasattr(sys, "print_exception"):
            sys.print_exception(e)
        else:
            print(e)
        print()

        # if it fails try the Pi Pico MicroPython implementation
        import urequests as requests

        # in this case we also need to connect to WiFi first
        if not wifiConnected:
            if not connectToWiFi():
                return None, None

        return requests.get, requests.post

    return None, None

def getTextDrawer():
    try:
        # Try BDF parser library
        from bdf import DrawText
        return DrawText
    except Exception as e:
        print()
        if hasattr(sys, "print_exception"):
            sys.print_exception(e)
        else:
            print(e)
        print()

        # fall back to the Pico Interstate75 implementation
        from pico import PicoText
        return PicoText

    return None

def getInput():
    try:
        # try evdev library
        from gamepad import InputWrapper
        return InputWrapper()
    except Exception as e:
        print()
        if hasattr(sys, "print_exception"):
            sys.print_exception(e)
        else:
            print(e)
        print()

        # fall back to the Pico Interstate75 implementation
        from pico import PicoInput
        return PicoInput()

    return None

def loop(gui, func = None):
    while True:
        if gui.loop_start():
            break
        if func != None:
            func()
        gui.loop_end()
    gui.exit()
