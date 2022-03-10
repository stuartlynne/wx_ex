#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## StackedPlotFrame: a wx.Frame for 2 PlotPanels, top and bottom
##   with the top panel being the main panel and the lower panel
##   being 1/4 the height (configurable) and the dependent panel

import wx
import numpy as np
import matplotlib
from matplotlib.ticker import NullFormatter, NullLocator
from functools import partial
from wx_ex.stackedpanelex import StackedPlotPanelEx
from wxmplot.utils import pack, MenuItem
from wxmplot.plotpanel import PlotPanel
from wxmplot.baseframe import BaseFrame



class StackedPlotFrameEx(BaseFrame):
    """
    Top/Bottom MatPlotlib panels in a single frame
    """
    def __init__(self, parent=None, title ='Stacked Plot Frame', framesize=(550,650), panelsize=(550,350), ratio=3.0, **kws):

        kws['style'] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER

        BaseFrame.__init__(self, parent=parent, title=title, size=framesize, **kws)

        self.ratio = ratio
        self.framesize = framesize
        self.panelsize = panelsize

        self.stackedpanel = StackedPlotPanelEx(parent=self, messenger=self.write_message, framesize=framesize, panelsize=panelsize, ratio=ratio, **kws)

        #self.panel = None
        #self.panel_bot = None
        #self.xlabel = None
        sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-3,-1])
        self.SetStatusText('',0)
        self.BuildFrame()

    def get_panel(self, panelname):
        return self.stackedpanel.get_panel(panelname)

    def plot(self, x, y, panel='top', xlabel=None, **kws):
        """plot after clearing current plot """
        self.stackedpanel.plot(x, y, panel=panel, xlabel=xlabel, **kws)

    def oplot(self, x, y, panel='top', xlabel=None, **kws):
        """plot method, overplotting any existing plot """
        self.stackedpanel.oplot(x, y, panel=panel, xlabel=xlabel, **kws)

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        self.stackedpanel.unzoom_all(event=event)

    def unzoom(self, event=None, panel='top'):
        """zoom out 1 level, or to full data range """
        self.stackedpanel.unzoom(event=event, panel=panel)

    def update_line(self, t, x, y, panel='top', **kws):
        """overwrite data for trace t """
        self.stackedpanel.update_line(t, x, y, panel=panel)

    def set_xylims(self, lims, axes=None, panel='top', **kws):
        """set xy limits"""
        self.stackedpanel.set_xylims(lims, axes=axes, panel=panel, **kws)

    def clear(self, panel='top'):
        """clear plot """
        self.stackedpanel.clear(panel=panel)

    def set_title(self,s, panel='top'):
        "set plot title"
        self.stackedpanel.set_title(s, panel=panel)

    def set_xlabel(self,s, panel='top'):
        "set plot xlabel"
        self.stackedpanel.set_xlabel(s, panel=panel)

    def set_ylabel(self,s, panel='top'):
        "set plot xlabel"
        self.stackedpanel.set_ylabel(s, panel=panel)

    def save_figure(self, event=None, panel='top'):
        """ save figure image to file"""
        self.stackedpanel.save_figure(event=event, panel=panel)

    def configure(self, event=None, panel='top'):
        self.stackedpanel.configure(event=event, panel=panel)

    ####
    ## create GUI
    ####
    def BuildFrame(self):
#        sbar = self.CreateStatusBar(2, wx.CAPTION)
#        sfont = sbar.GetFont()
#        sfont.SetWeight(wx.BOLD)
#        sfont.SetPointSize(10)
#        sbar.SetFont(sfont)
#
#        self.SetStatusWidths([-3,-1])
#        self.SetStatusText('',0)

        #pack(self, self.stackedpanel.sizer())
        #self.SetSize(self.GetBestVirtualSize())
        self.BuildMenu()

    def BuildMenu(self):
        mfile = self.Build_FileMenu()

        mopts = wx.Menu()
        MenuItem(self, mopts, "Configure Plot\tCtrl+K", "Configure Plot styles, colors, labels, etc", self.configure)
        MenuItem(self, mopts, "Configure Lower Plot", "Configure Plot styles, colors, labels, etc", self.configure)
        MenuItem(self, mopts, "Toggle Legend\tCtrl+L", "Toggle Legend Display", self.toggle_legend)
        MenuItem(self, mopts, "Toggle Grid\tCtrl+G", "Toggle Grid Display", self.toggle_grid)


        mopts.AppendSeparator()

        MenuItem(self, mopts, "Zoom Out\tCtrl+Z", "Zoom out to full data range", self.unzoom_all)

        mhelp = wx.Menu()
        MenuItem(self, mhelp, "Quick Reference",  "Quick Reference for WXMPlot", self.onHelp)
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

    def toggle_legend(self, event=None, show=None):
        "toggle grid on top/bottom panels"
        self.stackedpanel.toggle_legend(event=event, show=show)

    def toggle_grid(self, event=None, show=None):
        "toggle grid on top/bottom panels"
        self.stackedpanel.toggle_grid(event=event, show=show)

    def onThemeColor(self, color, item):
        """pass theme colors to bottom panel"""
        self.stackedpanel.onThemeColor(color, item)

    def onMargins(self, left=0.1, top=0.1, right=0.1, bottom=0.1):
        """ pass left/right margins on to bottom panel"""
        self.stackedpanel.onMargins(left=left, top=top, right=right, bottom=bottom)

    def set_viewlimits(self, panel='top'):
        """update xy limits of a plot, as used with .update_line() """
        self.stackedpanel.set_viewlimits(panel=panel)

    def null_formatter(self, x, pos, type='x'):
        return ''

    def bot_yformatter(self, val, type=''):
        """custom formatter for FuncFormatter() and bottom panel"""
        self.stackedpanel.bot_yformatter(val, type=type)
