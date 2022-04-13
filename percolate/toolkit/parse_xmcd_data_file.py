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
import re
import numpy as np


class xmcdSample:
    # Represent a single XMCD sample point.Only those properties relevant to the analysis are represented.
    def __init__(self, mag, e, ioes, ey, ly, clock):

        self.mag = mag
        self.e = e
        self.ioes = ioes
        self.ey = ey
        self.ly = ly
        self.clock = clock


    @property
    def transmission(self):
        # print(self.clock)
        # return self.ey/ (self.ioes-self.clock)

        return self.ey/(self.clock+self.ioes)

    def z_value(self):
        pass



def parse_xmcd_data_file(file_path):
    "Parse XMCD Samples from file.If the data file/column format changes accomodate that in here."

    #Sample record headers look like:-
    #Time of Day	Time (s)	Z	Magnet Field	Energy	Beam Current	I0 ES	EY	Counter 2	LY	Clock
    COL_TITLE_RE = "Time of Day"
    COL_TITLE_RE = re.compile(COL_TITLE_RE) 

    #dictionary to contain the column numbers of column headers
    listofcolumns = {
        "Magnet Field":0,
        "Energy": 0,
        "I0 ES" : 0,
        "EY"    : 0,
        "LY"    : 0,
        "Clock" :  0
    }

    # Sample record lines look like:-
    #    15:52:51 97.76799774 -1.79999995 66.20078278 750.09997559 500.39013672	...

    DATA_RE = "^\d\d:\d\d:\d\d\s+"
    DATA_CRE = re.compile(DATA_RE)  # Pre-compile the pattern for greater speed

    # Open file and examine line by line
    data_file = file_path.split("\n")
    samples = []
    for line in data_file:

        # Only process valid looking data lines
        if COL_TITLE_RE.match(line):
            
            # Split the tab separated column headers into an array.
            vals = line.split("\t")
            
            #update listofcolumns dictionary with the position of column headers in current file
            for item in range(len(vals)):
                for j in listofcolumns.keys():
                    #take the first of all values 
                    if vals[item] == j and listofcolumns[j] == 0:
                        listofcolumns[j] = item

        if DATA_CRE.match(line):

            # Split the white-space separated text values into an array.
            vals = line.split()

            # Select values from the columns that we want
            # and convert from text to float at same time.
            props = [float(vals[col]) for col in listofcolumns.values()]

            # Construct XMCD Sample object from selected values.
            # This assumes COLS are listed in order required by
            # the Sample constructor.
            samples.append(xmcdSample(*props))


    return samples
