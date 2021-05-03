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
import os

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
from percolate.toolkit.check_values_in_range import check_values_in_range
from percolate.toolkit.parse_xmcd_data_file import parse_xmcd_data_file
from percolate.toolkit.parse_exafs_data_file import parse_data_file
from percolate.toolkit.parse_xanes_data import parse_xanes_data_file


class args_parser:
    def __init__(self, parent):

        self.average_data = parent.average_data.default


class EXAFSStreamParser(Function):
    def __init__(self):

        super().__init__("EXAFSStreamParser")

        # input ports
        self.input = StreamInput(self, "in")
        self.average_data = choice_input(self, "Average data", "off", ["off", "on"])

        # output ports
        self.e = ArrayOutput(self, "e", self.read_e)
        self.intensity = ArrayOutput(self, "intensity", self.read_intensity)



        self.e_data = None
        self.intensity_data = None

    def evaluate(self):

        # e = None # Common energy scale extracted from first sample set
        intensity_all = []
        e_all = []
        names = []

        for file in self.input.read():
            name = os.path.basename(os.path.normpath(file))
            # parse_data_file is a defined function at top (it extracts columns)
            f = open(file)
            data = f.read()
            samples = parse_xanes_data_file(data)

            energy = [sample.energy for sample in samples]
            intensity = [sample.intensity for sample in samples]
            # Sanity check
            # if len(t_p) != len(t_a):
            #    raise Exception(" - Check SELECT_COL is selecting the correct columns from data file Number of parallel (%d) and anti-parallel (%d) samples differ" % (len(t_p), len(t_a)))
            # Add to array for averaging

            intensity_all.append(intensity)
            e_all.append(energy)

            # uncomment for XMLD
            # t_p_all.append(t_a[0:int(len(t_a)/2 -1)])
            # t_a_all.append(t_a[int(len(t_a)/2):-1])
            # e_all.append(e[0:int(len(t_a)/2 -1)])
            names.append(name)

        # write data to ports
        if self.average_data.default == "on":

            self.intensity_all_data = [np.mean(np.array(intensity_all), axis=0)]
            self.e_all_data = [np.mean(np.array(e_all), axis=0)]
            self.label = "Averaged"

        else:
            self.intensity_all_data = np.array(intensity_all)
            self.e_all_data = np.array(e_all)
            self.label = names

        self.lines = None

    def getpath(self, name):

        return_path = str(self) + "/" + str(name)

        return return_path

    def read_intensity(self):

        return {
            "data": [self.e_all_data, self.intensity_all_data, self.lines],
            "label": self.label,
        }
        # return self.t_a_all_data

    def read_e(self):
        return {
            "data": [self.e_all_data, self.e_all_data, self.lines],
            "label": self.label,
        }
        # return self.t_p_all_data

        # return self.e_data


class XMCDStreamParser(Function):
    def __init__(self):

        super().__init__("XMCDStreamParser")

        # input ports
        self.input = StreamInput(self, "in")
        self.average_data = choice_input(self, "Average data", "off", ["off", "on"])

        # output ports
        self.t_a_all = ArrayOutput(self, "t_a_all", self.read_t_a)
        self.t_p_all = ArrayOutput(self, "t_p_all", self.read_t_p)
        self.e = ArrayOutput(self, "e", self.read_e)

        # declare
        self.inputs = [
            self.input,
            self.average_data,
        ]
        self.outputs = [
            self.t_a_all,
            self.t_p_all,
            self.e,
        ]

        self.t_a_all_data = None
        self.t_p_all_data = None
        self.e_data = None
        self.parent = Function

    def getpath(self, name):
        # pass instance of class as path
        return_path = str(self) + "/" + str(name)
        # return_path = self.parent.getpath(self, str(self.__class__) + "/" + str(name))
        # return_path = self.parent.getpath(self, str(self.__class__.__name__) + "/" + str(name))
        return return_path

    def evaluate(self):

        # e = None # Common energy scale extracted from first sample set
        t_p_all = []  # Array of Parallel transmission series from each file
        t_a_all = []
        e_all = []
        names = []

        for file in self.input.read():
            name = os.path.basename(os.path.normpath(file))
            # parse_data_file is a defined function at top (it extracts columns)
            f = open(file)
            data = f.read()

            samples = parse_xmcd_data_file(data)

            # Sanity checks
            angle = [sample.angle for sample in samples]
            ioes = [sample.ioes for sample in samples]

            # change
            if len(samples) % 2:
                raise Exception(
                    " - Expected even number of samples, found odd number (%d) of samples"
                    % len(samples)
                )
            # ------------------------------------------------------------------------
            # Extract Energy series from 1st file only. Assume same in the rest.
            # ------------------------------------------------------------------------
            # if not e:
            # Assume parallel and anti-parallel samples have same energy sequence
            # and extract from one set or other.
            e = [sample.e for sample in samples if sample.mag < 0]

            # ------------------------------------------------------------------------
            # Parallel & Anti-parallel Transmission
            # -----------------------------------------------------------------------
            t_p = [sample.transmission for sample in samples if sample.mag >= 0]
            t_a = [sample.transmission for sample in samples if sample.mag < 0]

            # uncomment for XMLD
            """print(len(t_a))
            if len(t_p) == 0:
                t_p = t_a[0:500]
                t_a = t_a[501: 1001]
                e = e[0:500]
            if len(t_p) == 0:
                t_p = t_p[0:len(t_p)/2 -1]
                t_a = t_p[len(t_p)/2: len(t_p)]
                e=e[0:len(t_a)/2]
            print(len(t_p))"""

            # Sanity check
            if len(t_p) != len(t_a):
                raise Exception(
                    " - Check SELECT_COL is selecting the correct columns from data file. Number of parallel (%d) and anti-parallel (%d) samples differ"
                    % (len(t_p), len(t_a))
                )
            # Add to array for averaging
            t_p_all.append(t_p)
            t_a_all.append(t_a)
            e_all.append(e)

            # uncomment for XMLD
            # t_p_all.append(t_a[0:int(len(t_a)/2 -1)])
            # t_a_all.append(t_a[int(len(t_a)/2):-1])
            # e_all.append(e[0:int(len(t_a)/2 -1)])
            names.append(name)

        # write data to ports
        if self.average_data.default == "on":
            self.t_a_all_data = np.mean(np.array(t_a_all), axis=0)
            self.t_p_all_data = np.mean(np.array(t_p_all), axis=0)
            self.e_data = np.mean(np.array(e_all), axis=0)
            self.label = "Average"

        else:
            self.t_a_all_data = np.array(t_a_all)
            self.t_p_all_data = np.array(t_p_all)
            self.e_data = np.array(e_all)
            self.label = names

        self.lines = None

    def read_t_a(self):

        return {
            "data": [self.e_data, self.t_a_all_data, self.lines],
            "label": self.label,
        }
        # return self.t_a_all_data

    def read_t_p(self):
        return {
            "data": [self.e_data, self.t_p_all_data, self.lines],
            "label": self.label,
        }
        # return self.t_p_all_data

    def read_e(self):
        return {"data": [self.e_data, self.e_data, self.lines], "label": self.label}
        # return self.e_data


