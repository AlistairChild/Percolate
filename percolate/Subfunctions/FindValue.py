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

from percolate.toolkit.find_array_equivalent import find_array_equivalent


class FindValue(Function):
    def __init__(self, name):

        super().__init__(name)

        # input ports
        self.inputarray = StreamInput(self, "inputarray")
        self.lookup = int_input(self, "lookup", self.inputarray, None)

        # output ports
        self.value = TextOutput(self, "value", self.read_value)
        self.graph = ArrayOutput(self, "graph", self.read_graph)
        # declare
        self.inputs = [
            self.inputarray,
            self.lookup,
        ]

        self.outputs = [
            self.value,
            self.graph,
        ]

    def getpath(self, name):

        return_path = str(self) + "/" + name

        return return_path

    def evaluate(self):

        if len(np.array(self.inputarray.read()["data"][1]).shape) > 1:
            n_files = len(np.array(self.inputarray.read()["data"][1]))
        else:
            n_files = 1

        value = []

        for i in range(n_files):
            try:
                value_i = self.inputarray.read()["data"][1][i][
                    find_array_equivalent(
                        self.inputarray.read()["data"][0][i], self.lookup.default
                    )
                ]
                value.append(value_i)
            except:
                value = None

        self.value = value
        self.lines = [self.lookup.default]

    def read_value(self):
        return {
            "data": [self.inputarray.read()["data"][0], self.value],
            "label": self.inputarray.read()["label"],
        }
        # return self.value

    def read_graph(self):
        return {
            "data": [
                self.inputarray.read()["data"][0],
                self.inputarray.read()["data"][1],
                self.lines,
            ],
            "label": self.inputarray.read()["label"],
        }