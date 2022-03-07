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

# generic imports
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

# subfunction imports
from percolate.Subfunctions.DirReader import DirReader
from percolate.Subfunctions.FileReader import FileReader
from percolate.Subfunctions.parser import EXAFSStreamParser
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
from percolate.Subfunctions.IdentifyPeaks import IdentifyPeaks
from percolate.Subfunctions.single_step_subtraction import single_step_subtraction


class EXAFS(CompositeFn):
    def __init__(self):

        super().__init__(None, "EXAFS")

        fr = FileReader(self)
        exp = EXAFSStreamParser(self)
        bs = background_subtraction2(self)
        ss = single_step_subtraction(self)
        ipeaks = IdentifyPeaks(self)

        self.subfns.append(fr)
        self.subfns.append(exp)
        self.subfns.append(bs)
        self.subfns.append(ss)
        self.subfns.append(ipeaks)

        self.edges.append(Edge(fr.file_data, exp.input))

        self.edges.append(Edge(exp.intensity, bs.input_data))

        self.edges.append(Edge(bs.background, ss.input_array))

        self.edges.append(Edge(ss.subtracted_step, ipeaks.input_array))


function = EXAFS()
