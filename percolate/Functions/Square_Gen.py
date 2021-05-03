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
from scipy import signal
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
class SquareGen(Function):
    """
    This create a sin function where the user can alter the frequency and amplitude
    """

    def __init__(self):

        super().__init__("SquareGen")

        # ports
        self.frequency = free_int_input(self, "freq", 1, 3, 5)
        self.amplitude = free_int_input(self, "amp", 0, 20, 100)
        self.square = ArrayOutput(self, "square", self.read_square)


    def getpath(self, name):

        return_path = str(self) + "/" + str(name)

        return return_path

    def evaluate(self):

        self.time = np.linspace(0, 1, 500)
        self.square_calc = self.amplitude.default * signal.square(
            2 * np.pi * self.frequency.default * self.time
        )

    def read_square(self):
        return {"data": [self.time, self.square_calc, None], "label": "s"}


function = SquareGen()
