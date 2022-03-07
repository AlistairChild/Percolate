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
from percolate.framework import num_input
from percolate.framework import bool_input
from percolate.framework import choice_input
from percolate.framework import Function
from percolate.framework import Edge
from percolate.framework import CompositeFn


from percolate.Subfunctions.difference import difference
from percolate.Subfunctions.Scale import scale
from percolate.Subfunctions.integrate import Integrate
from percolate.Subfunctions.Transpose import Transpose
from percolate.Subfunctions.FindValue import FindValue
from percolate.Subfunctions.background_subtraction import background_subtraction
from percolate.Subfunctions.background_subtraction import background_subtraction2


class Xmcd_c(CompositeFn):
    def __init__(self, parent, input, output):

        super().__init__(parent, "XMCD")

        diff = difference(self)
        transp = Transpose(self)
        bg_xmcd = background_subtraction2(self)
        sc = scale(self)
        itgr_xmcd = Integrate(self)
        q_val = FindValue(self, "q_val")
        p_val = FindValue(self, "p_val")

        self.subfns.append(diff)
        self.subfns.append(bg_xmcd)
        self.subfns.append(sc)
        self.subfns.append(itgr_xmcd)
        self.subfns.append(q_val)
        self.subfns.append(p_val)

        if input and output:
            # Pass step subtraction spectra to difference and xas functions
            self.edges.append(Edge(input.a_a_step_subtracted, diff.A))
            self.edges.append(Edge(input.a_p_step_subtracted, diff.B))

            # From difference to transpose
            self.edges.append(Edge(diff.diff, bg_xmcd.input_data))

            self.edges.append(Edge(bg_xmcd.subtracted_background, sc.input))
            self.edges.append(Edge(sc.scaled, itgr_xmcd.input))

            # self.edges.append(Edge(bg.background, itgr.input))

            self.edges.append(Edge(itgr_xmcd.integral, p_val.inputarray))
            self.edges.append(Edge(itgr_xmcd.integral, q_val.inputarray))

            # send p, q, r values to the sum rules
            self.edges.append(Edge(p_val.value, output.p))
            self.edges.append(Edge(q_val.value, output.q))
