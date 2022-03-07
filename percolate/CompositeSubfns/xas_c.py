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


# Generic imports
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
from percolate.framework import Edge
from percolate.framework import CompositeFn

# Subfunction imports
from percolate.Subfunctions.DirReader import DirReader
from percolate.Subfunctions.parser import XMCDStreamParser
from percolate.Subfunctions.background_subtraction import background_subtraction
from percolate.Subfunctions.background_subtraction import background_subtraction2
from percolate.Subfunctions.Normalise import Normalise
from percolate.Subfunctions.step_subtraction import step_subtraction
from percolate.Subfunctions.XAS import Xas
from percolate.Subfunctions.area import Area
from percolate.Subfunctions.Multiplexer import Multiplexer
from percolate.Subfunctions.Addition import addition
from percolate.Subfunctions.difference import difference
from percolate.Subfunctions.Transpose import Transpose
from percolate.Subfunctions.FindValue import FindValue
from percolate.Subfunctions.SumRules import SumRules
from percolate.Subfunctions.integrate import Integrate


class Xas_c(CompositeFn):
    def __init__(self, parent, inputs, outputs):

        super().__init__(parent, "XAS_composite")

        # xas = Xas()

        bs_xas = background_subtraction(self)
        ad = addition(self)
        intgr_xas = Integrate(self)
        r_val = FindValue(self, "r_val")

        # self.subfns.append(xas)
        self.subfns.append(bs_xas)
        self.subfns.append(ad)
        self.subfns.append(intgr_xas)
        self.subfns.append(r_val)

        if inputs and outputs:
            # Pass step subtraction spectra to difference and xas functions
            self.edges.append(Edge(inputs.a_a_step_subtracted, bs_xas.t_a_all))
            self.edges.append(Edge(inputs.a_p_step_subtracted, bs_xas.t_p_all))

            self.edges.append(Edge(bs_xas.a_a_background_subtracted, ad.A))
            self.edges.append(Edge(bs_xas.a_p_background_subtracted, ad.B))

            self.edges.append(Edge(ad.added, intgr_xas.input))

            # find the p, q and r values to be used in sum rules
            self.edges.append(Edge(intgr_xas.integral, r_val.inputarray))

            # send p, q, r values to the sum rules
            self.edges.append(Edge(r_val.value, outputs.r))
