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
from percolate.framework import choice_input
from percolate.framework import Function
from percolate.framework import Edge
from percolate.framework import CompositeFn

# Applications Functions
class SinGen(Function):
    """
    This create a sin function where the user can alter the frequency and amplitude
    """

    def __init__(self):

        super().__init__("SinGen")

        # ports
        self.frequency = free_int_input(self, "freq", 100, 200, 500)
        self.amplitude = free_int_input(self, "amp", 0, 1, 100)
        self.line1 = free_int_input(self, "line1", 0, 1, 100)
        self.line2 = free_int_input(self, "line2", 0, 1, 100)
        self.sin = ArrayOutput(self, "sin", self.read_sin)

        # declare inputs and outputs
        self.inputs = [
            self.frequency,
            self.amplitude,
            self.line1,
            self.line2,
        ]
        self.outputs = [
            self.sin,
        ]

    def getpath(self, name):

        return_path = str(self) + "/" + str(name)

        return return_path

    def evaluate(self):

        self.time = np.linspace(0, 100, 500)
        self.sin_calc = self.amplitude.default * np.sin(
            2 * np.pi * self.frequency.default / 10 * self.time
        )
        self.lines = [self.line1.default, self.line2.default]

    def read_sin(self):
        return {"data": [self.time, self.sin_calc, self.lines], "label": "s"}


function = SinGen()
