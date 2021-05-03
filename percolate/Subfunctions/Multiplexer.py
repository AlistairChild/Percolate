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


class Multiplexer(Function):

    # TODO: support arrays of different length!
    def __init__(self, n_inputs):

        super().__init__("Multiplexer")

        self.n_inputs = n_inputs

        self.inputs = []

        for item in range(n_inputs):

            input = StreamInput(self, "in" + str(item))
            self.inputs.append(input)
            # input.changed += self.on_data

        self.multiplot = ArrayOutput(self, "out", self.read_output)


        self.a = None

    def evaluate(self):

        a = []
        e = []
        labels = []
        count = 0
        for input in self.inputs:
            count = count + 1
            if count <= self.n_inputs:

                if len(np.array(input.read()["data"][1]).shape) > 1:
                    n_files = len(np.array(input.read()["data"][1]))
                else:
                    n_files = 1

                for i in range(n_files):

                    labels.append(np.array(input.read()["label"][1][i]))
                    a.append(np.array(input.read()["data"][1][i]))
                    e.append(np.array(input.read()["data"][0][i]))

        self.e = np.array(e)
        self.a = np.array(a)
        self.labels = np.array(labels)
        self.lines = None

    def read_output(self):
        return {"data": [self.e, self.a, self.lines], "label": self.labels}
        # return self.a
