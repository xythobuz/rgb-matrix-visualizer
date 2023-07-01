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

# to check if we're actually running on MicroPython
on_pico = False
try:
    import uos
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
        self.blacklist = []

    def path(self, p):
        self.update_path = p

    def ignore(self, path):
        if not path in self.blacklist:
            self.blacklist.append(path)

    def fetch(self, url):
        # lazily initialize WiFi
        if self.get == None:
            self.get = util.getRequests()
            if self.get == None:
                return None

        try:
            #print("GET " + url)
            r = self.get(url)
            r.close()
            return r
        except Exception as e:
            print()
            if hasattr(sys, "print_exception"):
                sys.print_exception(e)
            else:
                print(e)
            print()
            return None

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

        current = ""
        try:
            f = open(os.path.join(self.update_path, "ota_version"), "r")
            current = f.readline().strip()
            f.close()
        except Exception as e:
            print()
            if hasattr(sys, "print_exception"):
                sys.print_exception(e)
            else:
                print(e)
            print()

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

            # get a file from a commit
            r = self.fetch(self.host + "/" + self.repo + "/raw/commit/" + commit + "/" + f["path"]).text

            if verbose:
                print("Writing " + f["path"] + " to " + self.update_path)

            # overwrite existing file
            f = open(os.path.join(self.update_path, f["path"]), "w")
            f.write(r)
            f.close()

        # Write new commit id to local file
        f = open(os.path.join(self.update_path, "ota_version"), "w")
        f.write(commit + os.linesep)
        f.close()

if __name__ == "__main__":
    ota = PicoOTA("https://git.xythobuz.de", "thomas/rgb-matrix-visualizer")

    # stuff not needed on Pico
    ota.ignore(".gitignore")
    ota.ignore("README.md")
    ota.ignore("copy.sh")
    ota.ignore("config.py")
    ota.ignore("fonts")
    ota.ignore("images")
    ota.ignore("bdf.py")
    ota.ignore("camp_small.py")
    ota.ignore("gamepad.py")
    ota.ignore("pi.py")
    ota.ignore("test.py")

    if not on_pico:
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        ota.path("tmp")

    newer, commit = ota.check(True)
    if newer:
        ota.update_to_commit(commit, True)
