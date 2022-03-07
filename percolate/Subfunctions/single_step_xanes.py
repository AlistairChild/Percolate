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
from percolate.toolkit.single_step import single_step



class args_step:
    def __init__(self, parent):

        self.apply_step = parent.apply_step.default
        self.fit_function = parent.fit_function.default

        self.pre_feature_min = parent.pre_feature_min.default
        self.pre_feature_max = parent.pre_feature_max.default
        self.post_feature_min = parent.post_feature_min.default
        self.post_feature_max = parent.post_feature_max.default


class single_step_subtraction_xanes(Function):
    """TODO: Centre the step function on the peaks energy!"""

    def __init__(self, parent):

        super().__init__(parent, "step_subtraction")

        # Input Ports
        self.input_array = StreamInput(self, "input_array")

        self.apply_step = choice_input(self, "Apply", "off", ["off", "on"])
        self.fit_function = choice_input(
            self, "fit_function", "Voight", ["Voight", "Arctan"]
        )
        self.pre_feature_min = int_input(
            self, "pre_feature_min", self.input_array, None
        )
        self.pre_feature_max = int_input(
            self, "pre_feature_max", self.input_array, None
        )
        self.post_feature_min = int_input(
            self, "post_feature_min", self.input_array, None
        )
        self.post_feature_max = int_input(
            self, "post_feature_max", self.input_array, None
        )

        # output ports
        self.stepfunction = ArrayOutput(self, "stepfunction", self.read_stepfunction)
        self.subtracted_step = ArrayOutput(
            self, "subtracted_step", self.read_subtracted_step
        )




    # evaluate method
    def evaluate(self):

        local_arguments = args_step(self)

        x = self.input_array.read()["data"][0]
        y = self.input_array.read()["data"][1]
        pre_feature_min = local_arguments.pre_feature_min
        pre_feature_max = local_arguments.pre_feature_max
        post_feature_min = local_arguments.post_feature_min
        post_feature_max = local_arguments.post_feature_max

        if local_arguments.apply_step == "off":

            x = x
            background = make_zero_array(x)
            y = y - background

        else:
            x, y, background = pre_edge_fit(
                x,
                y,
                pre_feature_min,
                pre_feature_max,
                post_feature_min,
                post_feature_max,
            )

        self.x = x
        self.y = y
        self.background = background

        self.lines = [
            pre_feature_min,
            pre_feature_max,
            post_feature_min,
            post_feature_max,
        ]

    def read_stepfunction(self):
        return {
            "data": [self.x, self.background, self.lines],
            "label": self.input_array.read()["label"],
        }
        # return self.stepfunction_a

    def read_subtracted_step(self):
        return {
            "data": [self.x, self.y, self.lines],
            "label": self.input_array.read()["label"],
        }
        # return self.post_step_p

    def calculate_fit(self, x, y, argument):
        pass
