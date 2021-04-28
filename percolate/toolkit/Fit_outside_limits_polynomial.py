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


import numpy as np

from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.make_zero_array import make_zero_array


def calculate_results1(x, y, lowerx, upperx, power):

    """Taking the x and y coordinates and the upper and lower x energies to fit"""

    if y.ndim == 1:

        arr_lower_lim = int(find_array_equivalent(x, lowerx))
        arr_upper_lim = int(find_array_equivalent(x, upperx))

        if arr_lower_lim <= arr_upper_lim:

            x_cut = np.concatenate((x[:arr_lower_lim], x[arr_upper_lim:]), axis=0)
            y_cut = np.concatenate((y[:arr_lower_lim], y[arr_upper_lim:]), axis=0)

        elif arr_lower_lim > arr_upper_lim:

            x_cut = np.concatenate((x[:arr_upper_lim], x[arr_lower_lim:]), axis=0)
            y_cut = np.concatenate((y[:arr_upper_lim], y[arr_lower_lim:]), axis=0)

        a_poly = np.polyfit(x_cut, y_cut, power)
        a_polygen = np.poly1d(a_poly)
        ia_bg = [a_polygen(e) for e in x]

        a_bg = np.array(ia_bg)
        a_p_norm = y - a_bg

    elif absorption.ndim == 2:

        print("Deal with at a higher level to avoid clutter")

    return x, a_p_norm, a_bg


def Fit_outside_limits_polynomial(
    x: np.ndarray, y: np.ndarray, lowerx: float, upperx: float, power: int
):

    if lowerx and upperx and power and x.any() and y.any():

        return calculate_results1(x, y, lowerx, upperx, power)

    else:

        return x, y, make_zero_array(x)
