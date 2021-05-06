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

from scipy import integrate
import numpy as np


from percolate.framework import Port
from percolate.framework import InPort
from percolate.framework import OutPort
from percolate.framework import StreamOutput
from percolate.framework import TextOutput
from percolate.framework import StreamInput
from percolate.framework import ArrayOutput
from percolate.framework import FilePathInput
from percolate.framework import DirPathInput
from percolate.framework import MuxInput
from percolate.framework import MuxOutput
from percolate.framework import Param_input
from percolate.framework import func_Output
from percolate.framework import int_input
from percolate.framework import free_int_input
from percolate.framework import bool_input
from percolate.framework import GridInput
from percolate.framework import choice_input
from percolate.framework import Function


# toolKit
from percolate.toolkit.step2 import step2
from percolate.toolkit.fit_peaks_to_data import fit_peaks_to_data


"""class args():   

    def __init__(self, parent):
    
        self.number_of_peaks = parent.number_of_peaks.default
        self.center_of_peaks = parent.center_of_peaks.default
        self.sigma_of_peaks = parent.sigma_of_peaks.default
        self.height_of_peaks = parent.height_of_peaks.default
        self.type_of_peaks = parent.type_of_peaks.default
        
class IdentifyPeaks(Function):
    ''TODO: Centre the step function on the peaks energy!''
    def __init__(self):
    
        super().__init__("Identify Peaks")  
        
        #Input Ports
        self.input_array = StreamInput(self, "input_array")

        self.number_of_peaks = free_int_input(self, "number_of_peaks", 1, 2, 10)
        self.center_of_peaks = int_input(self, "center_of_peaks", self.input_array, 5990)
        self.sigma_of_peaks = int_input(self, "sigma_of_peaks", self.input_array, 30)
        self.height_of_peaks = int_input(self, "height_of_peaks", self.input_array, 0.12)
        self.type_of_peaks = choice_input(self, "GaussianModel", "GaussianModel", ["GaussianModel","LorentzianModel"])

        #output ports
        self.fitted_peaks = ArrayOutput(self, "fitted_peaks", self.read_fitted_peaks)

        

        #publish ports
        self.inputs = [
        
            self.input_array,
            self.number_of_peaks,
            self.center_of_peaks,
            self.sigma_of_peaks,
            self.height_of_peaks,
            self.type_of_peaks,
            
        ]
        
        self.outputs = [
        
            
            self.fitted_peaks,

        ] 

        
    #evaluate method       
    def evaluate(self):
        
        #argument cantains peak information in default values (updated from GUI)
        local_arguments = args(self)
        
        #we set up a list with information to givew to Model. Looks like;
        #    {
        #        'type': 'GaussianModel',
        #        'params': {'center': 652, 'height': 82, 'sigma': 60},
        #    },
        fit = []
        for i in range(self.number_of_peaks.default):
            
            model_type = str(self.type_of_peaks.default)
            
            params = { 
            'center': self.center_of_peaks.default,
            'height': self.height_of_peaks.default,
            'sigma' : self.sigma_of_peaks.default,
            }
            
            model_params = {
            'type' : model_type,
            'params' : params,
            }
            
            
            fit.append(model_params)
        
        print(fit)
        fitting_params= fit
        #perform fit (returns a list of arrays of each peak.)
        self.fitted_energy_scale, self.fitted_peaks = fit_peaks_to_data(energy = self.input_array.read()["data"][0], intensity = self.input_array.read()["data"][1], args = local_arguments, fitting_params = fit)
        #self.fitted_peaks = self.input_array.read()["data"][1]
        #lines representing the peak positions.
        
        print(self.fitted_peaks)
        print(self.fitted_energy_scale)
        print(self.input_array.read()["data"][0])
        self.lines = None
        
    def read_input_array(self):
        return {"data" : [self.input_array.read()["data"][0], self.input_array.read()["data"][1], self.lines] , "label" : self.input_array.read()["label"]}
        #return self.stepfunction_a
        
    def read_fitted_peaks(self):
        return {"data" : [self.fitted_energy_scale, self.fitted_peaks, self.lines] , "label" : self.input_array.read()["label"]}
        #return self.stepfunction_p"""


class args:
    def __init__(self, parent):


        self.center_of_peak = []
        self.sigma_of_peak = []
        self.height_of_peak = []
        self.type_of_peak = []

