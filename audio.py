#!/usr/bin/env python3

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <xythobuz@xythobuz.de> wrote this file.  As long as you retain this notice
# you can do whatever you want with this stuff. If we meet some day, and you
# think this stuff is worth it, you can buy me a beer in return.   Thomas Buck
# ----------------------------------------------------------------------------

import time
import pyaudio
import numpy as np

class AudioVisualizer:
    def __init__(self, g, f = 20, t = 60.0, fft = True):
        self.gui = g
        self.interval = 1.0 / f
        self.timeout = t
        self.do_fft = fft

        self.chunk = 1024 * 2 # stereo

        self.p = pyaudio.PyAudio()
        self.s = self.p.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True)
        print(self.s)

    def restart(self):
        self.data = self.init()
        self.start = time.time()

    def finished(self):
        if (time.time() - self.start) >= self.timeout:
            return True
        return FALSE

    def draw_line(self, x, val, y_off):
        h = int(val) / 32768.0 * self.gui.height / 2
        self.gui.set_pixel(x, y_off + (16 - h), (255, 255, 255))

    def draw_bar(self, x, val, y_off, max_val):
        if max_val <= 0.0:
            max_val = 1.0
        h = int(val) / float(max_val) * self.gui.height / 2
        for y in range(0, int(h)):
            self.gui.set_pixel(x, y_off + (32 - y), (255, 255, 255))

    # stolen from https://github.com/aiXander/Realtime_PyAudio_FFT/blob/master/src/fft.py
    def calc_fft(self, data):
        data = data * np.hamming(len(data))
        try:
            fft = np.abs(np.fft.rfft(data)[1:])
        except:
            fft = np.fft.fft(data)
            left, right = np.split(np.abs(fft), 2)
            fft = np.add(left, right[::-1])

        #try:
        #    fft = np.multiply(20, np.log10(fft))
        #except:
        #    pass

        return fft

    def draw(self):
        frames = self.s.read(self.chunk)

        left = frames[::4] # start from first left sample (index 0), skip 4 bytes (2 * 2, int16 and stereo)
        left = np.frombuffer(left, dtype=np.int16)

        right = frames[2::4] # start from first right sample (index 2), skip 4 bytes
        right = np.frombuffer(right, dtype=np.int16)

        if self.do_fft:
            # FFT
            left = self.calc_fft(left)
            right = self.calc_fft(right)

        # average down to fit screen
        m = self.chunk / 2 / self.gui.width # stereo
        if self.do_fft:
            m = m / 2
        left = left.reshape(-1, int(m)).mean(axis=1)
        right = right.reshape(-1, int(m)).mean(axis=1)

        l_max = max(left)
        r_max = max(right)

        for x in range(0, self.gui.width):
            if self.do_fft:
                self.draw_bar(x, left[x], 0, l_max)
                self.draw_bar(x, right[x], self.gui.height / 2, r_max)
            else:
                self.draw_line(x, left[x], 0)
                self.draw_line(x, right[x], self.gui.height / 2)

if __name__ == "__main__":
    import util
    i = util.getInput()
    t = util.getTarget(i)
    a = AudioVisualizer(t)
    util.loop(t, a.draw)
