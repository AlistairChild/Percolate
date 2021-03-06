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

# generic
from os import listdir
import importlib.util
from os.path import isfile, join
import sys
import os
import argparse
import re
import csv
import wx.lib.agw.aui.tabmdi
from os import walk
import importlib
import random
import lmfit
from lmfit import Model
from lmfit import minimize, Parameters


import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

# wx
import wx
import wx.aui
import wx.lib.scrolledpanel

# import ctypes
import keyword
import wx.grid as gridlib
import wx.lib.agw.aui as aui
import wx.lib.agw.flatmenu as FM
from itertools import count

# specialized
import scipy
from scipy.optimize import curve_fit
from scipy.integrate import simps
from scipy import integrate

# Import subfunctions
from percolate.Subfunctions.area import Area
from percolate.Subfunctions.DirReader import DirReader
from percolate.Subfunctions.FindValue import FindValue
from percolate.Subfunctions.SumRules import SumRules
from percolate.Subfunctions.Multiplexer import Multiplexer
from percolate.Subfunctions.XAS import Xas
from percolate.Subfunctions.difference import difference
from percolate.Subfunctions.step_subtraction import step_subtraction
from percolate.Subfunctions.Transpose import Transpose
from percolate.Subfunctions.Normalise import Normalise
from percolate.Subfunctions.background_subtraction import background_subtraction
from percolate.Subfunctions.background_subtraction import background_subtraction2
from percolate.Subfunctions.parser import EXAFSStreamParser
from percolate.Subfunctions.parser import XMCDStreamParser
from percolate.Subfunctions.IdentifyPeaks import IdentifyPeaks

# Toolkit imports
from percolate.toolkit.find_array_equivalent import find_array_equivalent
from percolate.toolkit.zerolistmaker import zerolistmaker
from percolate.toolkit.import_path import import_path

# Framework imports
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
from percolate.framework import num_input
from percolate.framework import free_int_input
from percolate.framework import bool_input
from percolate.framework import choice_input
from percolate.framework import Function
from percolate.framework import Edge
from percolate.framework import CompositeFn
from percolate.framework import GridInput

# matplotlib (Plotting)
import matplotlib
import matplotlib.cm as cm
import matplotlib.colors
import matplotlib.cbook as cbook
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import (
    NavigationToolbar2WxAgg as NavigationToolbar,
)
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt, animation
import numpy as np
import matplotlib.pyplot as pl
import math
linestyle = [

     ('solid', 'solid'),      # Same as (0, ()) or '-'
     ('dotted', 'dotted'),    # Same as (0, (1, 1)) or '.'
     ('dashed', 'dashed'),    # Same as '--'
     ('dashdot', 'dashdot'),
     #parameterised
     ('dotted',                (0, (1, 1))),
     ('densely dotted',        (0, (1, 1))),

     ('dashed',                (0, (5, 5))),
     ('densely dashed',        (0, (5, 1))),

     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),

     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))

]
markers = [
    ".",
    "o",
    "v",
    "^",
    "<",
    ">",
    "1",
    "8",
    "s",
    "p",
    "P",
    "*",
    "+",
    "D",
    "d",

]
colors = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']

def exists_in_list(list, item):
    '''Returns true if item found in list'''
    for entry in list:
        if entry == item:
            return True

def exists_in_dict(dict, item):
    '''Returns true if item found in dictionary'''
    for key, value in dict.items():
        if key == item:
            return True

# GUI
class InputControlBase(Function):
    def __init__(self, target_port, name="source"):

        super().__init__(None, name)

        # Auto Create Edge from local output to remote input port
        self.outport = OutPort(self, "auto", self.read)
        self.edge = Edge(self.outport, target_port)

    def changed(self):
        """Drive 2-phase update"""
        self.outport.notice(False)
        self.outport.notice(True)

    def evaluate(self):
        # input controls are always valid so do nothing
        pass

    def read(self):
        raise NotImplementedError()


class OutputControlBase(Function):
    def __init__(self, source_port, name="sink"):

        super().__init__(None, name)

        # Auto Create Edge from local input to remote source port
        self.in_port = InPort(self, "auto")
        self.edge = Edge(source_port, self.in_port)


# Control panel widgets
class FileSelectorControl(InputControlBase):
    def __init__(self, parent, port):

        super().__init__(port, "FileSelector(%s)" % port.name)

        self.port = port
        # Create UI file selector in panel
        self.ui = wx.FileSelector(label=port.name)

        self.data = None
        # hook selection event

    def on_select(self, filename):
        # open file, read it & write to port

        self.data = readfile(filename)
        self.changed()

    def read(self):

        return self.data

    def dragg(self):
        pass


class MyDropTarget(wx.TextDropTarget):
    def __init__(self, parent, object, app):

        wx.TextDropTarget.__init__(self)
        self.object = object
        self.app = app
        self.parent = parent

    def OnDropText(self, x, y, data):
        print(data)
        port = self.app.lookup_port(data)
        print("Port: '%s' containes files : '%s'"%(port.name,port.read().get("label")))
        self.parent.DisplayData(port)
        self.parent.DisplayPorts(port)

        return True

class PlotPanel(wx.Panel):

    def __init__(self, parent, fgs, port, aui_notebook, manager, app):

        super().__init__(parent, name = "PlotPanel(%s)" % port.name)


