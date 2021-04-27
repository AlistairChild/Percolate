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


from percolate.event import Event

"""The main framework of the programme ("do not modify unless you know what you are doing!")"""


class Port:
    def __init__(self, fn, name):

        self.fn = fn
        self.name = name

        # Track the number of edges attached
        self.edges = []

    def get_path(self):
        return_path = self.fn.getpath(self.name)
        return return_path


class InPort(Port):
    def __init__(self, fn, name):

        super().__init__(fn, name)

    def notice(self, note):
        """Propagate notifications to function"""

        self.fn.notice(note)

    def read(self):
        """Propagate read request via Edge"""
        if self.edges:
            return self.edges[0].read()
        else:
            return None


class OutPort(Port):
    def __init__(self, fn, name, read_fn):

        super().__init__(fn, name)

        self.read_fn = read_fn
        self.notice_event = Event(note=bool)

    def notice(self, note):

        self.notice_event(note=note)

    def read(self):

        if not self.fn.is_valid:
            # print("Evaluate: " + self.fn.name)
            self.fn.evaluate()

            self.fn.is_valid = True

        return self.read_fn()


class StreamOutput(OutPort):
    pass


class TextOutput(OutPort):
    pass


class StreamInput(InPort):
    pass


class ArrayOutput(OutPort):
    pass


class FilePathInput(InPort):
    pass


class DirPathInput(InPort):
    pass


class MuxInput(InPort):
    pass


class MuxOutput(OutPort):
    pass


class Param_input(InPort):
    def __init__(self, fn, name, default):

        super().__init__(fn, name)

        self.default = default


class func_Output(OutPort):
    pass


class bool_input(InPort):
    def __init__(self, fn, name, min, default, max):

        super().__init__(fn, name)

        self.min = min
        self.default = default
        self.max = max


class int_input(InPort):
    def __init__(self, fn, name, input_stream, default):

        super().__init__(fn, name)

        self.input_stream = input_stream
        self.default = default


class num_input(InPort):
    def __init__(self, fn, name, input_stream, default):

        super().__init__(fn, name)

        self.input_stream = input_stream
        self.default = default


class free_int_input(InPort):
    def __init__(self, fn, name, min, default, max):

        super().__init__(fn, name)

        self.min = min
        self.default = default
        self.max = max


class choice_input(InPort):
    def __init__(self, fn, name, default, choices):

        super().__init__(fn, name)

        self.choices = choices
        self.default = choices[0]


class Function:
    def __init__(self, name):

        self.name = name
        self.inputs = []
        self.outputs = []
        self.is_valid = False

    def notice(self, note):
        """Handle notice and propagate to all outputs"""

        # print(self.name + ": " + str(note))
        if note == False:
            self.is_valid = False

        # If this is a terminal node trigger evaluation
        if not self.outputs:
            if note == True and not self.is_valid:
                # print(self.name + ": Evaluate")
                self.evaluate()
                self.is_valid = True
        else:
            for out in self.outputs:
                out.notice(note)


class Edge:
    """Connect output port to input port"""

    def __init__(self, p1, p2):

        self.p1 = p1
        self.p2 = p2

        self.p1.edges.append(self)
        self.p2.edges.append(self)

        self.p1.notice_event += self.on_notice

    def on_notice(self, note):
        """Propagate notices from src to dst port"""

        self.p2.notice(note)

    def read(self):
        """Propagate read to the source port"""

        return self.p1.read()


class CompositeFn(Function):
    def __init__(self, name):
        super().__init__(name)

        self.subfns = []
        self.edges = []