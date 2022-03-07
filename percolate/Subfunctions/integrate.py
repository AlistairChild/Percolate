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
from percolate.framework import bool_input
from percolate.framework import choice_input
from percolate.framework import Function


# Tools
from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.check_values_in_range import check_values_in_range


class Integrate(Function):
    def __init__(self,parent):

        super().__init__(parent,"integrate")

        # input ports
        self.input = StreamInput(self, "inputarray")

        self.integral = ArrayOutput(self, "integral", self.read_integral)




    def evaluate(self):

        x = self.input.read()["data"][0]
        y = self.input.read()["data"][1]

        if x.ndim and y.ndim == 1:

            intgrl = integrate.cumtrapz(
                y[:],
                x[:],
                initial=0,
            )

        elif x.ndim and y.ndim == 2:

            int_list = []

            for i in range(x.shape[0]):

                integral_calc_ind_i = integrate.cumtrapz(
                    y[i][:],
                    x[i][:],
                    initial=0,
                )

                int_list.append(integral_calc_ind_i)

            intgrl = np.array(int_list)

        self.integral_calc = intgrl
        self.lines = None

    def read_integral(self):
        return {
            "data": [self.input.read()["data"][0], self.integral_calc, self.lines],
            "label": self.input.read()["label"],
        }
        # return self.value