class MaxPlotControl(OutputControlBase):
    
    def __init__(self, parent, port, aui_notebook, manager, app):

        # dictionary for plots
        self._dict = {}

        #coordinates of mouse
        self.xcoord = None
        self.ycoord = None

        # parent is the main frame
        self.panel = wx.Panel(app.main_frame, size=wx.Size(400,400))

        self.datarequest = wx.CheckBox(self.panel, label="Show data points")
        self.datarequest.SetValue(False)
        self.linerequest = wx.CheckBox(self.panel, label="Show line")
        self.linerequest.SetValue(True)
        self.legendrequest = wx.CheckBox(self.panel, label="Show Legend")
        self.legendrequest.SetValue(True)
        #does nothing
        self.guidelinesrequest = wx.CheckBox(self.panel, label="Show Guidelines")
        self.guidelinesrequest.SetValue(True)

        cbxsizer = wx.BoxSizer(wx.HORIZONTAL)

        cbxsizer.AddMany(
            [
                (self.guidelinesrequest, 1, wx.EXPAND),
                (self.datarequest, 1, wx.EXPAND),
                (self.linerequest, 1, wx.EXPAND),
                (self.legendrequest, 1, wx.EXPAND),
            ]
        )

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        fgs = wx.FlexGridSizer(4, 1, 10, 10)

        self.panel.fig = Figure((5, 3), 75)
        self.panel.subplots = self.panel.fig.add_subplot(111)
        
        self.coord = self.panel.fig.text(0.13,0.12, 'x:%1.4s, y:%1.4s'%(self.xcoord , self.ycoord))
        self.animation = animation.ArtistAnimation(self.panel.fig, [(self.coord,)])
        self.panel.fig.canvas = FigureCanvas(self.panel, -1, self.panel.fig)
        self.panel.toolbar = NavigationToolbar(self.panel.fig.canvas)  # matplotlib toolbar
        self.panel.toolbar.Realize()
        
        self.items_in_plot = wx.CheckListBox(
            self.panel, name="Ports Displayed", choices=[]
        )

        canvas_sizer = wx.BoxSizer(wx.HORIZONTAL)
        canvas_sizer.AddMany(
            [(self.panel.fig.canvas, 5, wx.EXPAND), (self.items_in_plot, 1, wx.EXPAND)]
        )

        dt = MyDropTarget(self, self.panel.fig.canvas, app)
        self.panel.fig.canvas.SetDropTarget(dt)

        fgs.AddMany(
            [
                (canvas_sizer, 1, wx.EXPAND),
                (self.panel.toolbar, 1, wx.EXPAND),
                (cbxsizer, 1, wx.EXPAND),
            ]
        )

        fgs.AddGrowableRow(0, 7)
        fgs.AddGrowableCol(0, 1)

        hbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, border=15)
        self.panel.SetSizer(hbox)

        self.panel.Bind(wx.EVT_CHECKBOX, self.on_data_point_request, self.datarequest)
        self.panel.Bind(wx.EVT_CHECKBOX, self.on_line_request, self.linerequest)
        self.panel.Bind(wx.EVT_CHECKBOX, self.on_legend_request, self.legendrequest)
        self.panel.Bind(
            wx.EVT_CHECKBOX, self.on_guideline_request, self.guidelinesrequest
        )
        self.panel.Bind(wx.EVT_CHECKLISTBOX, self.on_port_select, self.items_in_plot)
        self.panel.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move)

        self.ports = []
        self.evaluate()

        self.datapoints = False
        self.drawline = True
        self.legend = True
        self.guidelines = True

        self.selected_ports = []
        self.panel.fig.canvas.draw()

    def mouse_move(self, evt):
    
        self.xcoord, self.ycoord = evt.xdata, evt.ydata

        self.coord.set_text('x:%1.4s, y:%1.4s'%(self.xcoord , self.ycoord))

        self.panel.fig.canvas.draw()


    def on_port_select(self, evt):

        self.ports = []
        for item in self._dict.keys():
            if exists_in_list(self.items_in_plot.CheckedStrings, item.name):
                self.ports.append(item)
            else:
                pass

        self.evaluate()

    def on_legend_request(self, evt):

        if evt.IsChecked():
            self.legend = True
        else:
            self.legend = False
        self.evaluate()

    def on_guideline_request(self, evt):

        if evt.IsChecked():
            self.guidelines = True
        else:
            self.guidelines = False
        self.evaluate()

    def on_data_point_request(self, evt):

        if evt.IsChecked():
            self.datapoints = True
        else:
            self.datapoints = False
        self.evaluate()

    def on_line_request(self, evt):

        if evt.IsChecked():
            self.drawline = True
        else:
            self.drawline = False
        self.evaluate()

    def DisplayPorts(self, data):

        # create all gui references to ports
        if len(self.items_in_plot.Items) != 0:
            if exists_in_list(self.items_in_plot.Items, data.name):
                pass
            else:
                self.items_in_plot.Append(data.name)
        else:  # first instance
            self.items_in_plot.Append(data.name)

        self.items_in_plot.Check(len(self.items_in_plot.Items) - 1, check=True)

    def DisplayData(self, data):

        # create new item in dictionary
        self._dict[data] = self

        # clear the ports then fill from dictionary
        self.ports = []
        for item in self._dict.keys():
            self.ports.append(item)

        # just call for evaluation
        self.evaluate()

    def evaluate(self):
        
        
        # clear figure
        self.panel.subplots.clear()

        # we need to accompany multiple different ports
        count = 0
        for port in self.ports:
            
            # data
            
            x = np.array(port.read()["data"][0])
            y = np.array(port.read()["data"][1])
            lbl = list(port.read()["label"])
            lines = np.array(port.read()["data"][2])

            count = count + 1

            if x is not None and len(x.shape) > 1:
                
                # for item in x:
                for x_data, y_data, label in zip(x, y, lbl):
                    count = count + 1
                    try:
    
                        for line in lines:
        
                                if line:
            
                                    self.panel.lines = self.panel.subplots.axvline(line, 0, 1)
        
                    except:
        
                        pass

                    if len(x) != len(y):
                        y = "".join(y)
                        self.panel.lines = self.panel.subplots.plot(
                            x_data, y_data, color=colors[count%len(colors)], label = y, picker=2
                        )
                    else:
                        if self.datapoints and self.drawline:
                            self.panel.lines = self.panel.subplots.plot(
                                x_data,
                                y_data,
                                linestyle = linestyle[count%(len(linestyle))][1],
                                color=colors[count%len(colors)],
                                label = port.name + "/" + label,
                                picker=2
                            )
                            self.panel.subplots.scatter(
                                x_data, y_data, marker=markers[count%(len(markers))], color =colors[count%len(colors)], s=15, label = port.name + "/" + label
                            )

                        elif self.drawline:
                            self.panel.lines = self.panel.subplots.plot(
                                x_data,
                                y_data,
                                linestyle = linestyle[count%(len(linestyle))][1],
                                color=colors[count%len(colors)],
                                label=port.name + "/" + label,
                                picker=2
                            )

                        elif self.datapoints:
                            self.panel.subplots.scatter(
                                x_data, y_data, marker=markers[count%(len(markers))], color=colors[count%len(colors)], s=15,label = port.name + "/" + label
                            )

                        else:
                            pass

                    lines_labels = [
                        self.panel.subplots.get_legend_handles_labels() for a in self.panel.fig.axes
                    ]

                    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]

                    if self.legend:

                        self.panel.subplots.legend(lines, labels)

                        self.panel.subplots.legend()

            else:
                #self.panel.subplots.format_coords = format_coord

                try:

                    for line in lines:
    
                        if line:
    
                            self.panel.lines = self.panel.subplots.axvline(line, 0, 1)
    
                except:
    
                    pass
                if self.datapoints and self.drawline:
                    self.panel.lines = self.panel.subplots.plot(
                        x, y, linestyle = linestyle[count%(len(linestyle))][1], color=colors[count%len(colors)], label=lbl[0] + " - " + str(port.name)
                    )
                    self.panel.subplots.scatter(x, y, marker=markers[count%(len(markers))], color=colors[count%len(colors)], s=15,label = lbl[0] + " - " + str(port.name))

                elif self.drawline:
                    self.panel.lines = self.panel.subplots.plot(
                        x, y,linestyle = linestyle[count%(len(linestyle))][1], color=colors[count%len(colors)], label=lbl[0] + " - " + str(port.name)
                    )

                elif self.datapoints:
                    self.panel.subplots.scatter(x, y, marker=markers[count%(len(markers))], color=colors[count%len(colors)], s=15, label = lbl[0] + " - " + str(port.name))

                else:
                    pass

                if self.legend:

                    self.panel.subplots.legend()
                    
        
        
        
        self.panel.fig.canvas.draw()
        self.panel.toolbar.update()


            


