#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import sys

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
    except Exception as e:
        print()
        sys.print_exception(e)
        print()

        try:
            # Next we try the Pico Interstate75 interface
            from pico import PicoMatrix
            pico = PicoMatrix()

            # TODO hard-coded adjustments
            from mapper import MapperReduceBrightness
            target = MapperReduceBrightness(pico)

            if targetPlatform == None:
                # only print once
                print("Raspberry Pi Pico Interstate75 RGB LED Matrix detected")
            targetPlatform = "pico"
        except Exception as e:
            print()
            sys.print_exception(e)
            print()

            # If this fails fall back to the SDL/pygame GUI
            from test import TestGUI
            target = TestGUI()

            if targetPlatform == None:
                # only print once
                print("Falling back to GUI debug interface")
            targetPlatform = "tk"

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
        sys.print_exception(e)
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
    password = None
    for name, a, b, c, d, e in visible:
        for t_ssid, t_password in Config.networks:
            if name.decode("utf-8") == t_ssid:
                ssid = t_ssid
                password = t_password
                break
    if (ssid == None) or (password == None):
        print("No known network found")
        wifiConnected = False
        return False

    # Start connection
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
        return requests.get
    except Exception as e:
        print()
        sys.print_exception(e)
        print()

        # if it fails try the Pi Pico MicroPython implementation
        import urequests as requests

        # in this case we also need to connect to WiFi first
        if not wifiConnected:
            if not connectToWiFi():
                return None

        return requests.get

    return None

def getTextDrawer():
    try:
        # Try BDF parser library
        from bdf import DrawText
        return DrawText
    except Exception as e:
        print()
        sys.print_exception(e)
        print()

        # fall back to the Pico Interstate75 implementation
        from pico import PicoText
        return PicoText

    return None
