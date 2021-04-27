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

# Toolkit inmport
from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.zerolistmaker import zerolistmaker


def background_xmcd(energy, xmcd, args):

    loc_energy = np.array(energy)
    loc_absorption = np.array(xmcd)

    if len(np.array(loc_absorption).shape) > 1:
        n_files = len(np.array(loc_absorption))
    else:
        n_files = 1

    a_bg = []
    a_p_norm = []

    if args.fit == "linear":
        # Polyfit and generate background series from it
        e_cut = np.concatenate(
            (
                loc_energy[: find_array_equivalent(loc_energy, args.background_start)],
                loc_energy[find_array_equivalent(loc_energy, args.background_stop) :],
            )
        )
        a_cut = np.concatenate(
            (
                loc_absorption[
                    : find_array_equivalent(loc_energy, args.background_start)
                ],
                (
                    loc_absorption[
                        find_array_equivalent(loc_energy, args.background_stop) :
                    ]
                ),
            )
        )
        a_poly = np.polyfit(e_cut, a_cut, 1)

        a_polygen = np.poly1d(a_poly)
        ia_bg = [a_polygen(e) for e in loc_energy]

    if args.fit == "polynomial":
        # Polyfit and generate background series from it
        e_cut = np.concatenate(
            (
                loc_energy[: find_array_equivalent(loc_energy, args.background_start)],
                loc_energy[find_array_equivalent(loc_energy, args.background_stop) :],
            )
        )
        a_cut = np.concatenate(
            (
                loc_absorption[
                    : find_array_equivalent(loc_energy, args.background_start)
                ],
                (
                    loc_absorption[
                        find_array_equivalent(loc_energy, args.background_stop) :
                    ]
                ),
            )
        )
        a_poly = np.polyfit(e_cut, a_cut, args.power)

        a_polygen = np.poly1d(a_poly)
        ia_bg = [a_polygen(e) for e in loc_energy]

        # exponential decay
    elif args.fit == "exp decay":

        a_offset1 = 0  # ppp1-ooo1
        e_cut = (
            np.concatenate(
                (
                    loc_energy[
                        : find_array_equivalent(loc_energy, args.background_start)
                    ],
                    loc_energy[
                        find_array_equivalent(loc_energy, args.background_stop) :
                    ],
                )
            )
            - 750
        )
        a_cut = np.concatenate(
            (
                loc_absorption[
                    : find_array_equivalent(loc_energy, args.background_start)
                ],
                loc_absorption[
                    find_array_equivalent(loc_energy, args.background_stop) :
                ],
            )
        )

        transposed_energy = np.asarray(loc_energy) - 750
        # fit values, and mean
        def func(x, a, b, c):
            return a * np.exp(-b * x) + c

        y = func(transposed_energy, 2.3, 1.3, 1)
        popt, pcov = curve_fit(func, e_cut, a_cut)
        ia_bg = func(transposed_energy, *popt)

        # fit only considered 2 points at edge_start_index and edge_stop_index
    elif args.fit == "2 point linear":
        e_cut = [
            loc_energy[find_array_equivalent(loc_energy, args.background_start)],
            loc_energy[find_array_equivalent(loc_energy, args.background_stop)],
        ]
        a_cut = [
            loc_absorption[find_array_equivalent(loc_energy, args.background_start)],
            loc_absorption[find_array_equivalent(loc_energy, args.background_stop)],
        ]
        a_poly = np.polyfit(e_cut, a_cut, 1)
        a_polygen = np.poly1d(a_poly)
        ia_bg = [a_polygen(e) for e in loc_energy]

    elif args.fit == "Do Nothing!!":
        ia_bg = np.zeros(len(loc_energy))
    # for i in range(n_files):

    # fit only considered 2 points at edge_start_index and edge_stop_index

    # e_cut=[loc_energy[find_array_equivalent(loc_energy, args.background_start)],loc_energy[find_array_equivalent(loc_energy, args.background_stop)]]
    # a_cut=[loc_xmcd[find_array_equivalent(loc_energy, args.background_start)],loc_xmcd[find_array_equivalent(loc_energy, args.background_stop)]]

    # a_poly=np.polyfit(e_cut, a_cut, 1)
    # a_polygen = np.poly1d(a_poly)
    # ia_bg = [a_polygen(e) for e in loc_energy]

    background = np.array(ia_bg)

    subtracted_background = np.array(loc_absorption) - np.array(ia_bg)
    # a_p_norm.append(subtracted_background)
    # a_bg.append(background)

    return background, subtracted_background