class MinimalPlotControl(OutputControlBase):
    """Represents a vector output in one line
    - double clicking on graph opens a large static graph window
    - opening a canvas and dragging into window set up dynamic plot window"""

    def __init__(self, parent, fgs, port, aui_notebook, manager, app):

        super().__init__(port, "PlotControl(%s)" % port.name)

        self.port = port
        self.aui_notebook = aui_notebook
        self.manager = manager
        self.app = app
        self.parent = parent

        self.fig = Figure((5, 0.8), 75)
        self.canvas = FigureCanvas(parent, -1, self.fig)
        
        self.export_button = wx.Button(self.parent, label = " -> ")
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas, 10, wx.ALIGN_CENTRE | wx.LEFT)
        sizer.Add(self.export_button, 1, wx.ALIGN_CENTRE | wx.LEFT)
        fgs.Add(sizer, 0, wx.TOP | wx.EXPAND)

        # handlers
        self.canvas.mpl_connect("axes_enter_event", self.enter_axes)
        self.canvas.mpl_connect("axes_leave_event", self.leave_axes)
        self.canvas.mpl_connect("button_press_event", self.OnDrag)
        self.canvas.mpl_connect("button_release_event", self.OnDrag)
        
        self.export_button.Bind(wx.EVT_BUTTON, self.OnExportData)
        
        self.evaluate()
        
    def OnExportData(self, event):
        x = np.array(self.port.read()["data"][0])
        y = np.array(self.port.read()["data"][1])
        
        
        fdlg = wx.FileDialog(self.parent, "Input setting file path", "", "", "CSV files(*.csv)|*.*", wx.FD_SAVE)
        
        if fdlg.ShowModal() == wx.ID_OK:
            self.save_path = fdlg.GetPath() + ".csv"
        
        with open(self.save_path, "w",newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Energy", "Signal"]) 
            
            if x.ndim and y.ndim == 1:
                for i in range(len(x)):
                    writer.writerow([x[i], y[i]]) 
                    
            if x.ndim and y.ndim == 2:
                for i in range(len(x)):
                    for j in range(len(x[i])):
                        writer.writerow([x[i][j], y[i][j]]) 
                

                        
        
    def enter_axes(self, event):
        event.inaxes.patch.set_facecolor("lightgrey")
        event.canvas.draw()

    def leave_axes(self, event):
        event.inaxes.patch.set_facecolor("white")
        event.canvas.draw()

    def OnDrag(self, e):

        if e.dblclick:
            self.plot_stack = FigureStack(self.port)

        else:
            self.dragged = self.port
            my_data = wx.TextDataObject(str(self.port.get_path()))
            print(str(self.port.get_path()))
            dragsource = wx.DropSource(self.canvas)
            dragsource.SetData(my_data)
            result = dragsource.DoDragDrop(True)

    def OnDropInit(self, event):

        for key, item in self.app.canvas_dict.items():

            self.app.canvas_dict[key].DisplayData(self.dragged)

    def evaluate(self):

        self.fig.clear()

        a = self.fig.add_subplot(111)

        x = np.array(self.port.read()["data"][0])

        y = np.array(self.port.read()["data"][1])

        lines = np.array(self.port.read()["data"][2])

        lbl = list(self.port.read()["label"])

        if x.ndim and y.ndim == 1:

            try:

                for line in lines:

                    if line:

                        self.canvas.lines = a.axvline(line, 0, 1)

            except:

                pass

            self.canvas.lines = a.plot(x, y, color=colors[0], label=lbl)

        if x.ndim and y.ndim == 2:

            count = 0
            for xi, yi, label in zip(x, y, lbl):
                count = count + 1

                if lines.any():
                    for line in lines:
                        if line:
                            self.canvas.lines = a.axvline(line, 0, 1)
                else:
                    pass

                self.canvas.lines = a.plot(xi, yi, color=colors[count%len(colors)], label=label)

            if x.ndim == 3:

                print("3d")

        # else:

        #    if x.ndim == 1:

        #        self.canvas.lines = a.plot(x, y, color=colors[0], label=lbl)

        #    elif x.ndim == 2:

        #        print("2d")

        # if y is not None and len(y.shape) >= 1:
        #    print("plot")
        #    count = 0
        #
        #    for x_axis, y_axis, label in zip(x, y, lbl):

        #        try:

        #            for line in lines:

        #                self.canvas.lines = a.axvline(line, 0, 1)

        #        except:

        #            pass

        #        self.canvas.lines = a.plot(
        #            x_axis, y_axis, color=colors[count], label=label
        #        )

        #        count = count + 1
        # else:

        # self.lines = a.plot(x, y, "k", label=lbl)
        # self.lines = None
        # a.legend()

        self.fig.canvas.draw()
        a.legend()

        for key, item in self.app.canvas_dict.items():

            self.app.canvas_dict[key].evaluate()

class FigureStack(OutputControlBase):
    # ----------------------------------------------------------------------
    def __init__(self, name):

        x = np.array(name.read()["data"][0])
        y = np.array(name.read()["data"][1])
        lbl = list(name.read()["label"])

        number_of_colors = 24

        colors = [
            "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
            for i in range(number_of_colors)
        ]
        # if len(x.shape) > 1:
        if x is not None and len(x.shape) > 1:
            count = 0
            # for item in x:
            for x_axis, y_axis, label in zip(x, y, lbl):

                if len(x_axis) == 1:
                    pl.plot.axvline(x_axis, 0, 1)
                else:
                    pl.plot(x_axis, y_axis, color=colors[count%len(colors)], label=label)

                count = count + 1
        else:
            self.lines = pl.plot(x, y, "k", label=lbl)
            pl.legend()

        pl.legend()

        pl.title("FigureStack")

        pl.show()


class FileChooser(InputControlBase):
    def __init__(self, parent, fgs, port):

        super().__init__(port, "FileChooser(%s)" % port.name)
        self.port = port

        self.ctrl = wx.FilePickerCtrl(parent)
        fgs.Add(self.ctrl, 1, wx.EXPAND)

        self.ctrl.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_picked)
        self.path = None

    def on_picked(self, evt):

        self.path = evt.GetPath()
        self.changed()

    def read(self):

        return self.path


