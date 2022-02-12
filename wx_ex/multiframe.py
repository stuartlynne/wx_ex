#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
##

import wx
from wx import Panel
import matplotlib
from functools import partial

from wx_ex.multiplot import MultiPlotPanel
from wxmplot.plotpanel import PlotPanel
from wxmplot.baseframe import BaseFrame
from wxmplot.utils import MenuItem

class MultiPlotFrame(BaseFrame):
    """
    MatPlotlib Array of 2D plot as a wx.Frame, using PlotPanel
    """
    default_panelopts = dict(labelfontsize=7, legendfontsize=6)

    def __init__(self, parent=None, rows=1, cols=1, framesize=None, panelsize=(400, 320), panelopts=None, **kws):

        BaseFrame.__init__(self, parent=parent, title  = '2D Plot Array Frame', size=framesize, **kws)

        if framesize is None:
            framesize = (panelsize[0]*cols, panelsize[1]*rows)
        self.framesize = framesize
        self.current_panel = (0, 0)
        self.multipanel = MultiPlotPanel(frame=self, rows=rows, cols=cols, panelsize=panelsize, panelopts=panelopts, **kws)
        self.BuildFrame()

###
    def plot(self,x,y,panel=None,**kws):
        """plot after clearing current plot """
        self.multipanel.plot(x,y,panel=panel,**kws)

    def oplot(self,x,y,panel=None,**kws):
        """generic plotting method, overplotting any existing plot """
        self.multipanel.oplot(x,y,panel=panel,**kws)

    def update_line(self, t, x, y, panel=None, **kw):
        """overwrite data for trace t """
        self.multipanel.update_line(t,x,y,panel=panel,**kws)

    def set_xylims(self, lims, axes=None, panel=None):
        """overwrite data for trace t """
        self.multipanel.set_xylims(lime,axes=axes,panel=panel)

    def clear(self,panel=None):
        """clear plot """
        self.multipanel.clear(panel=panel)

    def unzoom_all(self,event=None,panel=None):
        """zoom out full data range """
        self.multipanel.clear(x,y,event=event,panel=panel)

    def unzoom(self, event=None, panel=None):
        """zoom out 1 level, or to full data range """
        self.multipanel.unzoom(event=event,panel=panel)

    def onZoomStyle(self, event=None, style='both x and y'):
        self.multipanel.onZoomStyle(event=event,style=style)

    def set_title(self,s,panel=None):
        "set plot title"
        self.multipanel.set_title(s,panel=panel)

    def set_xlabel(self,s,panel=None):
        "set plot xlabel"
        self.multipanel.set_xlabel(s,panel=panel)

    def set_ylabel(self,s,panel=None):
        "set plot ylabel"
        self.multipanel.set_ylabel(s,panel=panel)

    def save_figure(self,event=None,panel=None):
        """ save figure image to file"""
        self.multipanel.save_figure(event=event,panel=panel)

    def configure(self,event=None,panel=None):
        self.multipanel.configure(event=event,panel=panel)

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
        self.SetSizerAndFit(self.multipanel.sizer())

    def BuildMenu(self):
        mfile = self.Build_FileMenu()
        mopts = wx.Menu()
        MenuItem(self, mopts, "Configure Plot\tCtrl+K", "Configure Plot styles, colors, labels, etc", self.on_configure)
        MenuItem(self, mopts, "Toggle Legend\tCtrl+L", "Toggle Legend Display", self.on_toggle_legend)
        MenuItem(self, mopts, "Toggle Grid\tCtrl+G", "Toggle Grid Display", self.on_toggle_grid)

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

    def on_configure(self, event=None, **kws):
        self.multipanel.on_configure(event=event, **kws)

    def on_toggle_legend(self, event=None, **kws):
        self.multipanel.on_toggle_legend(event=event, **kws)

    def on_toggle_grid(self, event=None, **kws):
        self.multipanel.on_toggle_grid(event=event, **kws)

    def on_unzoom(self, event=None, **kws):
        self.multipanel.on_unzoom(event=event, **kws)

    def report_leftdown(self, event=None, panelkey=None,**kw):
        self.multipanel.report_leftdown(event=event, panelkey=panelkey, **kw)