class SimpleParser(Function):
    def __init__(self):

        super().__init__("SimpleParser")

        # input ports
        self.input = StreamInput(self, "in")
        self.average_data = choice_input(self, "Average data", "off", ["off", "on"])

        # output ports
        self.e = ArrayOutput(self, "e", self.read_e)
        self.intensity = ArrayOutput(self, "intensity", self.read_intensity)

        # declare
        self.inputs = [
            self.input,
            self.average_data,
        ]
        self.outputs = [
            self.e,
            self.intensity,
        ]

        self.e_data = None
        self.intensity_data = None

    def getpath(self, name):
        # pass instance of class as path
        return_path = str(self) + "/" + str(name)

        return return_path

    def evaluate(self):

        # e = None # Common energy scale extracted from first sample set
        # e = None # Common energy scale extracted from first sample set
        intensity_all = []
        e_all = []
        names = []

        for file in self.input.read():
            name = os.path.basename(os.path.normpath(file))
            # parse_data_file is a defined function at top (it extracts columns)
            f = open(file)
            data = f.read()

            samples = parse_xanes_data_file(data)

            energy = [sample.energy for sample in samples]
            intensity = [sample.intensity for sample in samples]
            # Sanity check
            # if len(t_p) != len(t_a):
            #    raise Exception(" - Check SELECT_COL is selecting the correct columns from data file Number of parallel (%d) and anti-parallel (%d) samples differ" % (len(t_p), len(t_a)))
            # Add to array for averaging

            intensity_all.extend(intensity)
            e_all.extend(energy)

            # uncomment for XMLD
            # t_p_all.append(t_a[0:int(len(t_a)/2 -1)])
            # t_a_all.append(t_a[int(len(t_a)/2):-1])
            # e_all.append(e[0:int(len(t_a)/2 -1)])
            names.append(name)

            # Sanity check
            # if len(t_p) != len(t_a):
            #    raise Exception(" - Check SELECT_COL is selecting the correct columns from data file Number of parallel (%d) and anti-parallel (%d) samples differ" % (len(t_p), len(t_a)))
            # Add to array for averaging

        # write data to ports
        if self.average_data.default == "on":

            self.intensity_all_data = [np.mean(np.array(intensity_all), axis=0)]
            self.e_all_data = [np.mean(np.array(e_all), axis=0)]
            self.label = "Averaged"

        else:
            self.intensity_all_data = np.array(intensity_all)
            self.e_all_data = np.array(e_all)
            self.label = names
        print(self.intensity_all_data.ndim)
        self.lines = None

    def read_intensity(self):

        return {
            "data": [self.e_all_data, self.intensity_all_data, self.lines],
            "label": self.label,
        }
        # return self.t_a_all_data

    def read_e(self):
        return {
            "data": [self.e_all_data, self.e_all_data, self.lines],
            "label": self.label,
        }
        # return self.t_p_all_data