class DirChooser(InputControlBase):
    def __init__(self, parent, fgs, port):

        super().__init__(port, "DirChooser(%s)" % port.name)
        self.port = port

        self.ctrl = wx.DirPickerCtrl(parent)

        fgs.Add(self.ctrl, 1, wx.EXPAND)

        self.ctrl.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_picked)
        self.path = None

    def on_picked(self, evt):

        self.path = evt.GetPath()
        self.changed()

    def read(self):

        return self.path


class DictControl(OutputControlBase):
    def __init__(self, parent, fgs, port):

        super().__init__(port, "TextControl(%s)" % port.name)

        self.port = port

        self.ctrl = wx.TextCtrl(parent, style=wx.TE_MULTILINE)
        # self.ctrl = ObjectListView(parent, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        fgs.Add(self.ctrl, -1, wx.EXPAND)

    def evaluate(self):

        for file in self.port.read():

            self.ctrl.write("File : " + file + "\n")

        # scroll to top
        self.ctrl.ShowPosition(0)


class TextControl(OutputControlBase):
    def __init__(self, parent, fgs, port):

        super().__init__(port, "TextControl(%s)" % port.name)

        self.port = port

        self.ctrl = wx.TextCtrl(parent, style=wx.TE_MULTILINE)
        # self.ctrl = ObjectListView(parent, wx.ID_ANY, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        fgs.Add(self.ctrl, -1)

        self.evaluate()

    def evaluate(self):

        # clear box
        self.ctrl.Clear()

        ##if len(np.array(self.port.read()).shape) > 1:
        if self.port.read()["data"][1]:

            for item in list(self.port.read()["data"][1]):

                self.ctrl.write("%f" % item + "\n")

        self.ctrl.ShowPosition(0)


