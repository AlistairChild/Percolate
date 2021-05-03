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
from percolate.toolkit.Transpose_spectra import Transpose_spectra


class args_transpose:
    def __init__(self, parent):

        self.action = parent.action.default
        self.x_value_for_transpose = parent.x_value_for_transpose.default


class Transpose(Function):
    def __init__(self):

        super().__init__("Transpose")

        # streamed inputs

        self.spectra = StreamInput(self, "spectra")

        # parameter inputs
        self.action = choice_input(self, "Action", "on", ["off", "on"])
        self.x_value_for_transpose = int_input(
            self, "x_value_for_transpose", self.spectra, 771
        )

        # output ports
        self.transposed_data = ArrayOutput(
            self, "transposed_data", self.read_transposed_data
        )




    def evaluate(self):

        local_arguments = args_transpose(self)

        self.transposed = Transpose_spectra(
            energy=self.spectra.read()["data"][0],
            absorption=self.spectra.read()["data"][1],
            args=local_arguments,
        )

        self.lines = [self.x_value_for_transpose.default]

    def read_transposed_data(self):
        return {
            "data": [self.spectra.read()["data"][0], self.transposed, self.lines],
            "label": self.spectra.read()["label"],
        }
        # return self.xmcd_integral
