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
import percolate
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

from percolate.Subfunctions.Addition import addition
from percolate.Subfunctions.DirReader import DirReader
from percolate.Subfunctions.FileReader import FileReader
from percolate.Subfunctions.parser import XMCDStreamParser
from percolate.Subfunctions.parser import SimpleParser
from percolate.Subfunctions.background_subtraction import background_subtraction2
from percolate.Subfunctions.background_subtraction import background_subtraction
from percolate.Subfunctions.Normalise import Normalise
from percolate.Subfunctions.step_subtraction import step_subtraction
from percolate.Subfunctions.single_step_subtraction_xanes import (
    single_step_subtraction_xanes,
)
from percolate.Subfunctions.XAS import Xas
from percolate.Subfunctions.area import Area
from percolate.Subfunctions.IdentifyPeaks import IdentifyPeaks


class pre_peak_subtraction(CompositeFn):
    def __init__(self):

        super().__init__("pre_peak_subtraction")

        '''# Subfunctions used
        fr = FileReader()
        p = SimpleParser()
        bs = background_subtraction2()
        step = single_step_subtraction_xanes()
        peak_id = IdentifyPeaks()

        # subfns
        self.subfns.append(fr)
        self.subfns.append(p)
        self.subfns.append(bs)
        self.subfns.append(step)
        self.subfns.append(peak_id)

        # edges
        self.edges.append(Edge(fr.file_data, p.input))

        self.edges.append(Edge(p.intensity, bs.input_data))

        self.edges.append(Edge(bs.subtracted_background, step.input_array))

        self.edges.append(Edge(step.subtracted_step, peak_id.input_array))'''
        
        
        # Subfunctions used
        dr = DirReader()
        p = XMCDStreamParser()
        bs = background_subtraction()
        step = step_subtraction()
        ad = addition()
        peak_id = IdentifyPeaks()

        # subfns
        self.subfns.append(dr)
        self.subfns.append(p)
        self.subfns.append(bs)
        self.subfns.append(step)
        self.subfns.append(ad)
        self.subfns.append(peak_id)

        # edges
        self.edges.append(Edge(dr.dir_contents, p.input))

        self.edges.append(Edge(p.t_a_all, bs.t_a_all))
        self.edges.append(Edge(p.t_p_all, bs.t_p_all))

        self.edges.append(Edge(bs.a_p_background_subtracted, step.a_p_norm))
        self.edges.append(Edge(bs.a_a_background_subtracted, step.a_a_norm))

        self.edges.append(Edge(step.a_a_step_subtracted, ad.A))
        self.edges.append(Edge(step.a_p_step_subtracted, ad.B))
        
        self.edges.append(Edge(ad.added, peak_id.input_array))


function = pre_peak_subtraction()