class NumberControl(InputControlBase):
    def __init__(self, parent, fgs, target_port):

        super().__init__(target_port, "NumberControl(%s)" % target_port.name)

        # Take initial value from target port default
        self.value = target_port

        self.ctrl = wx.TextCtrl(
            parent,
            value=str(round(float(target_port.default), 2)),
            name=target_port.name,
            style=wx.TE_PROCESS_ENTER,
        )

        self.ctrl.name = target_port.name

        fgs.Add(self.ctrl, 1, wx.EXPAND)

        self.ctrl.Bind(wx.EVT_TEXT_ENTER, self.on_data)

    def on_data(self, evt):

        raw_value = self.ctrl.GetValue().strip()
        # numeric check
        if all(x in "0123456789.+-" for x in raw_value):
            # convert to float and limit to 2 decimals
            self.rounded = round(float(raw_value), 2)
            self.ctrl.ChangeValue(str(self.rounded))
        else:
            self.ctrl.ChangeValue("Number only")

        self.value.default = float(self.ctrl.GetValue())
        self.changed()

    def read(self):

        return self.value


class SliderControl1(InputControlBase):
    def __init__(self, parent, fgs, target_port):

        super().__init__(target_port, "SliderControl1(%s)" % target_port.name)

        # Take initial value from target port default
        self.value = target_port

        # check min and max values of the slider
        if np.array(target_port.input_stream.read()["data"][0]).ndim == 1:

            minvalue = min(target_port.input_stream.read()["data"][0])
            maxvalue = max(target_port.input_stream.read()["data"][0])

        if np.array(target_port.input_stream.read()["data"][0]).ndim == 2:

            minvalue = min(target_port.input_stream.read()["data"][0][0])
            maxvalue = max(target_port.input_stream.read()["data"][0][0])

        # initialise in centre
        midvalue = (minvalue + maxvalue) / 2

        # GUI Slider
        # value = int(self.value.default),
        # self.ctrl = wx.Slider(parent, value = self.value, minValue=self.port.min, maxValue=self.port.max, name = port.name, style = wx.SL_AUTOTICKS | wx.SL_VALUE_LABEL| wx.SL_MIN_MAX_LABELS)# | wx.SL_SELRANGE
        self.ctrl = wx.Slider(
            parent,
            minValue=int(minvalue),
            maxValue=int(maxvalue),
            name=target_port.name,
            style=wx.SL_AUTOTICKS | wx.SL_VALUE_LABEL | wx.SL_MIN_MAX_LABELS,
        )  # | wx.SL_SELRANGE

        # self.ctrl.name = self.port.name
        self.ctrl.name = target_port.name
        fgs.Add(self.ctrl, 1, wx.EXPAND)

        self.ctrl.Bind(wx.EVT_SCROLL_CHANGED, self.on_scrolled)

    def on_scrolled(self, evt):

        obj = evt.GetEventObject()
        self.value.default = obj.GetValue()
        self.changed()

    def read(self):

        return self.value


class SliderControl2(InputControlBase):
    def __init__(self, parent, fgs, target_port):

        super().__init__(target_port, "SliderControl1(%s)" % target_port.name)

        # Take initial value from target port default
        self.value = target_port

        # GUI Slider
        # self.ctrl = wx.Slider(parent, value = self.value, minValue=self.port.min, maxValue=self.port.max, name = port.name, style = wx.SL_AUTOTICKS | wx.SL_VALUE_LABEL| wx.SL_MIN_MAX_LABELS)# | wx.SL_SELRANGE
        self.ctrl = wx.Slider(
            parent,
            minValue=target_port.min,
            maxValue=target_port.max,
            name=target_port.name,
            style=wx.SL_AUTOTICKS | wx.SL_VALUE_LABEL | wx.SL_MIN_MAX_LABELS,
        )  # | wx.SL_SELRANGE

        # self.ctrl.name = self.port.name
        self.ctrl.name = target_port.name
        fgs.Add(self.ctrl, 1, wx.EXPAND)

        self.ctrl.Bind(wx.EVT_SCROLL_CHANGED, self.on_scrolled)

    def on_scrolled(self, evt):

        obj = evt.GetEventObject()
        self.value.default = obj.GetValue()
        self.changed()

    def read(self):

        return self.value


class ChoiceControl(InputControlBase):
    def __init__(self, parent, fgs, target_port):

        super().__init__(target_port, "ChoiceControl(%s)" % target_port.name)

        # Take initial value from target port default
        self.value = target_port

        # GUI Slider
        # self.ctrl = wx.Slider(parent, value = self.value, minValue=self.port.min, maxValue=self.port.max, name = port.name, style = wx.SL_AUTOTICKS | wx.SL_VALUE_LABEL| wx.SL_MIN_MAX_LABELS)# | wx.SL_SELRANGE
        self.ctrl = wx.Choice(parent, choices=target_port.choices)
        self.ctrl.SetSelection(0)

        # self.ctrl.name = self.port.name
        self.ctrl.name = target_port.name
        fgs.Add(self.ctrl, 1, wx.EXPAND)

        self.ctrl.Bind(wx.EVT_CHOICE, self.on_picked)

    def on_picked(self, evt):

        choice = self.ctrl.GetStringSelection()
        self.value.default = choice
        self.changed()

    def read(self):

        return self.value


