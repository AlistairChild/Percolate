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


# imports
import numpy as np

# framework imports
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
from percolate.framework import num_input
from percolate.framework import bool_input
from percolate.framework import choice_input
from percolate.framework import Function


# Tools
from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.check_values_in_range import check_values_in_range


class args_scale:
    def __init__(self, parent):

        self.Reverse = parent.Reverse.default


class scale(Function):
    """takes the subtracts on spectra from another"""

    def __init__(self):

        super().__init__("Scale")

        # inputs
        self.input = StreamInput(self, "input")

        # params
        self.scale_value = num_input(self, "scale_value", self.input, 1)

        # outputs
        self.scaled = ArrayOutput(self, "scaled", self.read_scaled)


    def evaluate(self):

        a = np.array(self.input.read()["data"][1])

        if a.ndim == 1:

            ab = a * self.scale_value.default

        elif a.ndim == 2:

            scale_list = []

            for i in range(a.shape[0]):

                scale_i = a[i] * self.scale_value.default

                scale_list.append(scale_i)

            ab = np.array(scale_list)

        self.scaled_calc = np.array(ab)
        self.lines = None

    def read_scaled(self):
        return {
            "data": [self.input.read()["data"][0], self.scaled_calc, self.lines],
            "label": self.input.read()["label"],
        }
