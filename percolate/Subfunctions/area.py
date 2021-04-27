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


class Area(Function):
    def __init__(self):

        super().__init__("area")

        # input ports
        self.input = StreamInput(self, "inputarray")

        # int_input takes arguments (fn, name, input_stream)
        # The input_stream allows for limits to be calculated for GUI sliders.

        self.start = int_input(self, "start", self.input, 770)
        self.mid = int_input(self, "mid", self.input, 790)
        self.end = int_input(self, "end", self.input, 800)
        #

        self.value = TextOutput(self, "value", self.read_value)
        self.graph = ArrayOutput(self, "graph", self.read_graph)

        # declare
        self.inputs = [
            self.input,
            self.start,
            self.mid,
            self.end,
        ]

        self.outputs = [
            self.graph,
            self.value,
        ]

    def getpath(self, name):

        return_path = str(self) + "/" + name

        return return_path

    def evaluate(self):

        x = np.array(self.input.read()["data"][0])
        y = np.array(self.input.read()["data"][1])

        if x.ndim and y.ndim == 1:

            start = find_array_equivalent(x, self.start.default)
            mid = find_array_equivalent(x, self.mid.default)
            end = find_array_equivalent(x, self.end.default)

            a_l3 = integrate.cumtrapz(
                y[start:mid],
                x[start:mid],
                initial=0,
            )
            a_l2 = integrate.cumtrapz(
                y[mid:end],
                x[mid:end],
                initial=0,
            )

            b_ratio = [a_l3[-1] / (a_l2[-1] + a_l3[-1])]

        elif x.ndim and y.ndim == 2:

            bratio_list = []

            for i in range(x.shape[0]):

                start = find_array_equivalent(x[i], self.start.default)
                mid = find_array_equivalent(x[i], self.mid.default)
                end = find_array_equivalent(x[i], self.end.default)

                a_l3 = integrate.cumtrapz(
                    y[i][start:mid],
                    x[i][start:mid],
                    initial=0,
                )
                a_l2 = integrate.cumtrapz(
                    y[i][mid:end],
                    x[i][mid:end],
                    initial=0,
                )

                b_ratio = a_l3[-1] / (a_l2[-1] + a_l3[-1])

                bratio_list.append(b_ratio)

            b_ratio = list(bratio_list)

        self.value_calc = b_ratio

        self.lines = [self.start.default, self.mid.default, self.end.default]

    def read_value(self):
        return {
            "data": [self.input.read()["data"][0], self.value_calc],
            "label": self.input.read()["label"],
        }
        # return self.value

    def read_graph(self):
        return {
            "data": [
                self.input.read()["data"][0],
                self.input.read()["data"][1],
                self.lines,
            ],
            "label": self.input.read()["label"],
        }
        # return self.value
