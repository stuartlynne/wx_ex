#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
import sys
import time
import numpy as np
import sys
import wx
from wx.lib import masked
from floatcontrol import FloatCtrl
from wxmplot import BaseFrame
from wxmplot import PlotPanel
from wx_ex.plotpanelex import PlotPanelEx
from wx_ex.stackedpanelex import StackedPlotPanelEx
from wx_ex.plotpanelex import MultiPlotPanelEx
from wx_ex.plotpanelex import PlotPanelEx
from wx_ex.multiframe import MultiPlotFrame
from wx_ex.multiframeex import MultiFrameEx
#from wx_ex.trainerframeex import TrainerRowFrameEx
import matplotlib

import wx.lib.inspection


# Set the YMULTIPLER=1 to see the only the bottom two rows of the pcolormesh.
# Set the YMULTIPLER=10 to see the only the a more complete mesh.

# N.B. The pcolormesh does not get shown for any portion of the plot below zero.

YMULTIPLIER=1
#YMULTIPLIER=10

class TestXY:

    x   = np.linspace(0.0, 10.0, 201)
    y1  = np.sin(3*x)/(x+2)


# StatPlot - mini plot for displaying minimal plot and most recent value for
# a device statistic, e.g. power, alpha1, heart rate etc.
#
class StatPlot(PlotPanelEx):

    def __init__(self, parent, name=None, size=wx.DefaultSize, show_axes=True, show_legend=False, build_panel=True, fontsize=4, axesmargins=(1,1,1,1), **kws):

        print('StatPlot::__init__ name: %s size: %s, kws: %s' % (name, size, kws), file=sys.stderr)
        super(StatPlot, self).__init__(parent, name=name, size=size, **kws)

        #x   = np.linspace(0.0, 10.0, 201)
        #y1  = np.sin(3*x)/(x+2)
        x = TestXY.x
        y1 = TestXY.y1

        label1 = name.replace(' ', '\n')

        label2 = '%4.0f' % (123)
        self.plot(x, y1, show_legend=False, labelfontsize=5, legend_loc='upper right', legendfontsize='x-small', marker='no symbol', marksize=0)
        self.axes.tick_params(length=1, direction='in', bottom=False, left=False, labelbottom=False, labelleft=False)
        #self.axes.set_facecolor('lightgreen')

        self.axes.annotate(label1, xy=(0,0), xytext=(.12,.12), textcoords='figure fraction', fontsize=fontsize, horizontalalignment='left', verticalalignment='bottom')
        self.axes.annotate(label2, xy=(0,0), xytext=(.95,.93), textcoords='figure fraction', fontsize=fontsize+2, horizontalalignment='right', verticalalignment='top')
        self._name = name

# StackedStatPlots - two large plots to show higher resolution plots for multiple statistics,
# divided into top and bottom, share common X
#
class StackedStatPlots(StackedPlotPanelEx):

    def __init__(self, parent, name=None, size=wx.DefaultSize, show_axes=True, show_legend=False, build_panel=True, fontsize=4, axesmargins=(1,1,1,1), **kws):
        print('StackedStatPlots::__init__ name: %s size: %s, kws: %s' % (name, size, kws), file=sys.stderr)
        super(StackedStatPlots, self).__init__(parent, name=name, size=size, **kws)

        self.axesmargins = (1, 1, 1, 1)

        x = np.arange(0.0, 30.0, 0.1)

        noise = np.random.normal(size=len(x), scale=0.096)

        y1 = np.sin(2*x)/(x+2)
        y2 = np.sin(2*x)/(x+1)
        y2_ = y1 + noise

        self.plot(x, y2, label='data(fake)', ylabel=None, xlabel=None, title=None)
        self.oplot(x, y1, label='simple theory', show_legend=True)

        self.plot(x, y2, panel='bottom', ylabel=None)
        self.oplot(x, y1, panel='bottom', label='simple theory', show_legend=True)


