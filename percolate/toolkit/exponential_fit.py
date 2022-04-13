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
# Toolkit imports
from percolate.toolkit.find_array_equivalent import find_array_equivalent

def exponential_decay(x, y_in,lower_limit, upper_limit, a_offset1 = 0):
    print("Fitting Exponential")
    limits = y_in[find_array_equivalent(x, upper_limit)]- y_in[find_array_equivalent(x, lower_limit)]

    z_bin = np.linspace(-limits, limits, 20)
    a_bg_final  = y_in
    max_r2 = 0

    for i in range(len(z_bin)-1):
        a_offset1 = z_bin[i]

        #print(a_offset1)

        e_cut = (
            np.concatenate(
                (
                    x[: find_array_equivalent(x, lower_limit)],
                    x[find_array_equivalent(x, upper_limit) :],
                )
            )
            -x[0]
        )
        a_cut = np.concatenate(
            (
                y_in[: find_array_equivalent(x, lower_limit)],
                y_in[find_array_equivalent(x, upper_limit) :]
                - a_offset1,
            )
        )


        transposed_energy = x - x[0]
        # fit values, and mean
        def func(x, a, b, c, d):
            return a * np.exp(-b * x) + c * x + d

        
        popt, pcov = curve_fit(func, e_cut, a_cut)
        a_bg = func(transposed_energy, *popt)
        a_bg_cut = np.concatenate((a_bg[: find_array_equivalent(x, lower_limit)], a_bg[find_array_equivalent(x, upper_limit):]))

        

        if r2_score(a_bg_cut, a_cut)>max_r2:
            a_bg_final = a_bg
            max_r2 = r2_score(a_bg_cut, a_cut)
    print("R^2 score : %s"%max_r2)
    return x, y_in - a_bg_final, a_bg_final