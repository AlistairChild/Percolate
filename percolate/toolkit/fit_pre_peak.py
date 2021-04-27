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
import os
import math
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize, signal

from lmfit import models


import numpy as np
import lmfit
from lmfit import Model
from lmfit import models
from lmfit import minimize, Parameters

from scipy import optimize, signal


def gaussian_cdf(x, amp, mu, sigma):
    return (
        amp
        * (1 / (sigma * (np.sqrt(2 * np.pi))))
        * (np.exp((-1.0 / 2.0) * (((x - mu) / sigma) ** 2)))
    )


def lorentzian_cdf(x, amp, mu, sigma):
    return amp * sigma ** 2 / (sigma ** 2 + (x - mu) ** 2)


fitted = []


def fit_pre_peak(energy, intensity, args):

    # number of peaks
    # n_peaks = args.number_of_peaks

    # energy of peaks
    # e_peaks = args.energy_of_peaks

    # width of peaks
    # w_peaks = args.width_of_peaks

    # intensity of peaks
    # i_peaks = args.intensity_of_peaks

    # name of peaks
    # id_peaks = args.name_of_peaks

    ##models = []
    # = []

    # for item in range(n_peaks):

    # model = Model(lorentzian_cdf, prefix = str(item))
    # params = model.make_params(amp =293, mu=130, sigma=10)

    # models.append(model)
    # params.append(params)

    # print(models)

    # result = model.fit(intensity, params, x = energy)

    # fitted.append(intensity)

    def update_spec_from_peaks(spec, model_indicies, peak_widths=(10, 25), **kwargs):
        x = spec["x"]
        y = spec["y"]
        x_range = np.max(x) - np.min(x)
        peak_indicies = signal.find_peaks_cwt(y, peak_widths)
        np.random.shuffle(peak_indicies)
        for peak_indicie, model_indicie in zip(peak_indicies.tolist(), model_indicies):
            model = spec["model"][model_indicie]
            if model["type"] in ["GaussianModel", "LorentzianModel", "VoigtModel"]:
                params = {
                    "height": y[peak_indicie],
                    "sigma": x_range / len(x) * np.min(peak_widths),
                    "center": x[peak_indicie],
                }
                if "params" in model:
                    model.update(params)
                else:
                    model["params"] = params
            else:
                raise NotImplemented(f'model {basis_func["type"]} not implemented yet')
        return peak_indicies

    """spec = {
        'x': energy,
        'y': intensity,
        'model': [
            {'type': 'VoigtModel'},
            {'type': 'VoigtModel'},
            {'type': 'VoigtModel'},
            {'type': 'VoigtModel'},
            {'type': 'VoigtModel'},
            {'type': 'GaussianModel'},
            {'type': 'GaussianModel'},
            {'type': 'GaussianModel'},
            {'type': 'GaussianModel'},
            {'type': 'GaussianModel'},
            {'type': 'GaussianModel'},
            {'type': 'GaussianModel'},
        ]
    }"""

    # peaks_found = update_spec_from_peaks(spec, [0, 1, 2, 3, 4, 5, 6], peak_widths=(15,))

    def generate_model(spec):
        composite_model = None
        params = None
        x = spec["x"]
        y = spec["y"]
        x_min = np.min(x)
        x_max = np.max(x)

        x_range = x_max - x_min

        y_max = np.max(y)
        print(y_max)
        for i, basis_func in enumerate(spec["model"]):
            prefix = f"m{i}_"
            model = getattr(models, basis_func["type"])(prefix=prefix)
            if basis_func["type"] in [
                "GaussianModel",
                "LorentzianModel",
                "VoigtModel",
            ]:  # for now VoigtModel has gamma constrained to sigma
                model.set_param_hint("sigma", min=1e-6, max=x_range)
                model.set_param_hint("center", min=x_min, max=x_max)
                model.set_param_hint("height", min=1e-6, max=1.1 * y_max)
                model.set_param_hint("amplitude", min=1e-6)
                # default guess is horrible!! do not use guess()
                default_params = {
                    prefix + "center": x_min + x_range * random.random(),
                    prefix + "height": y_max * random.random(),
                    prefix + "sigma": x_range * random.random(),
                }
            else:
                raise NotImplemented(f'model {basis_func["type"]} not implemented yet')
            if "help" in basis_func:  # allow override of settings in parameter
                for param, options in basis_func["help"].items():
                    model.set_param_hint(param, **options)
            model_params = model.make_params(
                **default_params, **basis_func.get("params", {})
            )
            if params is None:
                params = model_params

            else:
                params.update(model_params)

            if composite_model is None:
                composite_model = model

            else:
                composite_model = composite_model + model

        return composite_model, params

    # TODO: make spec dynamical to account for fitting n peaks!
    spec = {
        "x": energy,
        "y": intensity,
        "model": [
            {
                "type": "GaussianModel",
                "params": {"center": 652, "height": 82, "sigma": 60},
                "help": {"center": {"min": 630, "max": 670}},
            },
            {
                "type": "VoigtModel",
                "params": {"center": 586, "height": 80, "sigma": 60, "gamma": 60},
                "help": {"center": {"min": 570, "max": 590}},
            },
            {
                "type": "VoigtModel",
                "params": {"center": 438, "height": 40, "sigma": 30},
            },
            {
                "type": "VoigtModel",
                "params": {"center": 385, "height": 30, "sigma": 30},
            },
            {
                "type": "GaussianModel",
                "params": {"center": 297, "height": 20, "sigma": 40},
            },
            {
                "type": "GaussianModel",
                "params": {"center": 263, "height": 30, "sigma": 40},
                "help": {"center": {"min": 258, "max": 265}},
            },
            {
                "type": "GaussianModel",
                "params": {"center": 218, "height": 10, "sigma": 60},
            },
            {
                "type": "VoigtModel",
                "params": {"center": 173, "height": 10, "sigma": 10, "gamma": 15},
            },
            {
                "type": "VoigtModel",
                "params": {"center": 125, "height": 20, "sigma": 15, "gamma": 15},
            },
            {
                "type": "VoigtModel",
                "params": {"center": 155, "height": 30, "sigma": 20, "gamma": 20},
            },
            # {'type': 'GaussianModel', 'help': {'center': {'max': 153}}},
            # {'type': 'GaussianModel'},
            # {'type': 'GaussianModel'}
        ],
    }

    model, params = generate_model(spec)
    output = model.fit(spec["y"], params, x=spec["x"])

    return output.best_fit
