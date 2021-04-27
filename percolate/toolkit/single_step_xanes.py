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


# math
import numpy as np
import array
import scipy
from scipy import asarray as ar, exp
import math
from lmfit import CompositeModel, Model
from lmfit.lineshapes import gaussian, step

# toolkit imports
from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.zerolistmaker import zerolistmaker
from percolate.toolkit.make_zero_array import make_zero_array
from numpy import exp, loadtxt, pi, sqrt


def gaussian_func(x, a, x0, sigma, c):
    return a * np.exp(-((x - x0) ** 2) / (2 * sigma ** 2)) + c


def pre_edge_fit(
    x: np.ndarray,
    y: np.ndarray,
    pre_feature_min: float,
    pre_feature_max: float,
    post_feature_min: float,
    post_feature_max: float,
):

    if (
        x.all()
        and y.all()
        and pre_feature_min
        and pre_feature_max
        and post_feature_min
        and post_feature_max
    ):

        return calculate_pre_edge_fit(
            x, y, pre_feature_min, pre_feature_max, post_feature_min, post_feature_max
        )

    else:
        return x, y, make_zero_array(x)


def calculate_pre_edge_fit(
    x, y, pre_feature_min, pre_feature_max, post_feature_min, post_feature_max
):

    if x.ndim == 1:
        # find array point
        pre_feature_min_arr = int(find_array_equivalent(x, pre_feature_min))
        pre_feature_max_arr = int(find_array_equivalent(x, pre_feature_max))
        post_feature_min_arr = int(find_array_equivalent(x, post_feature_min))
        post_feature_max_arr = int(find_array_equivalent(x, post_feature_max))

        # concatenate data for fitting
        # fit_resolution = len(energy[:edge])
        x_cut = np.concatenate(
            (
                x[pre_feature_min_arr:pre_feature_max_arr],
                x[post_feature_min_arr:post_feature_max_arr],
            )
        )
        y_cut = np.concatenate(
            (
                y[pre_feature_min_arr:pre_feature_max_arr],
                y[post_feature_min_arr:post_feature_max_arr],
            )
        )

        # cut data to edge
        y_out = y[pre_feature_min_arr:post_feature_max_arr]
        x_out = x[pre_feature_min_arr:post_feature_max_arr]

        initial_guess = [1.4, 6003, 2, 1]
        popt, pcov = scipy.optimize.curve_fit(
            gaussian_func, x_cut, y_cut, p0=initial_guess
        )

        # append guassian model to fit
        fit = []
        for item in range(len(x_out)):
            fit.append(gaussian_func(x_out, *popt)[item])

        fit = np.array(fit)
        y_out = y_out - fit

        return x_out, y_out, fit

    elif x.ndim == 2:
        print("2d")


def single_step_xanes(energy: np.ndarray, absorption: np.ndarray, args):

    if energy.ndim == 1:
        # find array point
        step_stop_energy = find_array_equivalent(energy, args.step_stop)
        step_start_energy = find_array_equivalent(energy, args.step_start)
        edge = find_array_equivalent(energy, args.edge)

        # concatenate data for fitting
        fit_resolution = len(energy[:edge])
        x = np.concatenate(
            [
                energy[:step_start_energy],
                energy[step_stop_energy:edge],
            ]
        )
        y = np.concatenate(
            [
                energy[:step_start_energy],
                energy[step_stop_energy:edge],
            ]
        )

        # cut data to edge
        output_ydata = absorption[:edge]
        x_all = energy[:edge]

        initial_guess = [1.4, 6003, 2, 6000]
        popt, pcov = scipy.optimize.curve_fit(gaussian_func, x, y, p0=initial_guess)

        output_xdata = x_all

        # append guassian model to fit
        fit = []
        for item in range(len(output_xdata)):
            fit.append(gaussian_func(output_xdata, *popt)[item])

    elif energy.ndim == 2:
        print("2d")

    if len(np.array(loc_absorption).shape) > 1:
        n_files = len(np.array(loc_absorption))
    else:
        n_files = 1

    fit_calc = []
    subtracted_fit_calc = []
    xdata_calc = []

    for i in range(n_files):

        if args.step_stop and args.step_start and args.edge:

            if args.apply_step == "on":

                # find array point
                step_stop_energy = find_array_equivalent(loc_energy[i], args.step_stop)
                step_start_energy = find_array_equivalent(
                    loc_energy[i], args.step_start
                )
                edge = find_array_equivalent(loc_energy[i], args.edge)

                # concatenate data for fitting
                fit_resolution = len(loc_energy[i][:edge])
                x = np.concatenate(
                    [
                        loc_energy[i][:step_start_energy],
                        loc_energy[i][step_stop_energy:edge],
                    ]
                )
                y = np.concatenate(
                    [
                        loc_absorption[i][:step_start_energy],
                        loc_absorption[i][step_stop_energy:edge],
                    ]
                )

                # cut data to edge
                output_ydata = loc_absorption[i][:edge]
                x_all = loc_energy[i][:edge]

                initial_guess = [1.4, 6003, 2, 6000]
                popt, pcov = scipy.optimize.curve_fit(
                    gaussian_func, x, y, p0=initial_guess
                )

                output_xdata = x_all

                # append guassian model to fit
                fit = []
                for item in range(len(output_xdata)):
                    fit.append(gaussian_func(output_xdata, *popt)[item])

            elif args.apply_step == "off":

                # subtracted_step = loc_absorption[i]
                # stepfunction = np.zeros(len(loc_energy[i]))
                output_xdata = loc_energy[i]
                output_ydata = loc_absorption[i]
                fit = np.zeros(len(loc_energy[i]))

        else:
            output_xdata = loc_energy[i]
            output_ydata = loc_absorption[i]
            fit = np.zeros(len(loc_energy[i]))

        subtracted_fit = output_ydata - fit

        fit_calc.append(fit)
        subtracted_fit_calc.append(subtracted_fit)
        xdata_calc.append(output_xdata)

    return xdata_calc, fit_calc, subtracted_fit_calc
