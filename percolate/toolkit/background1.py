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

# Toolkit imports
from percolate.toolkit.find_array_equivalent import find_array_equivalent


def background1(energy, absorption, args):

    loc_energy = np.array(energy)
    loc_absorption = np.array(absorption)

    if len(np.array(loc_absorption).shape) > 1:
        n_files = len(np.array(loc_absorption))
    else:
        n_files = 1

    a_bg = []
    a_p_norm = []

    for i in range(n_files):
        # if we have inital values
        if args.p_end and args.p_start:
            # Calc absorption level difference between end of pre-edge and start of post-edge
            if args.apply_offset == "off":
                a_offset = 0
                a_offset1 = 0
            else:
                # move post edge to preedge for fitting if called.
                post_edge_intensity = loc_absorption[i][
                    find_array_equivalent(loc_energy[i], args.p_end)
                ]
                pre_edge_intensity = loc_absorption[i][
                    find_array_equivalent(loc_energy[i], args.p_start)
                ]
                a_offset = post_edge_intensity - pre_edge_intensity

                # polynomial
            if (
                args.fit
                == "linear (fits for all e < 'Background_start' and e > ' Background_end') "
            ):
                # Polyfit and generate background series from it
                e_cut = np.concatenate(
                    (
                        loc_energy[i][
                            : find_array_equivalent(loc_energy[i], args.p_start)
                        ],
                        loc_energy[i][
                            find_array_equivalent(loc_energy[i], args.p_end) :
                        ],
                    )
                )
                a_cut = np.concatenate(
                    (
                        loc_absorption[i][
                            : find_array_equivalent(loc_energy[i], args.p_start)
                        ],
                        (
                            loc_absorption[i][
                                find_array_equivalent(loc_energy[i], args.p_end) :
                            ]
                            - a_offset
                        ),
                    )
                )
                a_poly = np.polyfit(e_cut, a_cut, 1)

                a_polygen = np.poly1d(a_poly)
                ia_bg = [a_polygen(e) for e in loc_energy[i]]

            if args.fit == "polynomial (fits for energies inside limits) ":
                # Polyfit and generate background series from it
                # e_cut = loc_energy[i] [ find_array_equivalent(loc_energy[i], args.p_start) : find_array_equivalent(loc_energy[i], args.p_end) ]
                # a_cut = loc_absorption[i] [ find_array_equivalent(loc_energy[i], args.p_start) : find_array_equivalent(loc_energy[i], args.p_end) ]

                if find_array_equivalent(
                    loc_energy[i], args.p_end
                ) <= find_array_equivalent(loc_energy[i], args.p_start):

                    e_cut = loc_energy[i][
                        find_array_equivalent(
                            loc_energy[i], args.p_end
                        ) : find_array_equivalent(loc_energy[i], args.p_start)
                    ]
                    a_cut = loc_absorption[i][
                        find_array_equivalent(
                            loc_energy[i], args.p_end
                        ) : find_array_equivalent(loc_energy[i], args.p_start)
                    ]

                elif find_array_equivalent(
                    loc_energy[i], args.p_start
                ) < find_array_equivalent(loc_energy[i], args.p_end):

                    e_cut = loc_energy[i][
                        find_array_equivalent(
                            loc_energy[i], args.p_start
                        ) : find_array_equivalent(loc_energy[i], args.p_end)
                    ]
                    a_cut = loc_absorption[i][
                        find_array_equivalent(
                            loc_energy[i], args.p_start
                        ) : find_array_equivalent(loc_energy[i], args.p_end)
                    ]

                a_poly = np.polyfit(e_cut, a_cut, args.power)

                a_polygen = np.poly1d(a_poly)
                ia_bg = [a_polygen(e) for e in loc_energy[i]]

            if (
                args.fit
                == "polynomial (fits for all e < 'Background_start' and e > ' Background_end')"
            ):
                # Polyfit and generate background series from it
                e_cut = np.concatenate(
                    (
                        loc_energy[i][
                            : find_array_equivalent(loc_energy[i], args.p_start)
                        ],
                        loc_energy[i][
                            find_array_equivalent(loc_energy[i], args.p_end) :
                        ],
                    )
                )
                a_cut = np.concatenate(
                    (
                        loc_absorption[i][
                            : find_array_equivalent(loc_energy[i], args.p_start)
                        ],
                        (
                            loc_absorption[i][
                                find_array_equivalent(loc_energy[i], args.p_end) :
                            ]
                            - a_offset
                        ),
                    )
                )
                a_poly = np.polyfit(e_cut, a_cut, args.power)

                a_polygen = np.poly1d(a_poly)
                ia_bg = [a_polygen(e) for e in loc_energy[i]]

                # exponential decay
            elif (
                args.fit
                == "exp decay (fits for all e < 'Background_start' and e > ' Background_end')"
            ):

                a_offset1 = 0  # ppp1-ooo1
                e_cut = (
                    np.concatenate(
                        (
                            loc_energy[i][
                                : find_array_equivalent(loc_energy[i], args.p_start)
                            ],
                            loc_energy[i][
                                find_array_equivalent(loc_energy[i], args.p_end) :
                            ],
                        )
                    )
                    - 750
                )
                a_cut = np.concatenate(
                    (
                        loc_absorption[i][
                            : find_array_equivalent(loc_energy[i], args.p_start)
                        ],
                        loc_absorption[i][
                            find_array_equivalent(loc_energy[i], args.p_end) :
                        ]
                        - a_offset1,
                    )
                )

                transposed_energy = np.asarray(loc_energy[i]) - 750
                # fit values, and mean
                def func(x, a, b, c):
                    return a * np.exp(-b * x) + c

                y = func(transposed_energy, 2.3, 1.3, 1)
                popt, pcov = curve_fit(func, e_cut, a_cut)
                ia_bg = func(transposed_energy, *popt)

                # fit only considered 2 points at edge_start_index and edge_stop_index
            elif args.fit == "2 point linear (straight line between 2 points)":
                e_cut = [
                    loc_energy[i][find_array_equivalent(loc_energy[i], args.p_start)],
                    loc_energy[i][find_array_equivalent(loc_energy[i], args.p_end)],
                ]
                a_cut = [
                    loc_absorption[i][
                        find_array_equivalent(loc_energy[i], args.p_start)
                    ],
                    loc_absorption[i][find_array_equivalent(loc_energy[i], args.p_end)],
                ]

                a_poly = np.polyfit(e_cut, a_cut, 1)
                a_polygen = np.poly1d(a_poly)

                ia_bg = [a_polygen(e) for e in loc_energy[i]]

            elif args.fit == "No fit":
                ia_bg = np.zeros(len(loc_absorption[i]))

        else:
            ia_bg = np.zeros(len(loc_absorption[i]))

        ia_bg = np.array(ia_bg)

        ia_p_norm = np.array(loc_absorption[i]) - np.array(ia_bg)
        a_p_norm.append(ia_p_norm)
        a_bg.append(ia_bg)

    return a_bg, a_p_norm
