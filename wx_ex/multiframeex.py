#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
##

import wx
from wx import Panel
import matplotlib
from functools import partial

from wxmplot.baseframe import BaseFrame
from wxmplot.utils import MenuItem



# extend BaseFrame to support multiple named sub-panels.
#
class MultiFrameEx(BaseFrame):
    """
    2D grid of PlotPanels
    """
    default_panelopts = dict(labelfontsize=7, legendfontsize=6)

    def __init__(self, parent=None, rows=1, cols=1, framesize=None, panelsize=(400, 320), panelopts=None, **kws):

        kws['style'] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER

        BaseFrame.__init__(self, parent=parent, title  = '2D Plot Array Frame', size=framesize, **kws)

        if framesize is None:
            framesize = (panelsize[0]*cols, panelsize[1]*rows)
        self.framesize = framesize
        #self.multipanel = MultiPlotPanel(frame=self, rows=rows, cols=cols, panelsize=panelsize, panelopts=panelopts, **kws)
        self.panels = {}

    def Add(self, panel=None):
        self.panels[panel.name()] = panel
    
    def AddMany(self, panellist=None):
        for p in panellist:
            panel, *junk = p
            self.panels[panel.name()] = panel


    ####
    ## create GUI
    ####
    def BuildFrame(self):
        sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.BuildMenu()
        self.SetStatusWidths([-3, -1])
        self.SetStatusText('',0)
        self.SetSize(self.framesize)
        self.SetAutoLayout(True)
        self.SetSizerAndFit(self._sizer)

    def BuildMenu(self):
        mfile = self.Build_FileMenu()
        mopts = wx.Menu()
        #MenuItem(self, mopts, "Configure Plot\tCtrl+K", "Configure Plot styles, colors, labels, etc", self.on_configure)
        #MenuItem(self, mopts, "Toggle Legend\tCtrl+L", "Toggle Legend Display", self.on_toggle_legend)
        #MenuItem(self, mopts, "Toggle Grid\tCtrl+G", "Toggle Grid Display", self.on_toggle_grid)

        mopts.AppendSeparator()

        MenuItem(self, mopts, "Zoom X and Y\tCtrl+W", "Zoom on both X and Y", partial(self.onZoomStyle, style='both x and y'), kind=wx.ITEM_RADIO, checked=True)
        MenuItem(self, mopts, "Zoom X Only\tCtrl+X", "Zoom X only", partial(self.onZoomStyle, style='x only'), kind=wx.ITEM_RADIO)

        MenuItem(self, mopts, "Zoom Y Only\tCtrl+Y", "Zoom Y only", partial(self.onZoomStyle, style='y only'), kind=wx.ITEM_RADIO)

        MenuItem(self, mopts, "Zoom Out\tCtrl+Z", "Zoom out to full data range", self.unzoom) 
        mopts.AppendSeparator()


        mhelp = wx.Menu()
        MenuItem(self, mhelp, "Quick Reference", "Quick Reference for WXMPlot", self.onHelp) 
        MenuItem(self, mhelp, "About", "About WXMPlot", self.onAbout)

        mbar = wx.MenuBar()
        mbar.Append(mfile, 'File')
        mbar.Append(mopts, '&Options')
        if self.user_menus is not None:
            for title, menu in self.user_menus:
                mbar.Append(menu, title)

        mbar.Append(mhelp, '&Help')

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_CLOSE,self.onExit)

    #def on_configure(self, event=None, **kws):
    #    self.multipanel.on_configure(event=event, **kws)

    #def on_toggle_legend(self, event=None, **kws):
    #    self.multipanel.on_toggle_legend(event=event, **kws)

    #def on_toggle_grid(self, event=None, **kws):
    #    self.multipanel.on_toggle_grid(event=event, **kws)

    #def on_unzoom(self, event=None, **kws):
    #    self.multipanel.on_unzoom(event=event, **kws)

    def report_leftdown(self, event=None, panelkey=None,**kw):
        self.multipanel.report_leftdown(event=event, panelkey=panelkey, **kw)



class BoxFrameEx(MultiFrameEx):

    def __init__(self, parent=None, orient=wx.VERTICAL, framesize=None, panelsize=(400, 320), panelopts=None, **kws):

        super(BoxFrameEx, self).__init__(parent=parent, framesize=framesize, panelsize=panelsize, panelopts=panelopts, **kws)
        self._sizer = wx.BoxSizer(orient=orient)
        #self.BuildFrame()
###
    def Add(self, panel=None, proportion=1):
        super(BoxFrameEx, self).Add(panel)
        self._sizer.Add(panel, proportion=proportion)

    def AddMany(self, panellist=None):
        super(BoxFrameEx, self).AddMany(panellist)
        self._sizer.AddMany(panellist)

class GridBagFrameEx(MultiFrameEx):

    def __init__(self, parent=None, rows=1, cols=1, framesize=None, panelsize=(400, 320), panelopts=None, **kws):

        super(GridBagFrameEx, self).__init__(parent=parent, rows=rows, cols=cols, framesize=framesize, panelsize=panelsize, panelopts=panelopts, **kws)
        self._sizer = wx.GridBagSizer(3, 3)
        #self.BuildFrame()
###
    def Add(self, panel=None, loc=(0,0), span=(1,1)):
        super(GridBagFrameEx, self).Add(panel)
        row, col = pos
        self.sizer.Add(panel, pos, span)
        self.sizer.AddGrowableRow(row)
        self.sizer.AddGrowableCol(col)

    def AddMany(self, panellist=None, grow=(1,1)):
        super(GridBagFrameEx, self).AddMany(panellist)
        self._sizer.AddMany(panellist)
        row, col = grow
        for r in row:
            self.sizer.AddGrowableRow(row)
        for c in col:
            self.sizer.AddGrowableCol(col)

