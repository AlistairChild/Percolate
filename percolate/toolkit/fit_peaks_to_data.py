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
from percolate.toolkit.make_zero_array import make_zero_array


def gaussian_cdf(x, amp, mu, sigma):
    return (
        amp
        * (1 / (sigma * (np.sqrt(2 * np.pi))))
        * (np.exp((-1.0 / 2.0) * (((x - mu) / sigma) ** 2)))
    )


def lorentzian_cdf(x, amp, mu, sigma):
    return amp * sigma ** 2 / (sigma ** 2 + (x - mu) ** 2)


fitted = []


def fit_peaks_to_data(energy, intensity, fitting_params):
    if fitting_params:
        # number of peaks
        '''n_peaks = args.number_of_peaks
    
        # energy of peaks
        e_peaks = args.center_of_peaks
    
        # width of peaks
        w_peaks = args.sigma_of_peaks
    
        # intensity of peaks
        i_peaks = args.height_of_peaks
    
        # name of peaks
        id_peaks = args.type_of_peaks'''
    
        # create spec with fitting_params dynamical
        spec = {"x": energy, "y": intensity, "model": fitting_params}
        
    
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
    
            return composite_model, params, model
    
        composite_model, params, model  = generate_model(spec)
        output = composite_model.fit(spec["y"], params, x=spec["x"])
    
        # evaluate components of output
        comps = output.eval_components()
    
        components = []
        components_energy = []
        name =[]
    
        for i in comps:
            # print(i)
            
            
            components.append(comps[f"{i}"])
            components_energy.append(energy)
            name.append(str(i))

        #print()
        name.append("envolope")
        components.append(output.best_fit)
        components_energy.append(energy)
        
        
        components = np.array(components)
        components_energy = np.array(components_energy)

        
        return energy, output.best_fit, components, components_energy, name
        # return components_energy, components
    else:
        return energy, make_zero_array(intensity), make_zero_array(intensity), energy, ["fit"]
