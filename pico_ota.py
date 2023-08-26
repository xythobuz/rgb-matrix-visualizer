#!/usr/bin/env python3

# Uses the Gitea API to fetch the latest revision of the project from a repo.
#
# Inspired by:
# https://github.com/olivergregorius/micropython_ota
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import util
import sys
import os
import gc

# to check if we're actually running on MicroPython
on_pico = False
try:
    import machine
    on_pico = True
except Exception as e:
    print()
    if hasattr(sys, "print_exception"):
        sys.print_exception(e)
    else:
        print(e)
    print()

class PicoOTA:
    def __init__(self, host, repo, branch = None):
        self.host = host
        self.repo = repo
        self.branch = branch

        self.get = None
        self.update_path = "."
        self.exe_path = ""
        self.version_file = "ota_version"
        self.blacklist = []

        self.gui = None
        self.text = None

    def ui(self, g, t):
        self.gui = g
        self.text = t


        if (self.gui == None) or (self.text == None):
            return

        for i in range(0, 5):
            self.gui.loop_start()

            self.text.fg = (255, 255, 0)
            self.text.setText("WiFi", "bitmap6")
            self.text.draw(0, 6 * 0, False)

            self.text.fg = (255, 0, 255)
            self.text.setText("???", "bitmap6")
            self.text.draw(0, 6 * 1, False)

            self.text.fg = (255, 0, 0)
            self.text.setText(str(i + 1) + " / 5", "bitmap6")
            self.text.draw(0, 6 * 2, False)

            self.text.fg = (0, 255, 0)
            self.text.setText("", "bitmap6")
            self.text.draw(0, 6 * 3, False)

            self.text.setText("Conn...", "bitmap6")
            self.text.draw(0, 6 * 4, False)

            self.gui.loop_end()

            util.connectToWiFi()

            self.gui.loop_start()

            self.text.fg = (255, 255, 0)
            self.text.setText("WiFi", "bitmap6")
            self.text.draw(0, 6 * 0, False)

            self.text.fg = (255, 0, 255)
            self.text.setText("$NAME", "bitmap6")
            self.text.draw(0, 6 * 1, False)

            self.text.fg = (255, 0, 0)
            self.text.setText(str(i + 1) + " / 5", "bitmap6")
            self.text.draw(0, 6 * 2, False)

            self.text.fg = (0, 255, 0)
            self.text.setText("Status:", "bitmap6")
            self.text.draw(0, 6 * 3, False)

            self.text.setText("$val", "bitmap6")
            self.text.draw(0, 6 * 4, False)

            self.gui.loop_end()

    def path(self, p):
        self.update_path = p

    def exe(self, e):
        self.exe_path = e

    def ignore(self, path):
        if not path in self.blacklist:
            self.blacklist.append(path)

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

    def get_stored_commit(self):
        current = "unknown"
        try:
            f = open(self.update_path + "/" + self.version_file, "r")
            current = f.readline().strip()
            f.close()
        except Exception as e:
            print()
            if hasattr(sys, "print_exception"):
                sys.print_exception(e)
            else:
                print(e)
            print()
        return current

    def get_previous_commit(self, commit):
        r = self.fetch(self.host + "/" + self.repo + "/commit/" + commit).text
        for line in r.splitlines():
            if not (self.repo + "/commit/") in line:
                continue

            line = line[line.find("/commit/") : ][8 : ][ : 40]
            if line != commit:
                return line
        return "unknown"

    def check(self, verbose = False):
        if self.branch == None:
            # get default branch
            r = self.fetch(self.host + "/api/v1/repos/" + self.repo).json()
            self.branch = r["default_branch"]

            if verbose:
                print("Selected default branch " + self.branch)

        # check for latest commit in branch
        r = self.fetch(self.host + "/api/v1/repos/" + self.repo + "/branches/" + self.branch).json()
        commit = r["commit"]["id"]

        if verbose:
            print("Latest commit is " + commit)

        current = self.get_stored_commit()

        if verbose:
            if current != commit:
                print("Current commit " + current + " is different!")
            else:
                print("No update required")

        return (current != commit, commit)

    def update_to_commit(self, commit, verbose = False):
        # list all files for a commit
        r = self.fetch(self.host + "/api/v1/repos/" + self.repo + "/git/trees/" + commit).json()

        # TODO does not support sub-folders

        if verbose:
            if len(r["tree"]) > 0:
                print(str(len(r["tree"])) + " files in repo:")
                for f in r["tree"]:
                    if f["path"] in self.blacklist:
                        print("  - (IGNORED) " + f["path"])
                    else:
                        print("  - " + f["path"])
            else:
                print("No files in repo?!")

        for f in r["tree"]:
            if f["path"] in self.blacklist:
                continue

            if (self.gui != None) and (self.text != None):
                self.gui.loop_start()

                self.text.fg = (255, 255, 0)
                self.text.setText("OTA", "bitmap6")
                self.text.draw(0, 6 * 0, False)

                self.text.fg = (255, 0, 255)
                self.text.setText(commit[ 0 :  5], "bitmap6")
                self.text.draw(0, 6 * 1, False)

                self.text.fg = (0, 255, 255)
                self.text.setText("Get", "bitmap6")
                self.text.draw(0, 6 * 2, False)

                self.text.fg = (0, 255, 0)
                self.text.setText(f["path"][0 : 5], "bitmap6")
                self.text.draw(0, 6 * 3, False)

                self.text.setText(f["path"][5 : ], "bitmap6")
                self.text.draw(0, 6 * 4, False)

                self.gui.loop_end()

            gc.collect()
            if hasattr(gc, "mem_free"):
                print("Collected Garbage:", gc.mem_free())

            # get a file from a commit
            r = self.fetch(self.host + "/" + self.repo + "/raw/commit/" + commit + "/" + f["path"]).text

            if verbose:
                print("Writing " + f["path"] + " to " + self.update_path)

            if (self.gui != None) and (self.text != None):
                self.gui.loop_start()

                self.text.fg = (255, 255, 0)
                self.text.setText("OTA", "bitmap6")
                self.text.draw(0, 6 * 0, False)

                self.text.fg = (255, 0, 255)
                self.text.setText(commit[ 0 :  5], "bitmap6")
                self.text.draw(0, 6 * 1, False)

                self.text.fg = (255, 0, 0)
                self.text.setText("Write", "bitmap6")
                self.text.draw(0, 6 * 2, False)

                self.text.fg = (0, 255, 0)
                self.text.setText(f["path"][0 : 5], "bitmap6")
                self.text.draw(0, 6 * 3, False)

                self.text.setText(f["path"][5 : ], "bitmap6")
                self.text.draw(0, 6 * 4, False)

                self.gui.loop_end()

            # overwrite existing file
            fo = open(self.update_path + "/" + f["path"], "w")
            fo.write(r)
            fo.close()

            if f["path"] == self.exe_path:
                if verbose:
                    print("Writing " + f["path"] + " to main.py")

                fo = open(self.update_path + "/main.py", "w")
                fo.write(r)
                fo.close()

        # Write new commit id to local file
        f = open(self.update_path + "/" + self.version_file, "w")
        f.write(commit + "\n")
        f.close()

