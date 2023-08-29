#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import util
import time
import sys
import json
from config import Config

class TelegramBot:
    def __init__(self):
        if (Config.telegram_key == None) or len(Config.telegram_key) < 10:
            raise RuntimeError("No Telegram Bot API Key set!")

        self.get = None
        self.post = None
        self.previous_offset = None
        self.api = "https://api.telegram.org/bot" + Config.telegram_key + "/"

    def message(self, text):
        for chat in Config.telegram_whitelist:
            data = {
                "chat_id": chat,
                "text": text,
            }
            r = self.fetch(self.api + "sendMessage", data)
            print(r)

    def poll(self):
        if self.previous_offset != None:
            data = {
                "offset": self.previous_offset + 1,
            }
            r = self.fetch(self.api + "getUpdates", data)
        else:
            r = self.fetch(self.api + "getUpdates")

        print(r)

        for msg in r["result"]:
            if (self.previous_offset == None) or (self.previous_offset < msg["update_id"]):
                self.previous_offset = msg["update_id"]

    def fetch(self, url, data = None):
        # lazily initialize WiFi
        if self.get == None:
            self.get, self.post = util.getRequests()
            if self.get == None:
                return None

        try:
            if data == None:
                print("GET " + url)
                r = self.get(url)
            else:
                js = json.dumps(data)
                print("POST " + url + " " + js)
                r = self.post(url, headers = { "Content-Type": "application/json" }, data = js)

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

            return r.json()
        except Exception as e:
            print()
            print(url)
            if hasattr(sys, "print_exception"):
                sys.print_exception(e)
            else:
                print(e)
            print()
            return None

if __name__ == "__main__":
    b = TelegramBot()
    b.message("Hello World!")
    while True:
        b.poll()
