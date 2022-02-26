#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## MPlot PlotPanel: a wx.Panel for 2D line plotting, using matplotlib
##

import sys
import wx
from wx import Panel
import matplotlib
from functools import partial

from wxmplot.plotpanel import PlotPanel
from wxmplot.baseframe import BaseFrame
from wxmplot.utils import MenuItem

class PlotPanelEx(PlotPanel):

    def __init__(self, parent, size=(700, 450), dpi=150, axisbg=None,
                 facecolor=None, fontsize=9, trace_color_callback=None,
                 output_title='plot', with_data_process=True, theme=None,
                 **kws):

        PlotPanel.__init__(self, parent, size, dpi, axisbg, facecolor, fontsize, trace_color_callback, output_title, with_data_process, theme, **kws)
        self.axesmargins = (20, 20, 20, 20)

    def scale(self, p, min, max):
        return min + ( (float(p)) * ( (max - min) if max > min else (min - max)))

    def add_text_ex(self, text, x=None, y=None, nobox=True, xp=0.0, yp=0.0, side='left', size=None,
                 rotation=None, ha='left', va='center',
                 family=None, draw=True, **kws):
        """add text at supplied x, y position
        """
        axes = self.axes
        if x is None:
            min, max = axes.get_xlim()
            x = self.scale(xp, min, max)
        if y is None:
            min, max = axes.get_ylim()
            y = self.scale(yp, min, max)
        if side == 'right':
            axes = self.get_right_axes()
        dynamic_size = False
        if size is None:
            size = self.conf.legendfont.get_size()
            dynamic_size = True

        t = axes.text(x, y, text, ha=ha, va=va, size=size, rotation=rotation, family=family, **kws)
        if nobox:
            t.set_bbox(dict(facecolor=(1,1,1,0), alpha=0.0, edgecolor=(1,1,1,0), pad=None))
        self.conf.added_texts.append((dynamic_size, t))
        if draw:
            self.draw()

    def axes_set_title(self, label, fontdict=None, loc=None, pad=None, *, y=None, **kwargs):
        self.axes.set_title(label, fontdict=fontdict, loc=loc, pad=pad, y=y, **kwargs)
        self.draw()


class MultiPlotPanel(Panel):
    """
    MatPlotlib Array of 2D plot as a wx.Panel, using Panel
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

    def BuildPanel(self):

        self._sizer = wx.GridBagSizer(3, 3)

        for i in range(self.rows):
            for j in range(self.cols):
                self.panels[(i,j)] = PlotPanelEx(self.frame, size=self.panelsize, messenger=self.write_message)
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


    def set_panel(self,ix,iy):
        self.current_panel = (ix,iy)
        try:
            self.panel = self.panels[(ix,iy)]
        except KeyError:
            print('could not set self.panel')

    # **kw goes to matplotlib axes.text(...*kw)
#    def add_text(self,xp,yp,text,panel=None, **kw):
#        if panel is None:
#            panel = self.current_panel
#
#        xlims = self.panels[panel].axes.get_xlim()
#        ylims = self.panels[panel].axes.get_ylim()
#        x = xlims[0] + ( (float(xp)/1)) * ( (xlims[1] - xlims[0]) if xlims[1] > xlims[0] else (xlims[0] - xlims[1]))
#        y = ylims[0] + ( (float(yp)/1)) * ( (ylims[1] - ylims[0]) if ylims[1] > ylims[0] else (ylims[0] - ylims[1]))
#        #print('MultiPlotPanel::add_text: axes lims: [%5.2f %5.2f][%5.2f %5.2f] xy: %5.2f:%5.2f' % (xlims[0],xlims[1], ylims[0],ylims[1], x, y,), file=sys.stderr)
#        self.panels[panel].add_text(text, x, y, **kw)

    def add_text_ex(self, text, x=None, y=None, xp=0.0, yp=0.0, panel=None, **kws):
        self.panels[panel].add_text_ex(text, x=x, y=y, xp=xp, yp=yp, **kws)


    def plot(self,x,y,panel=None,**kws):
        """plot after clearing current plot """
        if panel is None:
            panel = self.current_panel
        opts = {}
        opts.update(self.default_panelopts)
        opts.update(kws)
        self.panels[panel].plot(x ,y, **opts)
        #self.panels[panel].set_ticks(None)
        #self.panels[panel].add_text('TEST', 1, 2, size=8)


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

    def axes_set_title(self, label, panel=None, fontdict=None, loc=None, pad=None, *, y=None, **kwargs):
        if panel is None: panel = self.current_panel
        self.panels[panel].axes_set_title(label, fontdict=fontdict, loc=loc, pad=pad, y=y, **kwargs)

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