class CheckControl(InputControlBase):
    def __init__(self, parent, fgs, target_port):

        super().__init__(target_port, "CheckControl(%s)" % target_port.name)

        self.port = target_port
        self.func = func

        # print(self.port.max)

        self.ctrl = wx.CheckBox(parent, name=target_port.name)
        self.ctrl.name = self.target_port.name

        fgs.Add(self.ctrl, 1, wx.EXPAND)

        self.ctrl.Bind(wx.EVT_CHECKBOX, self.on_checked)

    def on_checked(self, evt):

        self.state = evt.IsChecked()
        self.changed()

    def read(self):

        return self.state


class Equation_display:
    def __init__(self, parent, fgs, port):

        self.fig = Figure((2, 0.5), 75)

        self.canvas = FigureCanvas(parent, -1, self.fig)

        self.fig.text(0.05, 0.5, "$%s$" % port.name, size=10)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.canvas.draw()

        sizer.Add(self.canvas, 7, wx.ALIGN_CENTRE | wx.LEFT)

        fgs.Add(sizer, 0, wx.TOP | wx.EXPAND)

class GridControl(InputControlBase):

    def __init__(self, parent, fgs, target_port):
    
        super().__init__(target_port, "GridControl(%s)" % target_port.name)
    
        self.target_port = target_port
        
        
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        # print(self.port.max)

        self.ctrl = wx.grid.Grid(parent, name = target_port.name)
        self.ctrl.name = self.target_port.name
        self.ctrl.CreateGrid(10,  len(target_port.headers_titles))

        #self.ctrl.GetColSizes()
       
        self.ctrl.SetDefaultRowSize(30)
        self.ctrl.SetDefaultColSize(250)

        #types of cell attr
        choice_attr = wx.grid.GridCellAttr()
        num_attr = wx.grid.GridCellAttr()
        num_attr.SetEditor(wx.grid.GridCellFloatEditor())
        num_attr.SetRenderer(wx.grid.GridCellFloatRenderer())


        #iterate through headers
        for i in range(len(target_port.headers_titles)):
            self.ctrl.SetColLabelValue(i, target_port.headers_titles[i])
            if target_port.col_input_type[i] == "number":
                self.ctrl.SetColAttr(i,num_attr)
            elif target_port.col_input_type[i] == "choice":
                choice_attr.SetEditor(wx.grid.GridCellChoiceEditor(target_port.choices))
                self.ctrl.SetColAttr(i,choice_attr)

        
        #sizer.Add(panel, 1, wx.EXPAND)
        
        fgs.Add(self.ctrl , 1, wx.EXPAND)

        

        self.ctrl.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_value)



    def on_value(self, evt):
    
        col = evt.GetCol()
        row = evt.GetRow()
        print("changed")
        #put data into grid object
        self.target_port.grid[row][col] = self.ctrl.GetCellValue(row,col)
        
        self.changed()

    def read(self):

        return self.target_port
class PortControl:
    def __init__(self, parent, fgs, port, func, aui_notebook, manager, app):

        self.port = port

        # self.label = Equation_display(parent, fgs, port)
        # self.label = fgs.Add(label)
        self.label = fgs.Add(wx.StaticText(parent, label=port.name))

        if isinstance(port, FilePathInput):
            self.io = FileChooser(parent, fgs, port)

        elif isinstance(port, DirPathInput):
            self.io = DirChooser(parent, fgs, port)

        elif isinstance(port, StreamOutput):
            self.io = DictControl(parent, fgs, port)

        elif isinstance(port, ArrayOutput):
            self.io = MinimalPlotControl(parent, fgs, port, aui_notebook, manager, app)

        elif isinstance(port, TextOutput):
            self.io = TextControl(parent, fgs, port)

        elif isinstance(port, StreamInput):
            self.io = DictControl(parent, fgs, port)

        elif isinstance(port, int_input):
            self.io = SliderControl1(
                parent, fgs, port
            )  # dont think func needs to be passed.

        elif isinstance(port, num_input):
            self.io = NumberControl(parent, fgs, port)

        elif isinstance(port, free_int_input):
            self.io = SliderControl2(parent, fgs, port)

        elif isinstance(port, choice_input):
            self.io = ChoiceControl(parent, fgs, port)

        elif isinstance(port, bool_input):
            self.io = CheckControl(parent, fgs, port)

        elif isinstance(port, GridInput):
            self.io = GridControl(parent, fgs, port)

        elif isinstance(port, func_Output):
            print("No Implementation for func_Output")

        elif isinstance(port, MuxInput):
            print("No Implementation for MuxInput")

        else:
            self.io = fgs.Add(
                wx.StaticText(parent, label="unsupported type"), 1, wx.EXPAND
            )

        # dictionary contaning all io ports to be used for drag and drop reference
        app.io_dictionary[self.port] = self.io

