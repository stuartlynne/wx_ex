#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
##

import wx
from wx import Panel
import matplotlib
from functools import partial

#from wx_ex.panels[name] import MultiPlotPanel
from wxmplot.plotpanel import PlotPanel
from wxmplot.baseframe import BaseFrame
from wxmplot.utils import MenuItem

class PlotFrameEx(BaseFrame):
    """
    MatPlotlib Array of 2D plot as a wx.Frame, using PlotPanel
    """
    default_panelopts = dict(labelfontsize=7, legendfontsize=6)

    def __init__(self, parent=None, orient=wx.VERTICAL, framesize=(500,400), panelsize=(400, 320), panelopts=None, **kws):

        kws['style'] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER
        self.orient = orient

        BaseFrame.__init__(self, parent=parent, title  = 'MultiPlotFrameEx', size=framesize, **kws)

        #if framesize is None:
        #    framesize = (panelsize[0]*cols, panelsize[1]*rows)
        self.framesize = framesize

        self.panels = {}
        self.sizer = wx.BoxSizer(self.orient)
        self.SetSizer(self.sizer)
        self.BuildFrame()


    def add_panel(self, name=None, flag=wx.EXPAND|wx.ALIGN_CENTER, **kw ):
        self.panels[name] = panel
        self.sizer.Add(panel, **kw)

###
    def add_text(self, x=0, y= 0, text='', name=None, **kw):
        self.panels[name].add_text(name=name, x=x, y=y, text=text, **kw)

    def add_text_ex(self, text='', xp=0.0, yp=0.0, name=None, **kw):
        self.panels[name].add_text_ex(name=name, text=text, xp=xp, yp=yp, **kw)

    def plot(self, x, y, name=None, **kw):
        """plot after clearing current plot """
        self.panels[name].plot(x, y, name=name, **kw)

    def oplot(self, x, y, name=None, **kw):
        """generic plotting method, overplotting any existing plot """
        self.panels[name].oplot(x,y,name=name,**kws)

    def update_line(self, t, x, y, name=None, **kw):
        """overwrite data for trace t """
        self.panels[name].update_line(t,x,y,name=name,**kws)

    def set_xylims(self, lims, axes=None, name=None):
        """overwrite data for trace t """
        self.panels[name].set_xylims(lime,axes=axes,name=name)

    def clear(self,name=None):
        """clear plot """
        self.panels[name].clear(name=name)

    def unzoom_all(self,event=None,name=None):
        """zoom out full data range """
        self.panels[name].clear(x,y,event=event,name=name)

    def unzoom(self, event=None, name=None):
        """zoom out 1 level, or to full data range """
        self.panels[name].unzoom(event=event,name=name)

    def onZoomStyle(self, event=None, style='both x and y'):
        self.panels[name].onZoomStyle(event=event,style=style)

    def set_title(self,s,name=None):
        "set plot title"
        self.panels[name].set_title(s,name=name)

    def axes_set_title(self, label, name=None, fontdict=None, loc=None, pad=None, *, y=None, **kwargs):
        if panel is None: panel = self.current_panel
        self.panels[name].axes_set_title(label, name=name, fontdict=fontdict, loc=loc, pad=pad, y=y, **kwargs)

    def set_xlabel(self,s,name=None):
        "set plot xlabel"
        self.panels[name].set_xlabel(s,name=name)

    def set_ylabel(self,s,name=None):
        "set plot ylabel"
        self.panels[name].set_ylabel(s,name=name)

    def save_figure(self,event=None,name=None):
        """ save figure image to file"""
        self.panels[name].save_figure(event=event,name=name)

    def configure(self,event=None,name=None):
        self.panels[name].configure(event=event,name=name)

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
        self.panels[name].on_configure(event=event, **kws)

    def on_toggle_legend(self, event=None, **kws):
        self.panels[name].on_toggle_legend(event=event, **kws)

    def on_toggle_grid(self, event=None, **kws):
        self.panels[name].on_toggle_grid(event=event, **kws)

    def on_unzoom(self, event=None, **kws):
        self.panels[name].on_unzoom(event=event, **kws)

    def report_leftdown(self, event=None, panelkey=None,**kw):
        self.panels[name].report_leftdown(event=event, panelkey=panelkey, **kw)
