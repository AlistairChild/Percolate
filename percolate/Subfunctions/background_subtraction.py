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
from percolate.framework import free_int_input
from percolate.framework import bool_input
from percolate.framework import choice_input
from percolate.framework import Function


# Tools
from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.check_values_in_range import check_values_in_range
from percolate.toolkit.background1 import background1
from percolate.toolkit.exponential_fit import exponential_decay
from percolate.toolkit.Fit_inside_limits_polynomial import Fit_inside_limits_polynomial
from percolate.toolkit.Fit_outside_limits_polynomial import (
    Fit_outside_limits_polynomial,
)
from percolate.toolkit.make_zero_array import make_zero_array

option1 = "No fit"
option2 = "Polynomial fit inside limits"
option3 = "Polynomial fit outside limits"
option4 = "exp decay (fits for all e < 'Background_start' and e > ' Background_end')"
option5 = "2 point linear (straight line between 2 points)"

class args_background:
    def __init__(self, parent):

        self.p_start = parent.p_start.default
        self.p_end = parent.p_end.default
        self.power = parent.power.default
        self.apply_offset = parent.apply_offset.default
        self.fit = parent.fit.default


class background_subtraction2(Function):
    def __init__(self, parent):

        super().__init__(parent, "background_subtraction")

        # streamed inputs
        # self.e = StreamInput(self, "e")
        self.input_data = StreamInput(self, "input_data")

        # input.changed += self.on_data
        # parameter inputs


        

        self.fit = choice_input(
            fn=self,
            name="Fitting options",
            default=option1,
            choices=[
                option1,
                option2,
                option3,
                option4,
                option5,
            ],
        )
        self.apply_offset = choice_input(
            fn=self,
            name="apply_offset",
            default="off",
            choices=[
                "off",
                "on (shifts post 'Background_end' by amount equal to e = 'Background_end' to e = 'Background_start' )",
            ],
        )
        # self.apply_offset = int_input(self, "apply_offset", 1, 1, 3)
        self.p_start = int_input(self, "Background_start", self.input_data, None)
        self.p_end = int_input(self, "Background_end", self.input_data, None)
        self.power = free_int_input(self, "power", 1, 1, 3)

        # output ports
        self.background = ArrayOutput(self, "background", self.read_background)
        self.subtracted_background = ArrayOutput(
            self, "subtracted_background", self.read_subtracted_background
        )




    # evaluate method
    def evaluate(self):
        local_arguments = args_background(self)

        x = self.input_data.read()["data"][0]
        y = self.input_data.read()["data"][1]

        (
            self.x,
            self.calculated_subtracted_background,
            self.calculated_background,
        ) = calculate_background(
            x,
            y,
            local_arguments.p_start,
            local_arguments.p_end,
            local_arguments.power,
            local_arguments.fit,
            local_arguments.apply_offset,
        )

        self.lines = [self.p_start.default, self.p_end.default]

    def read_background(self):
        return {
            "data": [
                self.x,
                self.calculated_background,
                self.lines,
            ],
            "label": self.input_data.read()["label"],
        }

    def read_subtracted_background(self):
        return {
            "data": [
                self.x,
                self.calculated_subtracted_background,
                self.lines,
            ],
            "label": self.input_data.read()["label"],
        }


