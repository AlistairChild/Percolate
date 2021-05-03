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
from percolate.toolkit.find_files2 import find_files2


class DirReader(Function):
    """Given a file path"""

    def __init__(self):
        super().__init__("DirReader")

        # create ports
        self.dir_path = DirPathInput(self, "in")
        self.dir_contents = StreamOutput(self, "data", self.read)


        self.data = None

    def evaluate(self):

        list_dict = {}

        # find files
        files = find_files2(self.dir_path.read())

        # for key, value in sample_dict.items():
        #    list_dict[key] = []

        # fill these lists with the files of that sample!
        # for file in files:

        #    f = open(file)
        #    data = f.read()
        #    samples = parse_data_file(data)
        # print(int(samples[0].z_value))
        #    for key, value in sample_dict.items():
        #        if (int(samples[0].z_value) == sample_dict[key]):
        #            list_dict[key].append(file)
        self.data = files

    def read(self):

        return self.data
