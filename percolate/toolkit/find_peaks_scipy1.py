"""Copyright (c) 2021 Alistair Child

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


import scipy
import numpy as np
import scipy.signal


def find_max(array):

    max = array[0]
    for i in range(len(array)):
        if array[i] > max:
            max = array[i]
    return max


def find_min(array):

    min = array[0]
    for i in range(len(array)):
        if array[i] < min:
            min = array[i]
    return min


def find_peaks_scipy1(xs, ys):

    if len(np.array(xs).shape) > 1:

        if len(xs[0]) == 1:
            xs = xs[0]
            ys = ys[0]

        if len(xs[0]) > 1:
            xs = np.mean(xs, axis=0)[0]
            ys = np.mean(ys, axis=0)[0]
    min = find_min(ys)
    height = (find_max(ys) - find_min(ys)) / 6
    peaks, _ = scipy.signal.find_peaks(ys - min, height=height, width=10)
    return peaks
