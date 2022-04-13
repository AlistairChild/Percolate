# """Copyright (c) 2021 Alistair Child

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE."""


# import numpy as np

# from percolate.toolkit.find_array_equivalent import find_array_equivalent
# from percolate.toolkit.make_zero_array import make_zero_array


# def calculate_results1(x, y, lowerx, upperx, power, offset):

#     """Taking the x and y coordinates and the upper and lower x energies to fit"""

#     if y.ndim == 1:

#         arr_lower_lim = int(find_array_equivalent(x, lowerx))
#         arr_upper_lim = int(find_array_equivalent(x, upperx))

#         if offset == "off":

#             if arr_lower_lim <= arr_upper_lim:

#                 x_cut = np.concatenate((x[:arr_lower_lim], x[arr_upper_lim:]), axis=0)
#                 y_cut = np.concatenate((y[:arr_lower_lim], y[arr_upper_lim:]), axis=0)

#             elif arr_lower_lim > arr_upper_lim:

#                 x_cut = np.concatenate((x[:arr_upper_lim], x[arr_lower_lim:]), axis=0)
#                 y_cut = np.concatenate((y[:arr_upper_lim], y[arr_lower_lim:]), axis=0)
#         else:

#             offset = y[arr_lower_lim] - y[arr_upper_lim]

#             if arr_lower_lim <= arr_upper_lim:

#                 x_cut = np.concatenate((x[:arr_lower_lim], x[arr_upper_lim:]), axis=0)
#                 y_cut = np.concatenate(
#                     (y[:arr_lower_lim], y[arr_upper_lim:] + offset), axis=0
#                 )

#             elif arr_lower_lim > arr_upper_lim:

#                 x_cut = np.concatenate((x[:arr_upper_lim], x[arr_lower_lim:]), axis=0)
#                 y_cut = np.concatenate(
#                     (y[:arr_upper_lim], y[arr_lower_lim:] + offset), axis=0
#                 )

#         a_poly = np.polyfit(x_cut, y_cut, power)
#         a_polygen = np.poly1d(a_poly)
#         ia_bg = [a_polygen(e) for e in x]

#         a_bg = np.array(ia_bg)
#         a_p_norm = y - a_bg

#     elif absorption.ndim == 2:

#         print("Deal with at a higher level to avoid clutter")

#     return x, a_p_norm, a_bg


# def Fit_outside_limits_polynomial(
#     x: np.ndarray, y: np.ndarray, lowerx: float, upperx: float, power: int, offset: str
# ):

#     if lowerx and upperx and power and x.any() and y.any() and offset:

#         return calculate_results1(x, y, lowerx, upperx, power, offset)

#     else:

#         return x, y, make_zero_array(x)
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
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.make_zero_array import make_zero_array


def calculate_results1(x, y, lowerx, upperx, power, offset):

    """Taking the x and y coordinates and the upper and lower x energies to fit"""

    print("Fitting polynomial outside limit")
    if offset == "off":
        applyoffset = False
    else:
        applyoffset = True

    def func_pow1(x, a, b):
        return a*x + b
    def func_pow2(x, a, b, c):
        return a*x*x + b*x + c
    def func_pow3(x, a, b, c, d):
        return a*x*x*x + b*x*x + c*x + d


    arr_lower_lim = int(find_array_equivalent(x, lowerx))
    arr_upper_lim = int(find_array_equivalent(x, upperx))

    limits = y[arr_upper_lim]- y[arr_lower_lim]


    z_bin = np.linspace(-2*limits, 2*limits, 60)
    a_bg_final  = y
    max_r2 = 0



    
    if applyoffset:
        for i in range(len(z_bin) - 1):
            a_offset1 = z_bin[i]

            #print(a_offset1)

            e_cut = (
                np.concatenate(
                    (
                        x[: arr_lower_lim],
                        x[arr_upper_lim :],
                    )
                )
                -x[0]
            )
            a_cut = np.concatenate(
                (
                    y[: arr_lower_lim],
                    y[arr_upper_lim :]
                    - a_offset1,
                )
            )
            transposed_energy = x - x[0]
            # fit values, and mean


            if power ==1:
                popt, pcov = curve_fit(func_pow1, e_cut, a_cut)
                a_bg = func_pow1(transposed_energy, *popt)
            elif power==2:
                popt, pcov = curve_fit(func_pow2, e_cut, a_cut)
                a_bg = func_pow2(transposed_energy, *popt)
            elif power==3:
                popt, pcov = curve_fit(func_pow3, e_cut, a_cut)
                a_bg = func_pow3(transposed_energy, *popt)

            a_bg_cut = np.concatenate((a_bg[: arr_lower_lim], a_bg[arr_upper_lim:]))
            
            

            if r2_score(a_bg_cut, a_cut)>max_r2:
                a_bg_final = a_bg
                max_r2 = r2_score(a_bg_cut, a_cut)
    else:

        e_cut = (
            np.concatenate(
                (
                    x[: arr_lower_lim],
                    x[arr_upper_lim :],
                )
            )
            -x[0]
        )
        a_cut = np.concatenate(
            (
                y[: arr_lower_lim],
                y[arr_upper_lim :],
            )
        )
        transposed_energy = x - x[0]
        if power ==1:
            popt, pcov = curve_fit(func_pow1, e_cut, a_cut)
            a_bg = func_pow1(transposed_energy, *popt)
        elif power==2:
            popt, pcov = curve_fit(func_pow2, e_cut, a_cut)
            a_bg = func_pow2(transposed_energy, *popt)
        elif power==3:
            popt, pcov = curve_fit(func_pow3, e_cut, a_cut)
            a_bg = func_pow3(transposed_energy, *popt)

        a_bg_cut = np.concatenate((a_bg[: arr_lower_lim], a_bg[arr_upper_lim:]))
  
        max_r2 = r2_score(a_bg_cut, a_cut)
        a_bg_final = a_bg

    print("R^2 score : %s"%max_r2)
    
    return x, y - a_bg_final, a_bg_final


def Fit_outside_limits_polynomial(
    x: np.ndarray, y: np.ndarray, lowerx: float, upperx: float, power: int, offset: str
):

    if lowerx and upperx and power and x.any() and y.any() and offset:

        return calculate_results1(x, y, lowerx, upperx, power, offset)

    else:

        return x, y, make_zero_array(x)