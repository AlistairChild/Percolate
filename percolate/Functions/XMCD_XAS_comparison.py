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
from percolate.Subfunctions.difference import difference
from percolate.Subfunctions.Transpose import Transpose
from percolate.Subfunctions.FindValue import FindValue
from percolate.Subfunctions.SumRules import SumRules

from percolate.Subfunctions.Addition import addition

class XMCD_XAS_comparison(CompositeFn):
    """This function allows for a comparison between the XMCD and XAS spectra"""

    def __init__(self):

        super().__init__("XMCD_XAS_comparison")

        # create instance
        dr = DirReader()
        p = XMCDStreamParser()
        bs = background_subtraction2()
        bs2 = background_subtraction2()
        norm = Normalise()
        norm2 = Normalise()
        step = step_subtraction()
        diff = difference()
        diff_xas_xmcd = difference()
        ad= addition()

        # subfns
        self.subfns.append(dr)
        self.subfns.append(p)
        self.subfns.append(bs)
        self.subfns.append(bs2)
        self.subfns.append(norm)
        self.subfns.append(diff)
        self.subfns.append(ad)
        self.subfns.append(norm2)
        self.subfns.append(diff_xas_xmcd)

        # edges
        self.edges.append(Edge(dr.dir_contents, p.input))
        self.edges.append(Edge(p.t_a_all, bs.input_data))
        self.edges.append(Edge(p.t_p_all, bs2.input_data))
        self.edges.append(Edge(bs.subtracted_background, norm.t_p_all))
        self.edges.append(Edge(bs2.subtracted_background, norm.t_a_all))
        self.edges.append(Edge(norm.a_a_norm, diff.A))
        self.edges.append(Edge(norm.a_p_norm, diff.B))
        self.edges.append(Edge(norm.a_a_norm, ad.A))
        self.edges.append(Edge(norm.a_p_norm, ad.B))
        self.edges.append(Edge(ad.added, norm2.t_a_all))
        self.edges.append(Edge(diff.diff, norm2.t_p_all))
        self.edges.append(Edge(norm2.a_a_norm, diff_xas_xmcd.A))
        self.edges.append(Edge(norm2.a_p_norm, diff_xas_xmcd.B))


function = XMCD_XAS_comparison()