class background_subtraction(Function):
    def __init__(self, parent):

        super().__init__(parent, "background_subtraction")

        # streamed inputs
        # self.e = StreamInput(self, "e")
        self.t_p_all = StreamInput(self, "t_p_all")
        self.t_a_all = StreamInput(self, "t_a_all")
        # parameter inputs

        self.fit = choice_input(
            self,
            "Fitting options",
            option1,
            [
                option1,
                option2,
                option3,
                option4,
                option5,
            ],
        )
        self.apply_offset = choice_input(
            self,
            "apply_offset",
            "off",
            [
                "off",
                "on (shifts post 'Background_end' by amount equal to e = 'Background_end' to e = 'Background_start' )",
            ],
        )
        # self.apply_offset = int_input(self, "apply_offset", 1, 1, 3)
        self.p_start = int_input(self, "Background_start", self.t_p_all, None)
        self.p_end = int_input(self, "Background_end", self.t_p_all, None)
        self.power = free_int_input(self, "power", 1, 1, 4)

        # output ports
        self.a_p_background_subtraction = ArrayOutput(
            self, "a_p_background_subtraction", self.read_a_p_background_subtraction
        )
        self.a_a_background_subtraction = ArrayOutput(
            self, "a_a_background_subtraction", self.read_a_a_background_subtraction
        )
        self.a_p_background_subtracted = ArrayOutput(
            self, "a_p_background_subtracted", self.read_ia_p_background_subtracted
        )
        self.a_a_background_subtracted = ArrayOutput(
            self, "a_a_background_subtracted", self.read_ia_a_background_subtracted
        )
        # self.e_out= ArrayOutput(self, "e_out", self.read_e_out)

        # publish ports
        self.inputs = [
            # self.e,
            self.t_p_all,
            self.t_a_all,
            self.fit,
            self.apply_offset,
            self.p_start,
            self.p_end,
            self.power,
        ]

        self.outputs = [
            self.a_p_background_subtraction,
            self.a_a_background_subtraction,
            self.a_p_background_subtracted,
            self.a_a_background_subtracted,
            # self.e_out,
        ]


    # evaluate method
    def evaluate(self):

        local_arguments = args_background(self)

        x1 = self.t_p_all.read()["data"][0]
        y1 = self.t_p_all.read()["data"][1]

        x2 = self.t_a_all.read()["data"][0]
        y2 = self.t_a_all.read()["data"][1]

        (
            self.x1,
            self.calculated_subtracted_background1,
            self.calculated_background1,
        ) = calculate_background(
            x1,
            y1,
            local_arguments.p_start,
            local_arguments.p_end,
            local_arguments.power,
            local_arguments.fit,
            local_arguments.apply_offset,
        )
        (
            self.x2,
            self.calculated_subtracted_background2,
            self.calculated_background2,
        ) = calculate_background(
            x2,
            y2,
            local_arguments.p_start,
            local_arguments.p_end,
            local_arguments.power,
            local_arguments.fit,
            local_arguments.apply_offset,
        )

        self.lines = [self.p_start.default, self.p_end.default]

    def read_a_p_background_subtraction(self):
        return {
            "data": [self.x1, self.calculated_background1, self.lines],
            "label": self.t_p_all.read()["label"],
        }

    def read_a_a_background_subtraction(self):
        return {
            "data": [self.x2, self.calculated_background2, self.lines],
            "label": self.t_p_all.read()["label"],
        }

    def read_ia_p_background_subtracted(self):
        return {
            "data": [self.x1, self.calculated_subtracted_background1, self.lines],
            "label": self.t_p_all.read()["label"],
        }

    def read_ia_a_background_subtracted(self):
        return {
            "data": [self.x2, self.calculated_subtracted_background2, self.lines],
            "label": self.t_p_all.read()["label"],
        }


def calculate_background(x, y, p_start, p_end, power, fit, offset):

    x = np.array(x)
    y = np.array(y)

    lowerx = p_start
    upperx = p_end
    power = power
    offset = offset

    if x.ndim and y.ndim == 1:

        if fit == option1:

            x = x
            background = make_zero_array(x)
            y = y - background

        elif fit == option2:

            x, y, background = Fit_inside_limits_polynomial(
                x=x,
                y=y,
                lowerx=lowerx,
                upperx=upperx,
                power=power,
            )

        elif fit == option3:

            x, y, background = Fit_outside_limits_polynomial(
                x=x,
                y=y,
                lowerx=lowerx,
                upperx=upperx,
                power=power,
                offset =offset,
            )
        elif fit == option4:

            x, y, background = exponential_decay(
                x=x,
                y_in=y,
                lower_limit=lowerx,
                upper_limit=upperx,
            )

    elif x.ndim and y.ndim == 2:

        n_files = x.shape[0]

        x_list = []
        y_list = []
        background_list = []

        if fit == "No fit":

            for i in range(n_files):

                xi = x[i]
                backgroundi = make_zero_array(x[i])
                yi = y[i] - backgroundi

                x_list.append(xi)
                background_list.append(backgroundi)
                y_list.append(yi)

        elif fit == "Polynomial fit inside limits":

            for i in range(n_files):

                xi, yi, backgroundi = Fit_inside_limits_polynomial(
                    x=x[i],
                    y=y[i],
                    lowerx=lowerx,
                    upperx=upperx,
                    power=power,
                )
                x_list.append(xi)
                background_list.append(backgroundi)
                y_list.append(yi)

        elif fit == "Polynomial fit outside limits":

            for i in range(n_files):
                xi, yi, backgroundi = Fit_outside_limits_polynomial(
                    x=x[i],
                    y=y[i],
                    lowerx=lowerx,
                    upperx=upperx,
                    power=power,
                    offset=offset,
                )

                x_list.append(xi)
                background_list.append(backgroundi)
                y_list.append(yi)

        elif fit == option4:
            for i in range(n_files):
                xi, yi, backgroundi = exponential_decay(
                    x=x[i],
                    y_in=y[i],
                    lower_limit=lowerx,
                    upper_limit=upperx,
                    a_offset1 = 0,
                )

                x_list.append(xi)
                background_list.append(backgroundi)
                y_list.append(yi)

    
        x = np.array(x_list)
        y = np.array(y_list)
        background = np.array(background_list)

    return x, y, background