class FuncCtrl(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, aui_notebook, func, manager, app, name):
        self.name = name
        wx.lib.scrolledpanel.ScrolledPanel.__init__(
            self, parent=aui_notebook
        )  # panel sits in __auinotebook
        self.func = func
        self.manager = manager
        # self.control_panel = wx.lib.scrolledpanel.ScrolledPanel(self,-1, size=(600,400), pos=(0,28), style=wx.SIMPLE_BORDER)

        # scrolled window
        self.SetupScrolling()

        # Sizers
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.fgs = wx.FlexGridSizer(20, 2, 10, 10)

        # print("FuncCtrl " + func.name)
        for port in func.inputs:
            if port.edges:

                continue  # skip input ports with a edge already attached
            # print("Port in : " + port.name)

            PortControl(self, self.fgs, port, func, aui_notebook, manager, app)

        for port in func.outputs:
            # print("Port out : " + port.name)

            PortControl(self, self.fgs, port, func, aui_notebook, manager, app)

        # fgs.AddGrowableRow(2, 1)
        self.fgs.AddGrowableCol(1, 1)

        hbox.Add(self.fgs, proportion=2, flag=wx.ALL | wx.EXPAND, border=15)
        
        self.SetSizer(hbox)
        print("size" + str(hbox.GetSize()))
        print("size" + str(self.fgs.GetSize()))

    def add_node(parent_node, fn):
        if isinstance(fn, Compositefn):
            """this has children"""
            for subfn in fn.subfuns:
                print(" hi")


class CtrlFrame(wx.Frame):
    def __init__(
        self,
        parent=None
    ):

        wx.Frame.__init__(
            self, parent=None, size=(1400, 700), id=wx.ID_ANY, title="Percolate"
        )
        
        #create a dictionary so Aui manager has a reference to all notebooks and function trees.
        self.function_control = dict()
        
    
        self.Show()


