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

# https://github.com/raspberrypi/pico-examples/blob/master/pico_w/wifi/python_test_tcp/micropython_test_tcp_client.py
def connectToWiFi():
    import network
    import time
    from config import Config

    # Check if wifi details have been set
    if len(Config.networks) == 0:
        print('Please set wifi ssid and password in config.py')
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
        return False

    # Start connection
    wlan.connect(ssid, password)

    # Wait for connect success or failure
    max_wait = 20
    error_count = 20
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
        return False
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

    return True

def getRequests():
    try:
        # try to get normal python lib
        import requests
        return requests.get
    except:
        # if it fails try the Pi Pico MicroPython implementation
        import urequests as requests

        # in this case we also need to connect to WiFi first
        if not connectToWiFi():
            return None

        return requests.get

    return None

def getTextDrawer():
    try:
        # Try BDF parser library
        from bdf import DrawText
        return DrawText
    except:
        # fall back to the Pico Interstate75 implementation
        from pico import PicoText
        return PicoText

    return None
