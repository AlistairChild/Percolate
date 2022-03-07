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
from percolate.framework import num_input

# Toolkit imports
from percolate.toolkit.find_array_equivalent import find_array_equivalent


class SumRules(Function):
    def __init__(self, parent):

        super().__init__(parent, "SumRules")

        self.p = StreamInput(self, "p")
        self.q = StreamInput(self, "q")
        self.r = StreamInput(self, "r")

        self.shell_occupation = num_input(self, "shell_occupation", self.p, 7.51)

        self.ratio = TextOutput(self, "2q / (9p - 6p)", self.read_ratio)
        self.orbitalmoment = TextOutput(
            self,
            "orbital moment  -((4 * q) * (10 - n3d)) / (3 * r) ",
            self.read_orbitalmoment,
        )
        self.spinmoment = TextOutput(
            self, "spin moment -((6 * p - 4 * q) * (10 - n3d)) / r", self.read_spinmoment
        )

        

    def evaluate(self):

        n3d = self.shell_occupation.default

        valuep = self.p.read()["data"][1]
        valueq = self.q.read()["data"][1]
        valuer = self.r.read()["data"][1]

        if valuep and valuep and valuep != None:

            if len(valuep) == 1:

                p = float(valuep[0])
                q = float(valueq[0])
                r = float(valuer[0])

                # sum rules
                ratio = [2 * q / ((9 * p) - (6 * q))]
                orbital = [-((4 * q) * (10 - n3d)) / (3 * r)]
                spin = [-((6 * p - 4 * q) * (10 - n3d)) / r]

            else:

                ratio = []
                spin = []
                orbital = []

                for i in range(np.array(valuep).shape[0]):
                    # local variables
                    p = float(valuep[i])
                    q = float(valueq[i])
                    r = float(valuer[i])

                    # sum rules
                    ratio_i = 2 * q / ((9 * p) - (6 * q))
                    orbital_i = -((4 * q) * (10 - n3d)) / (3 * r)
                    spin_i = -((6 * p - 4 * q) * (10 - n3d)) / r

                    # append
                    ratio.append(ratio_i)
                    orbital.append(orbital_i)
                    spin.append(spin_i)
        else:
            ratio = None
            spin = None
            orbital = None

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
