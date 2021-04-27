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

# generic imports
from scipy import integrate
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
from percolate.framework import bool_input
from percolate.framework import choice_input
from percolate.framework import Function

# Toolkit imports
from percolate.toolkit.find_array_equivalent import find_array_equivalent


class SumRules(Function):
    def __init__(self):

        super().__init__("SumRules")

        self.p = StreamInput(self, "p")
        self.q = StreamInput(self, "q")
        self.r = StreamInput(self, "r")

        self.ratio = TextOutput(self, "ratio", self.read_ratio)
        self.orbitalmoment = TextOutput(self, "orbital moment", self.read_orbitalmoment)
        self.spinmoment = TextOutput(self, "spin moment", self.read_spinmoment)

        self.inputs = [
            self.p,
            self.q,
            self.q,
        ]

        self.outputs = [
            self.ratio,
            self.orbitalmoment,
            self.spinmoment,
        ]

    def evaluate(self):

        n3d = 7.51

        if len(self.p.read()["data"][1]) > 1:
            n_files = len(self.p.read()["data"][1])
        else:
            n_files = 1

        ratio = []
        spin = []
        orbital = []

        for i in range(n_files):
            # local variables
            p = float(self.p.read()["data"][1][i])
            q = float(self.q.read()["data"][1][i])
            r = float(self.r.read()["data"][1][i])

            # sum rules
            ratio_i = 2 * q / ((9 * p) - (6 * q))
            orbital_i = -((4 * q) * (10 - n3d)) / (3 * r)
            spin_i = -((6 * p - 4 * q) * (10 - n3d)) / r

            # append
            ratio.append(ratio_i)
            orbital.append(orbital_i)
            spin.append(spin_i)

        self.ratio = ratio
        self.spin = spin
        self.orbital = orbital
        self.lines = None

    def read_ratio(self):
        return {
            "data": [self.p.read()["data"][0], self.ratio, self.lines],
            "label": self.p.read()["label"],
        }
        # return self.ratio

    def read_orbitalmoment(self):
        return {
            "data": [self.p.read()["data"][0], self.orbital, self.lines],
            "label": self.p.read()["label"],
        }
        # return self.orbital

    def read_spinmoment(self):
        return {
            "data": [self.p.read()["data"][0], self.spin, self.lines],
            "label": self.p.read()["label"],
        }
        # return self.spin
