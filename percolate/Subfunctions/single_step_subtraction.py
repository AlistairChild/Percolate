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
from percolate.toolkit.step2 import step2
from percolate.toolkit.single_step import single_step


class args_step:
    def __init__(self, parent):

        self.step_start = parent.step_start.default
        self.step_stop = parent.step_stop.default
        self.apply_step = parent.apply_step.default
        self.fit_function = parent.fit_function.default
        self.edge = parent.edge.default


class single_step_subtraction(Function):
    """TODO: Centre the step function on the peaks energy!"""

    def __init__(self, parent):

        super().__init__(parent, "step_subtraction")

        # Input Ports
        self.input_array = StreamInput(self, "input_array")

        self.apply_step = choice_input(self, "Apply", "on", ["on", "off"])
        self.fit_function = choice_input(
            self, "fit_function", "Voight", ["Voight", "Arctan"]
        )
        self.step_start = int_input(self, "step_start", self.input_array, None)
        self.step_stop = int_input(self, "step_stop", self.input_array, None)
        self.edge = int_input(self, "edge", self.input_array, None)

        # output ports
        self.stepfunction = ArrayOutput(self, "stepfunction", self.read_stepfunction)
        self.subtracted_step = ArrayOutput(
            self, "post_step_a", self.read_subtracted_step
        )




    # evaluate method
    def evaluate(self):

        local_arguments = args_step(self)

        self.stepfunction_calc, self.subtracted_step_calc = single_step(
            energy=self.input_array.read()["data"][0],
            absorption=self.input_array.read()["data"][1],
            args=local_arguments,
        )

        self.lines = [self.step_start.default, self.step_stop.default]

    def read_stepfunction(self):
        return {
            "data": [
                self.input_array.read()["data"][0],
                self.stepfunction_calc,
                self.lines,
            ],
            "label": self.input_array.read()["label"],
        }
        # return self.stepfunction_a

    def read_subtracted_step(self):
        return {
            "data": [
                self.input_array.read()["data"][0],
                self.subtracted_step_calc,
                self.lines,
            ],
            "label": self.input_array.read()["label"],
        }
        # return self.post_step_p