class MyApp(wx.App):
    def OnInit(self):

        # Build the GUI
        self.Main_Frame_Adapter()
        return True
    #what does this do rename 
    def Main_Frame_Adapter(self):

        # dictionary of arrays to plot on maxplot.
        self._dict = dict()
        self._dict1 = dict()

        self.canvas_dict = dict()

        self.tab_reference = dict()
        self.dt_dictionary = dict()
        self.io_dictionary = dict()

        # create frame
        self.main_frame = CtrlFrame(None)


        # create aui manager
        self.__auiManager = aui.AuiManager()
        self.__auiManager.SetManagedWindow(self.main_frame)

        # create menubar
        self.main_frame.menubar = wx.MenuBar()

        #fetch funcitons from Function directory
        self.main_frame.functionMenu = wx.Menu()
        for file in package_contents("percolate/Functions"):
            self.main_frame.functionMenu.Append(wx.ID_ANY, file)

        #canvas for plotting
        self.main_frame.PlotMenu = wx.Menu()
        self.main_frame.PlotMenu.Append(wx.ID_ANY, "Canvas")

        # create menu hierarchy
        self.main_frame.menubar.Append(self.main_frame.functionMenu, "&Load Function")
        self.main_frame.menubar.Append(self.main_frame.PlotMenu, "Plot")

        #add to menubar
        self.main_frame.SetMenuBar(self.main_frame.menubar)

        #create a function control for the func ctrl trees to sit
        self.main_frame.function_control["Function Ctrl"] = aui.AuiNotebook(self.main_frame)
        self.main_frame.function_control["Function Ctrl"].SetAGWWindowStyleFlag(
            aui.AUI_NB_SCROLL_BUTTONS
            | aui.AUI_NB_TAB_MOVE
            |aui.AUI_NB_TAB_EXTERNAL_MOVE   
        )

        # create aui notebook
        self.main_frame.function_control["Function view"] = aui.AuiNotebook(self.main_frame)
        self.main_frame.function_control["Function view"].SetAGWWindowStyleFlag(
            aui.AUI_NB_WINDOWLIST_BUTTON
            | aui.AUI_NB_SCROLL_BUTTONS
            | aui.AUI_NB_TAB_EXTERNAL_MOVE
            | aui.AUI_NB_TAB_MOVE
            | aui.AUI_NB_TAB_SPLIT
            | aui.AUI_NB_TAB_EXTERNAL_MOVE
        )

        self.__auiManager.AddPane(
            self.main_frame.function_control["Function Ctrl"],
            aui.AuiPaneInfo()
            .Name("Function Ctrl")
            .Caption("Function Ctrl")
            .Left()
            .CloseButton(False)
            .MinSize(180,180),
        )

        # add panes to the manager to sort out display
        self.__auiManager.AddPane(
            self.main_frame.function_control["Function view"],
            aui.AuiPaneInfo()
            .Name("Function view")
            .Caption("Function view")
            .Center()
            .CloseButton(False)
            .MinSize(400,400),
        )

        # update to let the manager know about changes
        self.__auiManager.Update()

        # Bind handlers to controls
        self.main_frame.Bind(wx.EVT_CLOSE, self.WindowOnClose)
        self.main_frame.functionMenu.Bind(wx.EVT_MENU, self.on_func_select)
        #self.Bind(wx.EVT_MENU, self.on_func_select)
        
        self.main_frame.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_clicked)

        self.main_frame.PlotMenu.Bind(wx.EVT_MENU, self.On_Create_MaxPlot)

        self.__auiManager.Bind(aui.EVT_AUI_PANE_CLOSE, self.on_pane_close)
        self.main_frame.function_control["Function view"].Bind(
            aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_tab_close
        )

        # self.__auiManager.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on__close)
        self.func =None
        self.count = 0
        self.addedtabs = dict()

    def setup_function(self, application, functionname):  

        
        #import selected function dynamically
        path = importlib.import_module('.%s'% functionname, 'percolate.Functions')
        application.func = path.function
        
        application.main_frame.function_control_tree = wx.TreeCtrl(application.main_frame)

        application.main_frame.function_control["Function Ctrl"].AddPage(
                application.main_frame.function_control_tree,
                caption=application.func.name,
        )

        # repopulate tree with subfunctions
        control_root = application.main_frame.function_control_tree.AddRoot(
            application.func.name, data=application.func
        )
        application.create_controls(application.func, control_root)
        
        if self.__auiManager.GetPane(application.func.name).IsOk():   
        
            print("Function with this name already exists")
            
        
        else:
            if self.__auiManager.GetPane("Function view").IsOk():

                self.__auiManager.GetPane("Function view").caption = application.func.name
                self.__auiManager.GetPane("Function view").name = application.func.name
                application.main_frame.function_control = application.main_frame.function_control["Function view"]

        
            # Open first element
            if isinstance(application.func, CompositeFn):
                addedtab = FuncCtrl(
                    application.main_frame.function_control,
                    application.func.subfns[0],
                    self.__auiManager,
                    application,
                    application.func.subfns[0].name,
                )

                application.addedtabs[application.func.subfns[0].name] = addedtab
                # add the tab with event id as name
                application.main_frame.function_control.AddPage(
                    application.addedtabs[application.func.subfns[0].name],
                    caption=application.func.subfns[0].name,
                )
        self.__auiManager.Update()

        # create loop
        application.MainLoop()
        
    def on_func_select(self, evt):
        
        if self.func: #if function exists
            app = MyApp(False)
            self.setup_function(app, evt.GetEventObject().GetLabel(evt.GetId())[:-3])
            
        else:#if function new
            self.setup_function(self, evt.GetEventObject().GetLabel(evt.GetId())[:-3])

    def on_tab_close(self, evt):

        page_idx = evt.GetSelection()
        self.main_frame.__auiNotebook.RemovePage(page_idx)
        self.main_frame.__auiNotebook.DeletePage(page_idx)

    def on_pane_close(self, evt):
        del self.canvas_dict[evt.GetPane().name]

    def on_clicked(self, evt):

        item = evt.GetItem()

        # item data
        evt_data = self.main_frame.function_control_tree.GetItemData(item)
        evt_name = self.main_frame.function_control_tree.GetItemText(item)

        # FuncCtrl(parent, func)
        for key, value in self.addedtabs.items():

            if value.func == evt_data:
                
                print(evt_data)
                print("exists")
                return

        for key, item in self.addedtabs.items():

            if evt_name == key:

                evt_name = evt_name + "1"
        
        
        if self.__auiManager.GetPane(self.func.name).IsOk():
        
            self.addedtabs[evt_name] = FuncCtrl(
                self.main_frame.function_control,
                evt_data,
                self.__auiManager,
                self,
                evt_name,
            )
            
            tab = self.main_frame.function_control.AddPage(self.addedtabs[evt_name], caption=evt_name)

    def On_Create_MaxPlot(self, evt):

        # A count increment to ensure no duplicate panes
        self.count = self.count + 1

        id_selected = evt.GetId()

        # canvas0, canvas1, .....
        canvas_id = evt.GetEventObject().GetLabel(id_selected) + str(self.count)

        # Dictionary containing all maxplot windows!
        self.canvas_dict[canvas_id] = MaxPlotControl(
            self,
            canvas_id,
            self.main_frame.function_control,
            self.__auiManager,
            self,
        )

        self.__auiManager.AddPane(
            self.canvas_dict[canvas_id].panel,
            aui.AuiPaneInfo()
            .Name(canvas_id)
            .Caption(canvas_id)
            .MinSize(100, 100)
            .DestroyOnClose()
            .Float(),
        )

        self.__auiManager.Update()

    def lookup_port(self, path):
        print("function name " + self.func.name)
        port = self.func.resolve_path_to_port(path)

        return port

    def WindowOnClose(self, event):

        self.main_frame.Destroy()

    def create_controls(self, func, parent_node):
        """Create child nodes"""
        #    for input in func.inputs:

        if isinstance(func, CompositeFn):
            # this has children
            for subfn in func.subfns:

                if isinstance(subfn, CompositeFn):
                    # func has grandchildren
                    child = self.main_frame.function_control_tree.AppendItem(
                        parent_node, subfn.name, data=subfn
                    )

                    for item in subfn.subfns:
                        self.main_frame.function_control_tree.AppendItem(
                            child, item.name, data=item
                        )

                    # self.main_frame.tree_ctrl.AppendItem(node, subfn.name, data = subfn)

                else:
                    pass
                    self.main_frame.function_control_tree.AppendItem(
                        parent_node, subfn.name, data=subfn
                    )


def package_contents(package_name):

    module = importlib.__import__('percolate')
    files = []
    
    for module in os.listdir(module.__path__[0]+ "/Functions"):
        if module.startswith("_"):
            pass
        else:
            files.append(module)

    return files

def percolate():
    # call app
    app = MyApp(False)
    # create loop
    app.MainLoop()


if __name__ == "__main__":
    percolate()