# StaticBoxPlots - a static box to hold the device multiple statplot panels, this
# provides the grouping, draws a rectangle around them and puts a label at top left.
class StaticBoxPlots(wx.Panel):
    def __init__(self, parent, panels, name='', size=wx.DefaultSize, messenger=None):
        wx.Panel.__init__(self, parent, -1)
        self.panels = panels
        xmax = ymax = 0
        cols = int((len(panels)+1)/2)
        xmax = [0,0]
        ymax = [0,0]
        print('StaticBoxPlots::__init__ stats: %d cols: %d' % (len(panels), cols), file=sys.stderr)
        for i, p in enumerate(panels):
            row = int(i // cols)
            x,y = p.GetSize()
            if y > ymax[row]: ymax[row] = y
            xmax[row] += x
            print('TestBoxPlot::__init__[%d] row: %d x: %d y: %d xmax: %d ymax: %d' % (i, row, x, y, xmax[row], ymax[row]),file=sys.stderr)

        xmax = max(xmax)
        ymax = sum(ymax)

        self.messengner=messenger

        # Create static box and it's gridbag sizer to contain the sub panels
        self.static_box = wx.StaticBox(self, id=wx.ID_ANY, label=f" {name} ", size=(xmax+10,ymax+15))
        self.static_box.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.static_box_sizer = wx.GridBagSizer(0, 0)
        self.static_box.SetSizer(self.static_box_sizer)

        # Create a boxsizer for this panel, add static_box to it 
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.static_box, 1, wx.TOP|wx.EXPAND|wx.FIXED_MINSIZE|wx.ALL, border=0)
        self.SetSizer(self.sizer)

        # Reparent each panel with the static box and add to the static box sizer.
        # This is required to get layout and painting correct.
        for i, p in enumerate(panels):
            row = int(i // cols)
            col = int(i % cols)
            p.Reparent(self.static_box)
            print('TestBoxPlot::__init__[%d] pos(%d,%d)' % (i, row, col),file=sys.stderr)
            self.static_box_sizer.Add(p, pos=(row,col), span=(1,1), flag=wx.EXPAND|wx.FIXED_MINSIZE, border=0)

    def Destroy(self):
        print('StaticBoxPlots::Destroy', file=sys.stderr)

        # For each panel we need to detach from the static_box gridbag sizer and destroy
        for p in self.panels:
            print('StaticBoxPlots::Destroy detach %s panel: %s' % (p._name, p), file=sys.stderr)
            self.static_box_sizer.Detach(p)
            #p.Destroy()
        self.static_box_sizer.Detach(self.static_box_sizer)
        self.sizer.Detach(self.static_box)
        self.static_box.Destroy()
        del self.panels
        del self.static_box
        self.Layout()


# DevicePanel - This holds a group of statistic plots for a device. This is shown
# in a labeled static box.
#
class DevicePanel(MultiPlotPanelEx):

    def __init__(self, parent, name=None, statlist=None, messenger=None):
        print('DevicePanel::__init__ %s statlist: %s' % (name, statlist), file=sys.stderr)
        super(DevicePanel, self).__init__(parent=parent, name=name, style=wx.BORDER_NONE )

        print('DevicePanel::__init__ self._name: %s' % (self._name), file=sys.stderr)

        self.sizer = wx.BoxSizer(orient=wx.VERTICAL)

        plots = [ StatPlot(self, name=s, size=(125,100), fontsize=8, show_legend=True, messenger=messenger) for s in statlist]
        self.add_panels(plots)
        self.static_box = StaticBoxPlots(self, panels=plots, name=name, messenger=messenger, )
        self.sizer.Add(self.static_box, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND, border=0)

        #sbox = wx.StaticBox(parent, id=wx.ID_ANY, label=label)
        #sbox.SetSizer(sizer)
        #sizer = wx.BoxSizer(orient=wx.VERTICAL)
        #sizer.Add(sbox, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND, border=10)
        self.SetSizer(self.sizer)

        #statsizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        #for i in range(3):
        #    self.add_plot(panels=self.panels, name=f"{name}-{i}", sizer=statsizer, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND)
        #sizer.Add(statsizer, proportion=3, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND)
        self.Layout()
        self.Update()

    def Destroy(self):
        print('DevicePanel::Destroy %s panels: %s' % (self._name, self.panels), file=sys.stderr)

        self.sizer.Detach(self.static_box)
        self.static_box.Destroy()
        #for k, v in self.panels.items():
        #    print('DevicePanel::Destroy panel: %s' % (k), file=sys.stderr)
        #    print('DevicePanel::Destroy %s panel: %s' % (v._name, v), file=sys.stderr)
        #    v.Destroy()
        pass

class HRMDevice(DevicePanel):
    def __init__(self, parent, name='', messenger=None):
        super(HRMDevice, self).__init__(parent, name=name, statlist=["alpha1", "rmssd", "Heart Rate (bpm)", "ssdn", "Heart Rate (avg)", "lnrmssd"], messenger=messenger)

class PMDevice(DevicePanel):
    def __init__(self, parent, name='', messenger=None):
        super(PMDevice, self).__init__(parent, name=name, statlist=["Power (W)", "Power (NP)", "Power (AP)", "TSS", "Cadence (RPM)", ], messenger=messenger)

class FECDevice(DevicePanel):
    def __init__(self, parent, name='', messenger=None):
        super(FECDevice, self).__init__(parent, name=name, statlist=["Power (W)", "Power (NP)", "Power (AP)", "TSS", "Cadence (RPM)",], messenger=messenger)


#class RxFail(MultiPlotPanelEx):
#    def __init__(self, parent, name=None):
#        super(RxFail, self).__init__(parent=parent, name=name, )
#        self.panels = []
#        sizer = wx.BoxSizer(orient=wx.HORIZONTAL)
#        sizer.SetMinSize(100,20)
#
#        self.barLabel1 = wx.StaticText(self,wx.ID_ANY|wx.BORDER_NONE|wx.ALIGN_BOTTOM, '1234', size=(60,20))
#        self.barLabel2 = wx.StaticText(self,wx.ID_ANY|wx.BORDER_NONE|wx.ALIGN_BOTTOM, '5678\nabcd', size=(40,20))
#        self.barLabel1.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
#        self.barLabel2.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
#        self.bars1 = TestPlot(self, name=f"{name} RxFail", show_axes=False, show_legend=False, size=(100,20), messenger=self.write_message)
#        self.panels.append(self.bars1)
#        sizer.Add(self.barLabel1, flag=wx.ALIGN_LEFT|wx.EXPAND|wx.ALIGN_BOTTOM|wx.FIXED_MINSIZE, proportion=1, )
#        sizer.Add(self.bars1, flag=wx.EXPAND|wx.ALL, proportion=4, )
#        sizer.Add(self.barLabel2, flag=wx.ALIGN_RIGHT|wx.EXPAND|wx.FIXED_MINSIZE, proportion=1, )
#
#        self.SetSizer(sizer)
#        self.Layout()
#        self.Update()

#    def add_bar(self, panels=None, name=None, sizer=None, size=(150,100), **args):
#        print('DevicePanel::add_plot: %s args: %s' % (name, args), file=sys.stderr)
#        panel = TestBar(self, name=name)
#        panels.append(panel)
#        sizer.Add(panel, **args)

#    def add_plot(self, panels=None, name=None, sizer=None, size=(150,100), **args):
#        print('DevicePanel::add_plot: %s args: %s' % (name, args), file=sys.stderr)
#        panel = TestPlot(self, name=name, size=size, messenger=self.write_message)
#        panels.append(panel)
#        sizer.Add(panel, **args)

#    def add_box(self, panels=None, name=None, sizer=None, size=(150,100), **args):
#        print('DevicePanel::add_box: %s args: %s' % (name, args), file=sys.stderr)
#        panel = TestStaticBoxPlots(self, label=name, name=name, size=size)
#        panels.append(panel)
#        sizer.Add(panel, **args)

#class PlotsWrap(MultiPlotPanelEx):
#    def __init__(self, parent, name=None):
#        super(PlotsWrap, self).__init__(parent=parent, name=name, )
#        self.panels = []
#        sizer = wx.WrapSizer(orient=wx.HORIZONTAL)
#        self.SetSizer(sizer)
#        for i in range(6):
#            self.add_plot(panels=self.panels, name=f"{name}-{i}", sizer=sizer, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND)
#        self.Layout()
#        self.Update()
#
#    def add_plot(self, panels=None, name=None, sizer=None, **args):
#        print('PlotsWrap::add_plot: %s args: %s' % (name, args), file=sys.stderr)
#        panel = TestPlot(self, name=name, messenger=self.write_message)
#        panels.append(panel)
#        sizer.Add(panel, **args)

class TestFrame(MultiFrameEx):

    def __init__(self, parent, ID, **kws):

        print("TestFrame::__init__ kws=%s" % (kws), file=sys.stderr)
        kws["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL

        size = (1000,800)
        #super(TestFrame, self).__init__(self, parent, ID, '', wx.DefaultPosition, size, **kws)
        #super(TestFrame, self).__init__(self, parent, '', wx.DefaultPosition, size, **kws)
        self.framesize = size
        super(TestFrame, self).__init__(parent=parent, title  = '2D Plot Array Frame', framesize=size, **kws)

        self.BuildFrame()

    def BuildFrame(self):
        #sbar_widths = [-2, -1, -1]
        #sbar = self.CreateStatusBar(len(sbar_widths), wx.CAPTION)
        #sfont = sbar.GetFont()
        #sfont.SetWeight(wx.BOLD)
        #sfont.SetPointSize(10)
        #sbar.SetFont(sfont)
        #self.SetStatusWidths(sbar_widths)

        #sizer = wx.BoxSizer(wx.VERTICAL)
        panelkws = self.panelkws
        if self.size is not None:
            panelkws.update({'size': self.size})
        panelkws.update({'output_title': self.output_title,
                         'with_data_process': self.with_data_process,
                         'theme': self.theme})

        #self.panel = PlotPanel(self, **panelkws)
        # self.toolbar = NavigationToolbar(self.panel.canvas)
        #self.panel.messenger = self.write_message
        #sizer.Add(self.panel, 1, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSize(self.GetBestVirtualSize())

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.row1_panels = []
        self.row1_count = self.row2_count = 0
        self.row1_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.row1_sizer, proportion=2, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.ALIGN_CENTER|wx.EXPAND, border=0)

        self.row2_panels = []
        self.row2_sizer = wx.WrapSizer(orient=wx.HORIZONTAL)
        self.main_sizer.Add(self.row2_sizer, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER|wx.EXPAND, border=5)


        self.SetSizer(self.main_sizer)
        #self.row1_add_plot()
        self.panel = StackedStatPlots(self, name='Trainer', size=(500,500), fontsize=20, messenger=self.write_message)
        self.panel.nstatusbar = self.sbar.GetFieldsCount()
        self.row1_panels.append(self.panel)
        self.row1_sizer.Add(self.panel, flag=wx.ALIGN_CENTER|wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM)
        self.row1_sizer.Layout()

        # XXX

        #self.plotpanel = PlotPanel(self, )
        #self.plotpanel.BuildPanel()
        #self.row1_sizer.Add(self.plotpanel, 1, wx.GROW|wx.ALL|wx.ALIGN_LEFT|wx.LEFT, 0)
        #self.row1_sizer.Fit(self)

        #self.row2_add_device_wrap()
        #self.row2_add_device_grid()
        #self.row2_add_plots_gridbag()
        #self.row2_add_plots_wrap()

        self.row2_add_devicepanel()

        #self.row2_add_devicepanel()
        #self.row2_add_plots_box()
        #self.row2_add_plots()
        #self.row2_add_twoplots()
        #self.row2_add_devicepanel()
        #self.row2_add_plot()

        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer = wx.Timer(self)
        self.count = 0
        self.Refresh()
        self.SetSize(self.GetBestVirtualSize())
        self.SetAutoLayout(True)
        self.SetMinSize((500,400))

        self.BuildMenu()
        wx.CallAfter(self.onStartTimer)

    def write_message(self, msg, panel=0):
        #print('TestFrame::write_message msg: %s panel: %s' % (msg, panel), file=sys.stderr)
        super(TestFrame, self).write_message(msg, panel)

    def row2_add_device(self, panel):
        self.row2_sizer.Add(panel, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND, border=5)
        self.row2_panels.append(panel)
        self.Layout()

    def row2_add_devicepanel(self):
        row = len(self.row2_panels) + 1
        #for i in range(1):
        #    name = f"HRM-123{row}{i}"
        #    panel = DevicePanel(self, name=name, statlist=["alpha1", "rmssd", "bpm", "ssdn", "bpm(avg)", "lnrmssd"])
        #    print('row2_add_plots_devicepanel: %s %d:%d' % (name, row,i), file=sys.stderr)
        #    #self.row2_sizer.Add(panel, pos=(row,i), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND, border=0)

        #self.row2_add_device(HRMDevice(self, name="HRM-12345", messenger=self.write_message))
        #self.row2_add_device(HRMDevice(self, name="HRM-67890", messenger=self.write_message))
        #self.row2_add_device(PMDevice(self, name="PM-17890", messenger=self.write_message))
        #self.row2_add_device(FECDevice(self, name="FEC-07399", messenger=self.write_message))
        self.Layout()
        self.Update()

    def row1_add_plot(self):
        self.row1_count +=1
        col = self.row1_count
        name = f"row1-plot-{col}"
        print('row1_add_plot: %s %d' % (name, col), file=sys.stderr)
        #panel = TestPlot(self, name=name, size=(500,500), fontsize=20)
        panel = StackedStatPlots(self, name=name, size=(500,500), fontsize=20, messenger=self.write_message)
        self.row1_panels.append(panel)
        self.row1_sizer.Add(panel, flag=wx.ALIGN_CENTER|wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM)
        self.row1_sizer.Layout()


    def row2_add_plot(self):
        self.row2_count +=1
        col = self.row2_count
        name = f"row2-plot-{col}"
        print('row2_add_plot: %s %d' % (name, col), file=sys.stderr)
        panel = StatPlot(self, name=name, size=(150,100), fontsize=6, messenger=self.write_message)
        self.row2_panels.append(panel)
        #self.row2_sizer.Add(panel, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.FIXED_MINSIZE)
        self.row2_sizer.Add(panel, flag=wx.ALIGN_CENTER|wx.FIXED_MINSIZE)
        self.Layout()

    def destroy_panel(self, sizer, panel):
        print('TestFrame::destroy_panel %s panel: %s' % (panel._name, panel), file=sys.stderr)
        sizer.Detach(panel)
        panel.Destroy()
        del panel
        self.Layout()

    def row2_del_zero(self):
        print('TestFrame::row2_del_zero *****************************************************************', file=sys.stderr)
        panel = self.row2_panels.pop(0)
        self.destroy_panel(self.row2_sizer, panel)






#    def row2_add_device_wrap(self):
#        row = len(self.row2_panels) + 1
#        name = f"row2-device-{row}"
#        print('row2_add_device_wrap: %s %d' % (name, row), file=sys.stderr)
#        plots = DeviceWrap(self, name=name)
#        self.row2_sizer.Add(plots, pos=(row,0), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.FIXED_MINSIZE, border=0)
#        self.row2_panels.append(plots)
#        self.Layout()
#        self.Update()

#    def row2_add_device_grid(self):
#        row = len(self.row2_panels) + 1
#        name = f"row2-device-{row}"
#        print('row2_add_device_grid: %s %d' % (name, row), file=sys.stderr)
#        plots = DeviceGridBag(self, name=name)
#        self.row2_sizer.Add(plots, pos=(row,0), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.FIXED_MINSIZE, border=0)
#        self.row2_panels.append(plots)
#        self.Layout()
#        self.Update()

#    def row2_add_plots_gridbag(self):
#        row = len(self.row2_panels) + 1
#        name = f"gb-{row}"
#        print('row2_add_plots_gridbag: %s %d' % (name, row), file=sys.stderr)
#        plots = PlotsGridBag(self, name=name)
#        self.row2_sizer.Add(plots, pos=(row,0), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND, border=0)
#        self.row2_panels.append(plots)
#        self.Layout()
#        self.Update()

#    def row2_add_plots_box(self):
#        row = len(self.row2_panels) + 1
#        name = f"box-{row}"
#        print('row2_add_plots_box: %s %d' % (name, row), file=sys.stderr)
#        plots = PlotsBox(self, name=name)
#        self.row2_sizer.Add(plots, pos=(row,0), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND, border=0)
#        self.row2_panels.append(plots)
#        self.Layout()
#        self.Update()

    def row2_add_plots_wrap(self):
        row = len(self.row2_panels) + 1
        name = f"wrap-{row}"
        print('row2_add_plots_wrap: %s %d' % (name, row), file=sys.stderr)
        plots = PlotsWrap(self, name=name)
        self.row2_sizer.Add(plots, flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.EXPAND, border=0)
        self.row2_panels.append(plots)
        self.Layout()
        self.Update()

#    def row2_add_twoplots(self):
#        row = len(self.row2_panels) + 1
#        name = f"row2-row-{row}"
#        sizer = wx.GridBagSizer(1,2)
#        self.add_plot(panels=self.row2_panels, name=f"{name}-0", sizer=sizer, pos=(0,0), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.FIXED_MINSIZE)
#        self.add_plot(panels=self.row2_panels, name=f"{name}-1", sizer=sizer, pos=(0,1), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.FIXED_MINSIZE)
#        self.row2_sizer.Add(sizer, pos=(row,0), span=(1,1), flag=wx.ALIGN_CENTER|wx.RESERVE_SPACE_EVEN_IF_HIDDEN|wx.FIXED_MINSIZE, border=0)
#        self.Layout()
#        self.Update()

    def doupdate(self):
        #self.row2_add_twoplots()
        self.Layout()
        self.Update()


    def onStartTimer(self,event=None):
        self.count    = 0
        #self.tlist = [t0]

        self.firstFlag = True
        self.tmin_last = -10000
        self.time0 = time.time()
        self.timer.Start(4000)
        self.ylist = []
        self.tlist = []
        for t in range(100):
            self.ylist.append(0.0)
            self.tlist.append(-100+t)

    def onStopTimer(self,event=None):
        self.timer.Stop()

    def cmap(self, list):
        map = []
        for l in list:
            map += [l[0] for i in range(l[1]) ]
        return len(map), map

    def onTimer(self, event):
        print('onTimer: count: %d' % (self.count), file=sys.stderr)
        self.count += 1
        if self.count % 20 in [2,16]:
            self.row2_add_device(HRMDevice(self, name="HRM-12345", messenger=self.write_message))

        if self.count % 20 in [4,17]:
            self.row2_add_device(HRMDevice(self, name="HRM-67890", messenger=self.write_message))

        if self.count % 20 in [6,15]:
            self.row2_add_device(PMDevice(self, name="PM-17890", messenger=self.write_message))

        if self.count % 20 in [8,17]:
            self.row2_add_device(FECDevice(self, name="FEC-07399", messenger=self.write_message))

        if self.count % 20 in [9, 11]:
            self.row2_del_zero()
            self.row2_del_zero()

        if self.count % 20 in [ 19]:
            self.row2_del_zero()
            self.row2_del_zero()
            self.row2_del_zero()
            self.row2_del_zero()


        #if self.count == 20:
        #    #self.row2_add_plot()
        #    #self.doupdate()
        #    self.timer.Stop()
        #    pass


app = wx.App()
f = TestFrame(None,-1)
#f.StartFrame()
f.Show(True)
#wx.lib.inspection.InspectionTool().Show()
#f.write_message('test')
app.MainLoop()
#
