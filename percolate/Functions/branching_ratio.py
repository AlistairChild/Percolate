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
from percolate.framework import Edge
from percolate.framework import CompositeFn


from percolate.Subfunctions.DirReader import DirReader
from percolate.Subfunctions.parser import XMCDStreamParser
from percolate.Subfunctions.background_subtraction import background_subtraction
from percolate.Subfunctions.Normalise import Normalise
from percolate.Subfunctions.step_subtraction import step_subtraction
from percolate.Subfunctions.XAS import Xas
from percolate.Subfunctions.area import Area


class Branching_ratio(CompositeFn):
    def __init__(self):

        super().__init__("Branching_ratio")

        # self.multioutput = MuxOutput("Mux")

        # reference to the functions
        dr = DirReader()
        # fr = FileReader()
        p = XMCDStreamParser()
        bs = background_subtraction()
        norm = Normalise()
        step = step_subtraction()
        xas = Xas()
        area = Area()

        self.subfns.append(dr)
        # self.subfns.append(fr)
        self.subfns.append(p)
        self.subfns.append(bs)
        self.subfns.append(norm)
        self.subfns.append(step)
        self.subfns.append(xas)
        self.subfns.append(area)

        # self.edges.append(Edge(fr.file_data, p.input))
        self.edges.append(Edge(dr.dir_contents, p.input))

        # From the parser to background subtraction
        self.edges.append(Edge(p.t_a_all, bs.t_a_all))
        self.edges.append(Edge(p.t_p_all, bs.t_p_all))

        # From the background subtraction to normalising block

        self.edges.append(Edge(bs.a_p_background_subtracted, norm.t_p_all))
        self.edges.append(Edge(bs.a_a_background_subtracted, norm.t_a_all))

        # From the normalisation to the step

        self.edges.append(Edge(norm.a_p_norm, step.a_p_norm))
        self.edges.append(Edge(norm.a_a_norm, step.a_a_norm))

        # From step to addition (XAS)

        self.edges.append(Edge(step.a_a_step_subtracted, xas.a_a_norm))
        self.edges.append(Edge(step.a_p_step_subtracted, xas.a_p_norm))

        # from xas to area calculation

        self.edges.append(Edge(xas.xas, area.input))


function = Branching_ratio()
