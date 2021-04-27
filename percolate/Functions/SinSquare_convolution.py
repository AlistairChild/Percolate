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
from scipy import signal
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
from percolate.framework import Edge
from percolate.framework import CompositeFn

from percolate.Functions.Sin_Gen import SinGen
from percolate.Functions.Square_Gen import SquareGen
from percolate.Functions.Convolve import convolve

# Applications Functions
class SinSquareConv(CompositeFn):
    """
    This Function contains 3 Subfunctions allowing a sin wave to be convolved with a square wave.

    """

    def __init__(self):

        super().__init__("SinSquareConv")

        # subfunctions used in this function
        sin = SinGen()
        square = SquareGen()
        conv = convolve()

        # subfns
        self.subfns.append(sin)
        self.subfns.append(square)
        self.subfns.append(conv)

        # edges used for passing data from the output of one function to the input of another
        self.edges.append(Edge(sin.sin, conv.A))
        self.edges.append(Edge(square.square, conv.B))


function = SinSquareConv()
