#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

class Config:
    networks = [
        ("SSID_1", "PASS_1"),
        ("SSID_2", "USER_2", "PASS_2"),
    ]

    telegram_key = "API_KEY_HERE"
    telegram_whitelist = [
        "ALLOWED_CHAT_ID_HERE",
    ]

    weather_latlon = (YOUR_LAT_HERE, YOUR_LON_HERE)
