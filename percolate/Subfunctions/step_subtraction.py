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

# toolKit
from percolate.toolkit.step2 import step2
from percolate.toolkit.step2 import step3
from percolate.toolkit.make_zero_array import make_zero_array


class args_step:
    def __init__(self, parent):

        self.step_start = parent.step_start.default
        self.step_stop = parent.step_stop.default
        self.step_intermediate = parent.step_intermediate.default
        self.apply_step = parent.apply_step.default
        self.fit_function = parent.fit_function.default
        self.fit_type = parent.fit_type.default


class step_subtraction(Function):
    """TODO: Centre the step function on the peaks energy!"""

    def __init__(self):

        super().__init__("step_subtraction")

        # Input Ports
        self.a_p_norm = StreamInput(self, "a_p_norm")
        self.a_a_norm = StreamInput(self, "a_a_norm")

        self.apply_step = choice_input(self, "Apply", "off", ["off", "on"])
        self.fit_type = choice_input(self, "fit_type", "Alpha", ["Alpha", "Beta"])
        self.fit_function = choice_input(
            self, "fit_function", "Voight", ["Voight", "Arctan"]
        )
        self.step_start = int_input(self, "step_start", self.a_p_norm, None)
        self.step_intermediate = int_input(
            self, "step_intermediate", self.a_p_norm, None
        )
        self.step_stop = int_input(self, "step_stop", self.a_p_norm, None)

        # output ports
        self.a_a_stepfunction = ArrayOutput(
            self, "a_a_stepfunction", self.read_a_a_stepfunction
        )
        self.a_p_stepfunction = ArrayOutput(
            self, "a_p_stepfunction", self.read_a_p_stepfunction
        )
        self.a_a_step_subtracted = ArrayOutput(
            self, "a_a_step_subtracted", self.read_a_a_step_subtracted
        )
        self.a_p_step_subtracted = ArrayOutput(
            self, "a_p_step_subtracted", self.read_a_p_step_subtracted
        )




    # evaluate method
    def evaluate(self):

        local_arguments = args_step(self)

        x1 = self.a_a_norm.read()["data"][0]
        y1 = self.a_a_norm.read()["data"][1]
        x2 = self.a_p_norm.read()["data"][0]
        y2 = self.a_p_norm.read()["data"][1]

        self.x1, self.post_step1, self.stepfunction1 = self.invoke_step_function(
            x1, y1, local_arguments
        )
        self.x2, self.post_step2, self.stepfunction2 = self.invoke_step_function(
            x2, y2, local_arguments
        )

        self.lines = [
            self.step_start.default,
            self.step_intermediate.default,
            self.step_stop.default,
        ]

    def read_a_a_stepfunction(self):
        return {
            "data": [self.x1, self.stepfunction1, self.lines],
            "label": self.a_p_norm.read()["label"],
        }
        # return self.stepfunction_a

    def read_a_p_stepfunction(self):
        return {
            "data": [self.x2, self.stepfunction2, self.lines],
            "label": self.a_p_norm.read()["label"],
        }
        # return self.stepfunction_p

    def read_a_a_step_subtracted(self):
        return {
            "data": [self.x1, self.post_step1, self.lines],
            "label": self.a_p_norm.read()["label"],
        }
        # return self.post_step_a

    def read_a_p_step_subtracted(self):
        return {
            "data": [self.x2, self.post_step2, self.lines],
            "label": self.a_p_norm.read()["label"],
        }
        # return self.post_step_p

    def invoke_step_function(self, x: np.ndarray, y: np.ndarray, arguments):

        # arguments to relay
        start = arguments.step_start
        intermediate = arguments.step_intermediate
        stop = arguments.step_stop
        function = arguments.fit_function
        fittype = arguments.fit_type

        if arguments.apply_step == "off":
            x_return = x
            y_return = y
            step_return = make_zero_array(x)

        elif arguments.apply_step == "on":

            if np.array(y).ndim and np.array(x).ndim == 1:

                x_return, y_return, step_return = step3(
                    x, y, start, intermediate, stop, function, fittype
                )

            elif np.array(y).ndim and np.array(x).ndim == 2:

                xlist = []
                ylist = []
                steplist = []

                for i in range(np.array(y).shape[0]):
                    xi, yi, stepi = step3(
                        x[i], y[i], start, intermediate, stop, function, fittype
                    )
                    xlist.append(xi)
                    ylist.append(yi)
                    steplist.append(stepi)

                x_return = np.array(xlist)
                y_return = np.array(ylist)
                step_return = np.array(steplist)
            else:
                print("not 1 or 2 dimensions")
                x_return = x
                y_return = y
                step_return = make_zero_array(x)
        else:
            print("else, what")
            x_return = x
            y_return = y
            step_return = make_zero_array(x)

        return x_return, y_return, step_return
