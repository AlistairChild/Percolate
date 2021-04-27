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
from percolate.toolkit.Normalise_spectra import Normalise_spectra


class args_normalise:
    def __init__(self, parent):

        self.action = parent.action.default
        self.normalise_point_1 = parent.normalise_point_1.default
        self.normalise_point_2 = parent.normalise_point_2.default


class Normalise(Function):
    def __init__(self):

        super().__init__("Normalise")

        # streamed inputs

        self.t_p_all = StreamInput(self, "t_p_all")
        self.t_a_all = StreamInput(self, "t_a_all")

        # parameter inputs
        self.action = choice_input(
            self, "Action", "Do not Apply", ["Do not Apply", "Apply"]
        )
        self.normalise_point_1 = int_input(
            self, "normalise_point_1", self.t_p_all, None
        )
        self.normalise_point_2 = int_input(
            self, "normalise_point_2", self.t_p_all, None
        )

        # output ports
        self.a_p_norm = ArrayOutput(self, "a_p_norm", self.read_a_p_norm)
        self.a_a_norm = ArrayOutput(self, "a_a_norm", self.read_a_a_norm)

        self.inputs = [
            self.t_p_all,
            self.t_a_all,
            self.action,
            self.normalise_point_1,
            self.normalise_point_2,
        ]

        self.outputs = [
            self.a_p_norm,
            self.a_a_norm,
            # self.e_out,
        ]

    def getpath(self, name):

        return_path = str(self) + "/" + name

        # return_path = self.parent.getpath(self, str(self.__class__.__name__) + "/" + str(name))
        return return_path

    def evaluate(self):

        local_arguments = args_normalise(self)

        x1 = self.t_p_all.read()["data"][0]
        y1 = self.t_p_all.read()["data"][1]

        x2 = self.t_a_all.read()["data"][0]
        y2 = self.t_a_all.read()["data"][1]

        self.x1, self.a_p_normalised1 = self.invoke_normalise_function(
            x1, y1, local_arguments
        )
        self.x2, self.a_p_normalised2 = self.invoke_normalise_function(
            x2, y2, local_arguments
        )

        self.lines = [self.normalise_point_1.default, self.normalise_point_2.default]

    def read_a_p_norm(self):
        return {
            "data": [self.x1, self.a_p_normalised1, self.lines],
            "label": self.t_p_all.read()["label"],
        }
        # return self.ia_p_norm

    def read_a_a_norm(self):
        return {
            "data": [self.x2, self.a_p_normalised2, self.lines],
            "label": self.t_p_all.read()["label"],
        }
        # return self.ia_a_norm

    def invoke_normalise_function(self, x, y, arguments):

        p1 = arguments.normalise_point_1
        p2 = arguments.normalise_point_2

        if arguments.action == "Do not Apply":
            x = x
            y = y

        elif arguments.action == "Apply":

            if np.array(x).ndim and np.array(y).ndim == 1:

                x, y = Normalise_spectra(x, y, p1, p2)

            elif np.array(x).ndim and np.array(y).ndim == 2:

                x_list = []
                y_list = []

                for i in range(x.shape[0]):

                    xi, yi = Normalise_spectra(x[i], y[i], p1, p2)

                    x_list.append(xi)
                    y_list.append(yi)

                x = np.array(x_list)
                y = np.array(y_list)

        return x, y
