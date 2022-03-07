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


class FileReader(Function):
    """Given a file path"""

    def __init__(self, parent):
        super().__init__(parent, "FileReader")

        # create ports
        self.file_path = FilePathInput(self, "in")
        self.file_data = StreamOutput(self, "data", self.on_read)

        self.data = None

    def evaluate(self):

        # list_dict={}
        # for key, value in sample_dict.items():
        #    list_dict[key] = []

        # f = open(self.file_path.read())
        # data = f.read()
        # print(data)
        # samples = parse_data_file(self.file_path.read())

        # print(int(samples[0].z_value))
        # for key, value in sample_dict.items():
        #    if (int(samples[0].z_value) == sample_dict[key]):
        # print("hi")
        # list_dict[key].append(self.file_path.data)

        # save
        self.data = [self.file_path.read()]
        self.is_valid = True

    def on_read(self):

        return self.data
