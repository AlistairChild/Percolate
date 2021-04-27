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
import os
from percolate.toolkit.parse_xmcd_data_file import parse_xmcd_data_file


def find_files2(data_path):

    files = []
    if os.path.isdir(data_path):
        files = [
            os.path.join(data_path, filename)
            for filename in os.listdir(data_path)
            if os.path.isfile(os.path.join(data_path, filename))
        ]
    elif os.path.isfile(data_path):
        files = [
            data_path,
        ]

    if not files:
        raise Exception(" - No files found in data path: %s" % data_path)
    print("--------------------------------------------------------------")
    print("--------------------------------------------------------------")
    print("Files read in folder (%s);" % os.path.basename(data_path))

    for x in range(len(files)):
        print("-%s" % os.path.basename(files[x]))
    return files