def non_pico_ota_test(ota):
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    ota.path("tmp")

    print("Checking for updates")
    newer, commit = ota.check(True)
    print()

    # Just for testing
    previous = ota.get_previous_commit(commit)
    print("Previous commit (-1):", previous)
    previous = ota.get_previous_commit(previous)
    print("Previous commit (-2):", previous)
    print()

    if newer:
        print("Updating")
        ota.update_to_commit(commit, True)
    else:
        print("No update required")

if on_pico:
    from pico import PicoText
    i = util.getInput()
    t = util.getTarget(i)
    s = PicoText(t)

def pico_ota_run(ota):
    gc.collect()
    print("Collected Garbage:", gc.mem_free())

    t.loop_start()

    s.fg = (255, 255, 0)
    s.setText("OTA", "bitmap6")
    s.draw(0, 6 * 0, False)

    s.fg = (0, 255, 255)
    s.setText("Check", "bitmap6")
    s.draw(0, 6 * 2, False)

    t.loop_end()

    gc.collect()
    print("Collected Garbage:", gc.mem_free())

    print("Checking for updates")
    newer, commit = ota.check(True)

    gc.collect()
    print("Collected Garbage:", gc.mem_free())

    if newer:
        t.loop_start()

        s.fg = (255, 255, 0)
        s.setText("OTA", "bitmap6")
        s.draw(0, 6 * 0, False)

        s.fg = (255, 0, 255)
        s.setText(commit[ 0 :  5], "bitmap6")
        s.draw(0, 6 * 1, False)

        s.setText(commit[ 5 : 10], "bitmap6")
        s.draw(0, 6 * 2, False)

        s.setText(commit[10 : 15], "bitmap6")
        s.draw(0, 6 * 3, False)

        s.setText(commit[15 : 20], "bitmap6")
        s.draw(0, 6 * 4, False)

        t.loop_end()

        print("Updating to:", commit)
        ota.update_to_commit(commit, True)

        print("Resetting")
        machine.soft_reset()
    else:
        t.loop_start()

        s.fg = (255, 255, 0)
        s.setText("OTA", "bitmap6")
        s.draw(0, 6 * 0, False)

        s.fg = (0, 255, 0)
        s.setText("Done!", "bitmap6")
        s.draw(0, 6 * 1, False)

        s.fg = (255, 0, 255)
        s.setText("Boot", "bitmap6")
        s.draw(0, 6 * 2, False)

        s.fg = (0, 255, 255)
        s.setText("camp_pico.py"[0 : 5], "bitmap6")
        s.draw(0, 6 * 3, False)

        s.setText("camp_pico.py"[5 : ], "bitmap6")
        s.draw(0, 6 * 4, False)

        t.loop_end()

    fallback = False

    try:
        gc.collect()
        print("Collected Garbage:", gc.mem_free())

        print("Starting Application")
        import camp_pico
    except Exception as e:
        print()
        if hasattr(sys, "print_exception"):
            sys.print_exception(e)
        else:
            print(e)
        print()

        print("Falling back to previous")
        fallback = True

    # TODO this would immediately cause another update on reboot
    # TODO set a flag to prevent updates after fallbacks?
    # TODO or better, blacklist failed commit_id!
    #if fallback:
    #    previous = ota.get_previous_commit(commit, True)
    #    ota.update_to_commit(previous, True)
    #    machine.soft_reset()

ota = PicoOTA("https://git.xythobuz.de", "thomas/rgb-matrix-visualizer")

# stuff not needed on Pico
ota.ignore(".gitignore")
ota.ignore("README.md")
ota.ignore("copy.sh")
ota.ignore("config.py")
ota.ignore("fonts")
ota.ignore("hardware")
ota.ignore("images")
ota.ignore("bdf.py")
ota.ignore("camp_small.py")
ota.ignore("gamepad.py")
ota.ignore("pi.py")
ota.ignore("test.py")

if not on_pico:
    non_pico_ota_test(ota)
else:
    ota.exe("pico_ota.py")
    ota.ui(t, s)
    pico_ota_run(ota)
