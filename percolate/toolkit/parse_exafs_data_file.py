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


class Sample:

    # Properties to be selected from file.

    def __init__(self, energy, intensity):

        self.energy = energy

        self.intensity = intensity


def parse_data_file(data):
    "Parse EXAFS Samples from file. If the data file/column format changes accomodate that in here."

    pattern_seen = None
    # Sample record lines look like:-
    #    1086.33 280

    # Matching the time stamp pattern at start of the data lines seems adequate:
    DATA_RE = "#Acquired="
    DATA_CRE = re.compile(DATA_RE)  # Pre-compile the pattern for greater speed

    # List of column indices corresponding to required properties:
    #    (energy, intensity)
    SELECT_COLS = (0, 1)

    samples = []

    data_file = data.split("\n")

    # Only process valid looking data lines
    for line in data_file:

        # if pattern noticed
        if pattern_seen == True:

            # Split variables by tab seperation
            vals = line.split("\t")

            # Select values from the columns that we want
            # and convert from text to float at same time.
            props = [float(vals[col]) for col in SELECT_COLS]

            # Construct XMCD Sample object from selected values.
            # This assumes COLS are listed in order required by
            # the Sample constructor.
            samples.append(Sample(*props))

        # evaluate after since data starts after pattern
        if DATA_CRE.match(line):
            pattern_seen = True

    return samples
