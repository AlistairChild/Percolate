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

# standard
import numpy as np

# created functions.
from percolate.toolkit.find_array_equivalent import find_array_equivalent


def Transpose_spectra(energy, absorption, args):
    """Transpose_spectra(energy, absorption, args) requires args.x_value_for_transpose and args.action"""
    loc_energy = np.array(energy)
    loc_absorption = np.array(absorption)

    if len(np.array(loc_absorption).shape) > 1:
        n_files = len(np.array(loc_absorption))
    else:
        n_files = 1

    transposed_spectra = []

    for i in range(n_files):

        if args.action == "on":
            transposed_spectra_i = (
                loc_absorption[i]
                - loc_absorption[i][
                    find_array_equivalent(loc_energy[i], args.x_value_for_transpose)
                ]
            )

        else:
            transposed_spectra_i = loc_absorption[i]

        transposed_spectra.append(transposed_spectra_i)

    return transposed_spectra
