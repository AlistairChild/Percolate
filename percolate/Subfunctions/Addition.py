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
from percolate.framework import choice_input
from percolate.framework import Function

# Toolkit import
from percolate.toolkit.check_values_in_range import check_values_in_range
from percolate.toolkit.background_xmcd import background_xmcd


class addition(Function):
    """Adds two nd arrays together"""

    def __init__(self,parent):

        super().__init__(parent,"Addition")

        # inputs
        self.A = StreamInput(self, "A")
        self.B = StreamInput(self, "B")

        # outputs
        self.added = ArrayOutput(self, "added", self.read_added)


    def evaluate(self):

        a = np.array(self.A.read()["data"][1])
        b = np.array(self.B.read()["data"][1])

        if a.ndim and b.ndim == 1:

            add = a + b

        elif a.ndim and b.ndim == 2:

            add_list = []

            for i in range(a.shape[0]):

                add_i = a[i] + b[i]

                add_list.append(add_i)

            add = np.array(add_list)

        self.add_calc = np.array(add)
        self.lines = None

    def read_added(self):
        return {
            "data": [self.A.read()["data"][0], self.add_calc, self.lines],
            "label": self.A.read()["label"],
        }
        # return self.diff
