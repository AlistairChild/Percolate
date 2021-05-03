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
from percolate.toolkit.background_xmcd import background_xmcd
from percolate.toolkit.zerolistmaker import zerolistmaker


class args_xas:
    def __init__(self, parent):

        self.fit = parent.fit.default
        self.background_start = parent.background_start.default
        self.background_stop = parent.background_stop.default


class Xas(Function):
    def __init__(self):

        super().__init__("XAS spectra")

        # inputs

        self.a_p_norm = StreamInput(self, "a_p_norm")
        self.a_a_norm = StreamInput(self, "a_a_norm")
        # parameter inputs
        self.fit = choice_input(
            self,
            "fit",
            "Do Nothing!!",
            ["linear", "polynomial", "exp decay", "2 point linear", "Do Nothing!!"],
        )
        self.background_start = int_input(self, "p_start_xas", self.a_p_norm, 770)
        self.background_stop = int_input(self, "p_stop_xas", self.a_p_norm, 805)
        # outputs
        self.xas = ArrayOutput(self, "xas", self.read_xas)
        self.xas_bg = ArrayOutput(self, "xas_bg", self.read_xas_bg)
        self.xas_integral = ArrayOutput(self, "xas_integral", self.read_xas_integral)



    def getpath(self, name):

        return_path = str(self) + "/" + name

        return return_path

    def evaluate(self):

        local_arguments = args_xas(self)

        ax = np.array(self.a_p_norm.read()["data"][0])
        bx = np.array(self.a_a_norm.read()["data"][0])

        ay = np.array(self.a_p_norm.read()["data"][1])
        by = np.array(self.a_a_norm.read()["data"][1])

        if ax.ndim and bx.ndim == 1:

            add = by + ay

            integral_start = find_array_equivalent(ax, local_arguments.background_start)
            integral_end = find_array_equivalent(ax, local_arguments.background_stop)

            xas_bg_i, xas_i = background_xmcd(
                energy=np.array(ax),
                xmcd=add,
                args=local_arguments,
            )

            xas_integral_i = integrate.cumtrapz(
                xas_i[integral_start:integral_end],
                ax[integral_start:integral_end],
            )
            # self.xas_integral = np.append(xas_integral[0], xas_integral[0][-1])
            xas_integral1 = np.concatenate(
                [
                    zerolistmaker(len(ax[0:integral_start] + 1)),
                    xas_integral_i,
                    (zerolistmaker(len(ax[integral_end:]) + 1) + xas_integral_i[-1]),
                ]
            )
            xas_integral = np.array(xas_integral1)
            xas_bg = np.array(xas_bg_i)
            xas = np.array(xas_i)

        elif ax.ndim and bx.ndim == 2:

            xas_bg = []
            xas = []
            xas_integral = []

            for i in range(ax.shape[0]):
                add = (
                    np.array(self.a_p_norm.read()["data"][1])[i]
                    + np.array(self.a_a_norm.read()["data"][1])[i]
                )

                integral_start = find_array_equivalent(
                    self.a_a_norm.read()["data"][0][i], local_arguments.background_start
                )
                integral_end = find_array_equivalent(
                    self.a_a_norm.read()["data"][0][i], local_arguments.background_stop
                )

                xas_bg_i, xas_i = background_xmcd(
                    energy=np.array(self.a_a_norm.read()["data"][0])[i],
                    xmcd=add,
                    args=local_arguments,
                )

                xas_integral_i = integrate.cumtrapz(
                    xas_i[integral_start:integral_end],
                    self.a_a_norm.read()["data"][0][i][integral_start:integral_end],
                )
                # self.xas_integral = np.append(xas_integral[0], xas_integral[0][-1])
                xas_integral1 = np.concatenate(
                    [
                        zerolistmaker(
                            len(
                                self.a_a_norm.read()["data"][0][0][0:integral_start] + 1
                            )
                        ),
                        xas_integral_i,
                        (
                            zerolistmaker(
                                len(self.a_a_norm.read()["data"][0][0][integral_end:])
                                + 1
                            )
                            + xas_integral_i[-1]
                        ),
                    ]
                )
                xas_integral_i = list(xas_integral1)

                xas_integral.append(xas_integral_i)
                xas.append(xas_i)
                xas_bg.append(xas_bg_i)

            xas_bg = np.array(xas_bg)
            xas = np.array(xas)
            xas_integral = np.array(xas_integral)

        self.xas_calc = xas
        self.xas_bg_calc = xas_bg
        self.xas_integral_calc = xas_integral
        self.lines = [self.background_start.default, self.background_stop.default]

    def read_xas(self):
        return {
            "data": [self.a_a_norm.read()["data"][0], self.xas_calc, self.lines],
            "label": self.a_p_norm.read()["label"],
        }

    # return self.xas
    def read_xas_bg(self):
        return {
            "data": [self.a_a_norm.read()["data"][0], self.xas_bg_calc, self.lines],
            "label": self.a_p_norm.read()["label"],
        }
        # return self.xas_bg

    def read_xas_integral(self):
        return {
            "data": [
                self.a_a_norm.read()["data"][0],
                self.xas_integral_calc,
                self.lines,
            ],
            "label": self.a_p_norm.read()["label"],
        }
        # return self.xas_integral
