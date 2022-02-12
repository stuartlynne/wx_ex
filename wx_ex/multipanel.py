#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
##

import wx
from wx import Panel
import matplotlib
from functools import partial

from wxmplot.plotpanel import PlotPanel
from wxmplot.baseframe import BaseFrame
from wxmplot.utils import MenuItem

class MultiPlotPanel(Panel):
    """
    MatPlotlib Array of 2D plot as a wx.Panel, using PlotPanel
    """
    default_panelopts = dict(labelfontsize=7, legendfontsize=6)

    def __init__(self, frame=None, parent=None, messenger=None, rows=1, cols=1, framesize=None, panelsize=(400, 320), panelopts=None, **kws):

        #super(MultiPlotPanel, self).__init__(self, parent, -1, **kws)
        Panel.__init__(self, frame, -1, **kws)

        #self.messenger = messenger if messenger is not None else self.__def_messenger
        #self.parent = parent
        self.frame = frame
        self.messenger = messenger
        self.popup_menu = None
        self.panels = {}
        self.rows = rows
        self.cols = cols
        #if framesize is None:
        #    framesize = (panelsize[0]*cols, panelsize[1]*rows)
        #self.framesize = framesize
        self.panelsize = panelsize

        self.panelopts = self.default_panelopts
        if panelopts is not None:
            self.panelopts.update(panelopts)

        self.current_panel = (0, 0)
        self.BuildPanel()

    def set_panel(self,ix,iy):
        self.current_panel = (ix,iy)
        try:
            self.panel = self.panels[(ix,iy)]
        except KeyError:
            print('could not set self.panel')

    def plot(self,x,y,panel=None,**kws):
        """plot after clearing current plot """
        if panel is None:
            panel = self.current_panel
        opts = {}
        opts.update(self.default_panelopts)
        opts.update(kws)
        self.panels[panel].plot(x ,y, **opts)

    def oplot(self,x,y,panel=None,**kws):
        """generic plotting method, overplotting any existing plot """
        if panel is None:
            panel = self.current_panel
        opts = {}
        opts.update(self.default_panelopts)
        opts.update(kws)
        self.panels[panel].oplot(x, y, **opts)

    def update_line(self, t, x, y, panel=None, **kw):
        """overwrite data for trace t """
        if panel is None:
            panel = self.current_panel
        self.panels[panel].update_line(t, x, y, **kw)

    def set_xylims(self, lims, axes=None, panel=None):
        """overwrite data for trace t """
        if panel is None: panel = self.current_panel
        self.panels[panel].set_xylims(lims, axes=axes, **kw)

    def clear(self,panel=None):
        """clear plot """
        if panel is None: panel = self.current_panel
        self.panels[panel].clear()

    def unzoom_all(self,event=None,panel=None):
        """zoom out full data range """
        if panel is None: panel = self.current_panel
        self.panels[panel].unzoom_all(event=event)

    def unzoom(self, event=None, panel=None):
        """zoom out 1 level, or to full data range """
        if panel is None:
            panel = self.current_panel
        self.panels[panel].unzoom(event=event)

    def onZoomStyle(self, event=None, style='both x and y'):
        for panel in self.panels.values():
            panel.conf.zoom_style = style

    def set_title(self,s,panel=None):
        "set plot title"
        if panel is None: panel = self.current_panel
        self.panels[panel].set_title(s)

    def set_xlabel(self,s,panel=None):
        "set plot xlabel"
        if panel is None: panel = self.current_panel
        self.panels[panel].set_xlabel(s)

    def set_ylabel(self,s,panel=None):
        "set plot xlabel"
        if panel is None: panel = self.current_panel
        self.panels[panel].set_ylabel(s)

    def save_figure(self,event=None,panel=None):
        """ save figure image to file"""
        if panel is None: panel = self.current_panel
        self.panels[panel].save_figure(event=event)

    def configure(self,event=None,panel=None):
        if panel is None: panel = self.current_panel
        self.panels[panel].configure(event=event)


    def write_message(self, msg, panel=0):
        """write a message to the Status Bar"""
        self.frame.SetStatusText(msg, panel)

    def BuildPanel(self):

        self._sizer = wx.GridBagSizer(3, 3)

        for i in range(self.rows):
            for j in range(self.cols):
                self.panels[(i,j)] = PlotPanel(self.frame, size=self.panelsize, messenger=self.write_message)
                # **self.panelopts)
                self.panels[(i,j)].messenger = self.write_message
                panel = self.panels[(i,j)]

                self._sizer.Add(panel,(i,j),(1,1),flag=wx.EXPAND|wx.ALIGN_CENTER)
                panel.report_leftdown = partial(self.report_leftdown, panelkey=(i,j))

        self.panel = self.panels[(0,0)]
        for i in range(self.rows):
            self._sizer.AddGrowableRow(i)
        for i in range(self.cols):
            self._sizer.AddGrowableCol(i)

        pass

    def sizer(self):
        return self._sizer

    def on_configure(self, event=None, **kws):
        self.panel.configure()

    def on_toggle_legend(self, event=None, **kws):
        self.panel.toggle_legend()

    def on_toggle_grid(self, event=None, **kws):
        self.panel.toggle_grid()

    def on_unzoom(self, event=None, **kws):
        self.panel.unzoom()

    def report_leftdown(self, event=None, panelkey=None,**kw):
        try:
            self.panel.set_bg()
            self.panel.canvas.draw()
        except:
            pass

        if panelkey is None or event is None:
            return

        ix, iy = panelkey
        self.set_panel(ix, iy)
        panel = self.panel
        ex, ey = event.x, event.y
        tmsg = 'Current Panel: (%i, %i) ' % (ix, iy)
        try:
            x, y = panel.axes.transData.inverted().transform((ex, ey))
        except:
            x, y = event.xdata, event.ydata

        try:
            if x is not None and y is not None:
                msg = ("%s X,Y= %s, %s" % (tmsg, panel._xfmt, panel._yfmt)) % (x, y)

            self.write_message(msg, panel=0)
        except:
            pass


