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
from framework import Port
from framework import InPort
from framework import OutPort
from framework import StreamOutput
from framework import TextOutput
from framework import StreamInput
from framework import ArrayOutput
from framework import FilePathInput
from framework import DirPathInput
from framework import MuxInput
from framework import MuxOutput
from framework import Param_input
from framework import func_Output
from framework import int_input
from framework import bool_input
from framework import choice_input
from framework import Function
from framework import Edge
from framework import CompositeFn

# subfunction imports
from Subfunctions.DirReader import DirReader
from Subfunctions.FileReader import FileReader
from Subfunctions.parser import EXAFSStreamParser
from Subfunctions.background_subtraction import background_subtraction
from Subfunctions.background_subtraction import background_subtraction2
from Subfunctions.Normalise import Normalise
from Subfunctions.step_subtraction import step_subtraction
from Subfunctions.XAS import Xas
from Subfunctions.area import Area
from Subfunctions.Multiplexer import Multiplexer
from Subfunctions.difference import difference
from Subfunctions.Transpose import Transpose
from Subfunctions.FindValue import FindValue
from Subfunctions.IdentifyPeaks import IdentifyPeaks
from Subfunctions.single_step_subtraction import single_step_subtraction


class EXAFS(CompositeFn):
    def __init__(self):

        super().__init__("EXAFS")

        fr = FileReader()
        exp = EXAFSStreamParser()
        bs = background_subtraction2()
        ss = single_step_subtraction()
        ipeaks = IdentifyPeaks()
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
