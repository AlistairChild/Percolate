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


def fit_peaks_to_data(energy, intensity, args, fitting_params):

    # number of peaks
    n_peaks = args.number_of_peaks

    # energy of peaks
    e_peaks = args.center_of_peaks

    # width of peaks
    w_peaks = args.sigma_of_peaks

    # intensity of peaks
    i_peaks = args.height_of_peaks

    # name of peaks
    id_peaks = args.type_of_peaks

    # create spec with fitting_params dynamical
    spec = {"x": energy, "y": intensity, "model": fitting_params}

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

    def generate_model(spec):
        composite_model = None
        params = None
        x = spec["x"]
        y = spec["y"]
        x_min = np.min(x)
        x_max = np.max(x)

        x_range = x_max - x_min

        y_max = np.max(y)

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

    model, params = generate_model(spec)
    output = model.fit(spec["y"], params, x=spec["x"])

    # evaluate components of output
    comps = output.eval_components()

    components = []
    components_energy = []

    for i in comps:
        # print(i)

        components.append(list(comps[f"{i}"]))
        components_energy.append(energy)

    return energy, output.best_fit
    # return components_energy, components


"""


    #model = Model(lorentzian_cdf, prefix='g2_') + Model(lorentzian_cdf, prefix='g3_')+ Model(lorentzian_cdf, prefix='g4_')+ Model(lorentzian_cdf, prefix='g5_')+ Model(lorentzian_cdf, prefix='g7_')#+ Model(lorentzian_cdf, prefix='g7_')#+ Model(lorentzian_cdf, prefix='g8_')+ Model(lorentzian_cdf, prefix='g9_')+ Model(lorentzian_cdf, prefix='g10_')+ Model(lorentzian_cdf, prefix='g11_')

    # make a parameters object -- a dict with parameter names
    # taken from the arguments of your model function and prefix
    
    
    
	params = model.make_params(#g1_amp=293, g1_mu=138, g1_sigma=10,
                           g2_amp=0.6, g2_mu=307, g2_sigma=30,
						  # g10_amp=20, g10_mu=348, g10_sigma=2,
						   g3_amp=0.65, g3_mu=344, g3_sigma=30,
						   g4_amp=1, g4_mu=381, g4_sigma=20,
						   g5_amp=0.22, g5_mu=508, g5_sigma=30,
						   #g6_amp=80, g6_mu=560, g6_sigma=20,
						   g7_amp=0.15, g7_mu=675, g7_sigma=60.)
						  # g7_amp=1140, g7_mu=344, g7_sigma=1.)
						   #g8_amp=23, g8_mu=158, g8_sigma=2,
						   #g10_amp=10, g10_mu=97, g10_sigma=2,
						   #g11_amp=20, g11_mu=507, g11_sigma=2,
						   #g9_amp=26, g9_mu=129, g9_sigma=2.)
                           #g7_amp=0.01, g7_mu=440, g7_sigma=200.)

# you can apply bounds to any parameter
#params['g1_sigma'].min = 0   # sigma must be > 0!

# you may want to fix the amplitudes to 0.5:
#params['g1_amp'].vary = False
#params['g2_amp'].vary = False

# run the fit
	result = model.fit(y_new, params, x=x_new)

# print results
	print(result.fit_report())

# plot results, including individual components
	comps = result.eval_components(result.params, x=x_new)
	added_curves=comps['g2_']+comps['g3_']+comps['g4_']+comps['g5_']+comps['g7_']#+comps['g7_']
    
    """