class IdentifyPeaks(Function):
    """TODO: Centre the step function on the peaks energy!"""

    def __init__(self):

        super().__init__("Identify Peaks")

        # Input Ports
        self.input_array = StreamInput(self, "input_array")

        
        
        self.peak_params = GridInput(self, "peak_params")
        
        # output ports
        self.guide = ArrayOutput(self, "guide", self.read_guide)
        self.fitted_peaks = ArrayOutput(self, "fitted_peaks", self.read_fitted_peaks)
        


    # evaluate method
    def evaluate(self):
    
        self.lines = []
        
        self.args = args(self)
        
        
        for i in self.peak_params.grid:
            if i[0] != None:
                self.lines.append(float(i[0]))
            else:
                pass
            if all(i):
            
                self.args.center_of_peak.append(float(i[0]))
                self.args.type_of_peak.append(str(i[1]))
                self.args.height_of_peak.append(float(i[2]))
                self.args.sigma_of_peak.append(float(i[3]))
                
                

                    
                    
        #self.lines = None
        
        
        #pass
        
        # argument cantains peak information in default values (updated from GUI)
        #local_arguments = args(self)

        # we set up a list with information to givew to Model. Looks like;
        #    {
        #        'type': 'GaussianModel',
        #        'params': {'center': 652, 'height': 82, 'sigma': 60},
        #    },
        fit = []
        for i in range(len(self.args.center_of_peak)):

            model_type = str(self.args.type_of_peak[i])

            params = {
                "center": self.args.center_of_peak[i],
                "height": self.args.height_of_peak[i],
                "sigma": self.args.sigma_of_peak[i],
            }

            model_params = {
                "type": model_type,
                "params": params,
            }

            fit.append(model_params)

        
        fitting_params = fit
        # perform fit (returns a list of arrays of each peak.)
        self.fitted_energy_scale_calc, self.fitted_peaks_calc, self.components, self.comp_energy, self.label = fit_peaks_to_data(
            energy=self.input_array.read()["data"][0],
            intensity=self.input_array.read()["data"][1],
            fitting_params=fit,
        )

        
        # self.fitted_peaks = self.input_array.read()["data"][1]
        # lines representing the peak positions.
        
        #self.lines = None

    def read_guide(self):
        return {
            "data": [
                self.input_array.read()["data"][0],
                self.input_array.read()["data"][1],
                self.lines,
            ],
            "label": self.input_array.read()["label"],
        }
        # return self.stepfunction_a

    '''def read_fitted_peaks(self):
        return {
            "data": [                
                self.input_array.read()["data"][0],
                self.input_array.read()["data"][1], 
                self.lines],
                
            "label": self.input_array.read()["label"],
        }
        # return self.stepfunction_p'''
    def read_fitted_peaks(self):
        return {
            "data": [                
                self.comp_energy,
                self.components,
                None,],
            "label": self.label,
        }








'''class IdentifyPeaks(Function):
    """TODO: Centre the step function on the peaks energy!"""

    def __init__(self):

        super().__init__("Identify Peaks")

        # Input Ports
        self.input_array = StreamInput(self, "input_array")

        self.number_of_peaks = free_int_input(self, "number_of_peaks", 1, 2, 10)

        self.center_of_peaks = int_input(
            self, "center_of_peaks", self.input_array, 5990
        )
        self.sigma_of_peaks = int_input(self, "sigma_of_peaks", self.input_array, 30)
        self.height_of_peaks = int_input(
            self, "height_of_peaks", self.input_array, 0.12
        )
        self.type_of_peaks = choice_input(
            self, "GaussianModel", "GaussianModel", ["GaussianModel", "LorentzianModel"]
        )

        # output ports
        self.fitted_peaks = ArrayOutput(self, "fitted_peaks", self.read_fitted_peaks)



    # evaluate method
    def evaluate(self):

        # argument cantains peak information in default values (updated from GUI)
        local_arguments = args(self)

        # we set up a list with information to givew to Model. Looks like;
        #    {
        #        'type': 'GaussianModel',
        #        'params': {'center': 652, 'height': 82, 'sigma': 60},
        #    },
        fit = []
        for i in range(self.number_of_peaks.default):

            model_type = str(self.type_of_peaks.default)

            params = {
                "center": self.center_of_peaks.default,
                "height": self.height_of_peaks.default,
                "sigma": self.sigma_of_peaks.default,
            }

            model_params = {
                "type": model_type,
                "params": params,
            }

            fit.append(model_params)

        
        fitting_params = fit
        # perform fit (returns a list of arrays of each peak.)
        self.fitted_energy_scale_calc, self.fitted_peaks_calc = fit_peaks_to_data(
            energy=self.input_array.read()["data"][0],
            intensity=self.input_array.read()["data"][1],
            args=local_arguments,
            fitting_params=fit,
        )
        # self.fitted_peaks = self.input_array.read()["data"][1]
        # lines representing the peak positions.

        self.lines = None

    def read_input_array(self):
        return {
            "data": [
                self.input_array.read()["data"][0],
                self.input_array.read()["data"][1],
                self.lines,
            ],
            "label": self.input_array.read()["label"],
        }
        # return self.stepfunction_a

    def read_fitted_peaks(self):
        return {
            "data": [self.fitted_energy_scale_calc, self.fitted_peaks_calc, self.lines],
            "label": self.input_array.read()["label"],
        }
        # return self.stepfunction_p'''
