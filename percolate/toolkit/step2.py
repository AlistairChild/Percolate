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
from percolate.toolkit.find_peaks_scipy1 import find_peaks_scipy1
from scipy.special import comb
import scipy

# toolkit imports
from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.zerolistmaker import zerolistmaker


def smoothstep(x, x_min=0, x_max=1, N=8):
    x = np.clip((x - x_min) / (x_max - x_min), 0, 1)
    result = 0
    for n in range(0, N + 1):
        result += comb(N + n, n) * comb(2 * N + 1, N - n) * (-x) ** n
    result *= x ** (N + 1)
    return result


def find_peaks_scipy(xs, ys):

    height = max(ys) / 4
    peaks, _ = scipy.signal.find_peaks(xs, height=height)
    return peaks


def step2(energy, absorption, other_spectra, args):

    loc_energy = energy
    loc_absorption = absorption
    loc_other_spectra = other_spectra

    if len(np.array(loc_absorption).shape) > 1:
        n_files = len(np.array(loc_absorption))
    else:
        n_files = 1

    step = []
    subtracted_step = []

    for i in range(n_files):

        if args.step_stop and args.step_start:

            if args.apply_step == "on":
                # L3_peak, L2_peak = Identify_peak_position(args, loc_energy, loc_absorption)
                peaks = find_peaks_scipy1(loc_energy[i], loc_absorption[i])

                L3_peak_pos = peaks[0]
                L2_peak_pos = peaks[1]
                # peak_fwhm_calculation(args, L3_peak, L2_peak)

                # find array point
                step_stop_energy = find_array_equivalent(loc_energy[i], args.step_stop)
                step_start_energy = find_array_equivalent(
                    loc_energy[i], args.step_start
                )
                step_intermediate_energy = find_array_equivalent(
                    loc_energy[i], args.step_intermediate
                )

                # dummy variables
                fit_type = 1
                l2_peak = L2_peak_pos
                l3_peak = L3_peak_pos

                # el3_cut = len(energy[int(l3_peak-l3_fwhm):int(l3_peak+l3_fwhm)])
                # el2_cut = len(energy[int(l2_peak-l2_fwhm):int(l2_peak+l2_fwhm)])
                el3_cut = len(loc_energy[i][int(l3_peak - 3) : int(l3_peak + 3)])
                el2_cut = len(loc_energy[i][int(l2_peak - 3) : int(l2_peak + 3)])
                # create a linspace of equal length.
                xl3 = np.linspace(0, 1, el3_cut)
                xl2 = np.linspace(0, 1, el2_cut)
                xl3_arctan = np.linspace(-10, 10, el3_cut)
                xl2_arctan = np.linspace(-10, 10, el2_cut)
                # make a step function using the linspace created.

                # voight or a tangent function
                if args.fit_function == "Voight":
                    y = smoothstep(xl3, N=4)
                    u = smoothstep(xl2, N=4)

                elif args.fit_function == "Arctan":
                    y = np.arctan(xl3_arctan)
                    u = np.arctan(xl2_arctan)
                    y = y - min(y)
                    u = u - min(u)
                    y = y / max(y)
                    u = u / max(u)

                if args.fit_type == "Alpha":
                    """
                    1-- Identifies the average intensity post step_stop and the intensity at step_start.
                    2-- Average the parallel and antiparallel spectra finding difference between average post step_stop and min post (L2 peak, pre step_stop)
                    -- Using this we take difference in intensitys of 1 and subtract 2 to get step height.
                    -- The step start is then shifted to intensity at step_start.

                    """
                    # absorption_difference = ((min(loc_absorption[i][l2_peak:find_array_equivalent(loc_energy[i], args.step_stop)])) - (loc_absorption[i][find_array_equivalent(loc_energy[i], args.step_start)])) / 3

                    # average both north and south spectra together.
                    average_spectra = (loc_absorption[i] + loc_other_spectra[i]) / 2

                    # find minima post L2_peak to step_stop
                    minima_post_l2_step_stop = min(
                        average_spectra[
                            l2_peak : find_array_equivalent(
                                loc_energy[i], args.step_stop
                            )
                        ]
                    )

                    # (mean intensity post step stop - step_start intensity) - (average spectra post step stop - minima post l2 peak)
                    absorption_difference = (
                        np.mean(loc_absorption[i][step_stop_energy:-1])
                        - (loc_absorption[i][step_start_energy])
                        - (
                            np.mean(average_spectra[step_stop_energy:-1])
                            - minima_post_l2_step_stop
                        )
                    ) / 3

                    # transpose the step to intensity at step start energy.
                    l3_transpose = loc_absorption[i][
                        find_array_equivalent(loc_energy[i], args.step_start)
                    ]

                elif args.fit_type == "Beta":

                    """
                    --Simply identifies the intensity at step_stop and step_start and takes difference to find step height
                            --step_start is then shifted so that it starts at step_start.
                            --The step is always centered at the peak position with height 2/3 at L3 peak and 1/3 at L2 peak.
                    """
                    # calculate difference in step stop and step start intensity
                    absorption_difference = (
                        loc_absorption[i][step_stop_energy]
                        - loc_absorption[i][step_start_energy]
                    ) / 3

                    # transpose the step to intensity at step start energy.
                    l3_transpose = loc_absorption[i][
                        find_array_equivalent(loc_energy[i], args.step_start)
                    ]

                else:
                    absorption_difference = (
                        (
                            min(average[l2_peak:edge_stop_index])
                            + (
                                np.mean(
                                    loc_absorption[i][height:]
                                    - np.mean(average[height:])
                                )
                            )
                        )
                        - (((average[edge_start_index])))
                    ) / 3
                    l3_transpose = loc_absorption[i][edge_start_index]

                y = y * absorption_difference * 2
                u = u * absorption_difference

                # find max gradient in steps
                l3_p = np.diff(y, n=1)
                oo = find_peaks_scipy(l3_p, l3_p)
                l2_p = np.diff(u, n=1)
                oooo = find_peaks_scipy(l2_p, l2_p)
                # create zeros up to L3 step
                pre = zerolistmaker(int(l3_peak - oo[0]) - 1)
                # concatenate
                pre_plus_l3 = np.concatenate([pre, y])
                # zeros of length than transpose to step.
                mid = (
                    zerolistmaker(l2_peak - oooo[0] - len(pre_plus_l3))
                    + pre_plus_l3[-1]
                )
                # concatenate
                pre_l3_mid = np.concatenate([pre_plus_l3, mid, (u + mid[-1])])
                # post region
                post = (
                    zerolistmaker(len(loc_energy[i]) - len(pre_l3_mid)) + pre_l3_mid[-1]
                )
                # concatenate
                total = np.concatenate([pre_l3_mid, post])
                total = total + l3_transpose

            elif args.apply_step == "off":

                # subtracted_step = loc_absorption[i]
                # stepfunction = np.zeros(len(loc_energy[i]))
                total = np.zeros(len(loc_energy[i]))

        # loc_energy = energy.read()[0]
        # loc_absorption = absorption.read()[0]

        else:
            total = np.zeros(len(loc_energy[i]))

        post_step = loc_absorption[i] - total

        step.append(total)
        subtracted_step.append(post_step)

    return step, subtracted_step


