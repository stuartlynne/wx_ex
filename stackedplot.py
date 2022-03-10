#!/usr/bin/python
#
# Stacked Plot shows two related plots stacked top and bottom that are
# expected to share an X axis.

# The upper panel is a standard PlotPanel. The bottom panel is compressed
# in height, and follows the X-range when zooming the top panel, and does
# not respond to most other mouse events.

import wx
import numpy
from wx_ex.stackedframeex import StackedPlotFrameEx

x = numpy.arange(0.0, 30.0, 0.1)

noise = numpy.random.normal(size=len(x), scale=0.096)

y1 = numpy.sin(2*x)/(x+2)
y2 = numpy.sin(2*x)/(x+1)
y2_ = y1 + noise

app = wx.App()

pframe = StackedPlotFrameEx(title='Stacked Example', ratio=3.000)

pframe.plot(x, y2, label='data(fake)', ylabel='signal', xlabel='x', title='some fit')
pframe.oplot(x, y1, label='simple theory', show_legend=True)

#pframe.plot(x, noise, panel='bottom', ylabel='residual')
pframe.plot(x, y2, panel='bottom', ylabel='residual')
pframe.oplot(x, y1, panel='bottom', label='simple theory', show_legend=True)


pframe.Show()
pframe.Raise()

pframe.write_message('test')

app.MainLoop()
