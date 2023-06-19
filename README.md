# RGB Matrix Visualizer

Render various content to various output devices.

## Quick Start

Just run:

    ./manager.py

and go from there.

## Dependencies

You always need:

    pip install pil
    pip install bdfparser
    pip install "qrcode[pil]"
    pip install evdev

For evdev to find all devices you may need to add your user to the `input` group or run the scripts as root.

The rest depends on the output device chosen.
For debugging on your host PC you can use the TestGUI interface with pygame:

    pip install pygame

The other currently supported option is using a Raspberry Pi with the [Adafruit RGB Matrix Bonnet](https://shop.pimoroni.com/products/adafruit-rgb-matrix-bonnet-for-raspberry-pi?variant=2257849155594) and a matching [LED Matrix](https://shop.pimoroni.com/products/rgb-led-matrix-panel?variant=35962488650).
The [tutorial](https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi/driving-matrices) suggests using the [Adafruit Raspberry Pi Installer Script for the RGB matrix](https://github.com/adafruit/Raspberry-Pi-Installer-Scripts/blob/339cccfbdd8b503b53186176ff96bead9a13a2f5/rgb-matrix.sh).
This will give you the [hzeller/rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) project which includes the Python bindings used in this project.

## Adding your own visualizations

Take a look how others are implemented.
You can chain the different screens together using `Manager` and also check for conditions, as seen in `CheckHTTP`.
This should enable you to quickly create something usable.

One goal is to run this project on public events.
If this is the case, and you want your own message to appear, simply open up a PR or send an email with a patch.
Because of different versions between host PCs and the Raspbian OS, things may look slightly different, especially regarding stuff like animated GIF viewing.

## Licensing

This project is licensed as beer-ware:

    ----------------------------------------------------------------------------
    "THE BEER-WARE LICENSE" (Revision 42):
    <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
    you can do whatever you want with this stuff. If we meet some day, and you
    think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
    ----------------------------------------------------------------------------

The included fonts from [farsil/ibmfonts](https://github.com/farsil/ibmfonts) are licensed as `CC-BY-SA-4.0`.

The fonts from [cmvnd/fonts](https://github.com/cmvnd/fonts) are licensed as GPLv3.

The tiny font is from [robey](https://robey.lag.net/2010/01/23/tiny-monospace-font.html) and licensed as CC0.

The included GIFs are from [GifCities](https://gifcities.org/?q=32).