def step3(x, y, start, mid, end, function, fittype):

    if np.array(x).ndim == 1 and np.array(y).ndim == 1:

        # L3_peak, L2_peak = Identify_peak_position(args, loc_energy, loc_absorption)
        peaks = find_peaks_scipy1(x, y)
        L3_peak_pos = peaks[0]
        L2_peak_pos = peaks[1]
        # peak_fwhm_calculation(args, L3_peak, L2_peak)

        # find array point
        step_stop_arr = find_array_equivalent(x, end)
        step_start_arr = find_array_equivalent(x, start)
        step_intermediate_arr = find_array_equivalent(x, mid)

        # el3_cut = len(energy[int(l3_peak-l3_fwhm):int(l3_peak+l3_fwhm)])
        # el2_cut = len(energy[int(l2_peak-l2_fwhm):int(l2_peak+l2_fwhm)])
        el3_cut = len(x[int(L3_peak_pos - 10) : int(L3_peak_pos + 10)])
        el2_cut = len(x[int(L2_peak_pos - 10) : int(L2_peak_pos + 10)])
        # create a linspace of equal length.
        xl3 = np.linspace(0, 1, el3_cut)
        xl2 = np.linspace(0, 1, el2_cut)
        xl3_arctan = np.linspace(-10, 10, el3_cut)
        xl2_arctan = np.linspace(-10, 10, el2_cut)
        # make a step function using the linspace created.

        # voight or a tangent function
        if function == "Voight":
            yp = smoothstep(xl3, N=4)
            u = smoothstep(xl2, N=4)

        elif function == "Arctan":
            yp = np.arctan(xl3_arctan)
            u = np.arctan(xl2_arctan)
            yp = yp - min(yp)
            u = u - min(u)
            yp = yp / max(yp)
            u = u / max(u)

        if fittype == "Beta" or "Alpha":

            """
            --Simply identifies the intensity at step_stop and step_start and takes difference to find step height
                    --step_start is then shifted so that it starts at step_start.
                    --The step is always centered at the peak position with height 2/3 at L3 peak and 1/3 at L2 peak.
            """
            # calculate difference in step stop and step start intensity
            absorption_difference = (y[step_stop_arr] - y[step_start_arr]) / 3

            # transpose the step to intensity at step start energy.
            l3_transpose = y[step_start_arr]

        yp = yp * absorption_difference * 2
        u = u * absorption_difference

        # find max gradient in steps
        l3_p = np.diff(yp, n=1)
        oo = find_peaks_scipy(l3_p, l3_p)
        l2_p = np.diff(u, n=1)
        oooo = find_peaks_scipy(l2_p, l2_p)
        # create zeros up to L3 step
        pre = zerolistmaker(int(L3_peak_pos - oo[0]) - 1)
        # concatenate
        pre_plus_l3 = np.concatenate([pre, yp])
        # zeros of length than transpose to step.
        mid = zerolistmaker(L2_peak_pos - oooo[0] - len(pre_plus_l3)) + pre_plus_l3[-1]
        # concatenate
        pre_l3_mid = np.concatenate([pre_plus_l3, mid, (u + mid[-1])])
        # post region
        post = zerolistmaker(len(x) - len(pre_l3_mid)) + pre_l3_mid[-1]
        # concatenate
        total = np.concatenate([pre_l3_mid, post])
        total = total + l3_transpose

        post_step = y - total

    return x, post_step, total
