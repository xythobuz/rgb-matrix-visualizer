#!/usr/bin/env python3

# Requires openpyxl and openpyxl_image_loader.
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import sys
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader

if __name__ != "__main__":
    raise RuntimeError("Please run this file directly")

if len(sys.argv) < 2:
    raise RuntimeError("Please pass input file as argument")

wb = load_workbook(filename = sys.argv[1])
ws = wb.active
image_loader = SheetImageLoader(ws)

data = []

for row in ws:
    try:
        id = int(row[0].value)
    except:
        continue

    text = str(row[1].value)
    #print("id={} text='{}'".format(id, text))

    if not image_loader.image_in(row[2].coordinate):
        print("No image found for ID {}".format(id))
        image = None
    else:
        image = image_loader.get(row[2].coordinate)

    data.append((
        id, text, image
    ))

print("Found {} IDs:".format(len(data)))
print()

print("    self.descriptions = [")
for d in data:
    if d[2] != None:
        img_name = "weather_icon_{}.png".format(d[0])
        d[2].save(img_name)
        img_name = "'" + img_name + "'"
    else:
        img_name = "None"
    print("        ({}, '{}', {}),".format(d[0], d[1], img_name))
print("    ]")
print()
