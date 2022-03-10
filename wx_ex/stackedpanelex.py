#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## StackedPlotPanel: a wx.Panel for 2 PlotPanels, top and bottom
##   with the top panel being the main panel and the lower panel
##   being 1/4 the height (configurable) and the dependent panel

import sys
import wx
import numpy as np
import matplotlib
from matplotlib.ticker import NullFormatter, NullLocator
from functools import partial
from wx import Panel
from wxmplot.utils import pack, MenuItem
from wxmplot.plotpanel import PlotPanel
from wxmplot.baseframe import BaseFrame
from wxmplot.basepanel import BasePanel
from wx_ex.plotpanelex import PlotPanelEx
from wxmplot.config import PlotConfig


# StackedPlotPanelEx - create a panel that has top and bottom plots that
# share a common X. Both the top and bottom plots may have multiple plots.
#
class StackedPlotPanelEx(BasePanel):
    """
    Top/Bottom MatPlotlib panels in a single Panel
    """
    def __init__(self, parent=None, name='', messenger=None, framesize=(550,650), panelsize=(550,350), axesmargins=(0,0,0,0), ratio=3.0, **kws):

        print('StackedPlotPanelEx::__init__ kws: %s' % (kws), file=sys.stderr)

        #self.panelsize = panelsize
        #self.ratio = ratio
        super(StackedPlotPanelEx, self).__init__(parent, -1, **kws)
        self.toggle_deriv = False
        self.toggle_deriv = False
        self.conf = PlotConfig(panel=self, theme=None, with_data_process=True)

        self.messenger = messenger
        self.ratio = ratio
        self.panelsize = panelsize
        self.panel_top = None
        self.panel_bot = None
        self.xlabel = None
        self.BuildPanel()
        self.axesmargins = axesmargins

    # XXX These need to be implemented for Menu, which needs PlotConfig, which needs these.
    def process_data(self, data):
        pass
    def set_logscale(self):
        pass


    def Add(self, panel=None):
        self.panels[panel.name()] = panel

    def AddMany(self, panellist=None):
        for p in panellist:
            panel, *junk = p
            self.panels[panel.name()] = panel

    def get_panel(self, panelname):
        if panelname.lower().startswith('bot'):
            return self.panel_bot
        return self.panel_top

    def plot(self, x, y, panel='top', xlabel=None, **kws):
        """plot after clearing current plot """
        panel = self.get_panel(panel)
        panel.plot(x, y, **kws)
        if panel == 'top':
            panel.axes.tick_params(length=10, direction='in', bottom=False, left=True, labelbottom=False, labelleft=True)
        else:
            panel.axes.tick_params(length=10, direction='in', bottom=True, left=True, labelbottom=True, labelleft=True)
        if xlabel is not None:
            self.xlabel = xlabel
        if self.xlabel is not None:
            self.panel_bot.set_xlabel(self.xlabel)

    def oplot(self, x, y, panel='top', xlabel=None, **kws):
        """plot method, overplotting any existing plot """
        panel = self.get_panel(panel)
        panel.oplot(x, y, **kws)
        if xlabel is not None:
            self.xlabel = xlabel
        if self.xlabel is not None:
            self.panel_bot.set_xlabel(self.xlabel)

    def unzoom_all(self, event=None):
        """ zoom out full data range """
        print('StackedPlotPanelEx::unzoom_all[%s]' % (panel), file=sys.stderr)
        for p in (self.panel_top, self.panel_bot):
            p.conf.zoom_lims = []
            p.conf.unzoom(full=True)
        # self.panel.set_viewlimits()

    def unzoom(self, event=None, panel='top'):
        """zoom out 1 level, or to full data range """
        print('StackedPlotPanelEx::unzoom[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        panel.conf.unzoom(event=event)
        self.panel_top.set_viewlimits()

    def update_line(self, t, x, y, panel='top', **kws):
        """overwrite data for trace t """
        print('StackedPlotPanelEx::update_line[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        panel.update_line(t, x, y, **kws)

    def set_xylims(self, lims, axes=None, panel='top', **kws):
        """set xy limits"""
        print('StackedPlotPanelEx::set_xylims[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        # print("Stacked set_xylims ", panel, self.panel)
        panel.set_xylims(lims, axes=axes, **kws)

    def clear(self, panel='top'):
        """clear plot """
        print('StackedPlotPanelEx::clear[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        panel.clear()

    def set_title(self,s, panel='top'):
        """set plot title"""
        print('StackedPlotPanelEx::set_title[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        panel.set_title(s)

    def set_xlabel(self,s, panel='top'):
        "set plot xlabel"
        print('StackedPlotPanelEx::set_xlabel[%s]' % (panel), file=sys.stderr)
        self.panel_bot.set_xlabel(s)

    def set_ylabel(self,s, panel='top'):
        "set plot xlabel"
        print('StackedPlotPanelEx::set_ylabel[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        panel.set_ylabel(s)

    def save_figure(self, event=None, panel='top'):
        """ save figure image to file"""
        print('StackedPlotPanelEx::save_figure[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        panel.save_figure(event=event)

    def configure(self, event=None, panel='top'):
        print('StackedPlotPanelEx::configure[%s]' % (panel), file=sys.stderr)
        panel = self.get_panel(panel)
        panel.configure(event=event)


    ####
    ## create GUI
    ####
    def BuildPanel(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)

        botsize = self.panelsize[0], self.panelsize[1]/self.ratio
        margins = {'top': dict(left=0.15, bottom=0.01, top=0.10, right=0.05),
                   'bot': dict(left=0.15, bottom=0.300, top=0.02, right=0.05)}

        print('StackedPlotPanelEx::BuildPanel panelsize: %s:%s' % (self.panelsize), file=sys.stderr)
        print('StackedPlotPanelEx::BuildPanel botsize: %s:%s' % (botsize), file=sys.stderr)

        self.panel_top = PlotPanelEx(parent=self, name='Top', size=self.panelsize, style=wx.BORDER_SIMPLE, messenger=self.messenger)
        self.panel_bot = PlotPanelEx(parent=self, name='Bottom', size=botsize, style=wx.BORDER_SIMPLE, messenger=self.messenger)

        self.panel_top.xformatter = self.null_formatter
        #lsize = self.panel_top.conf.labelfont.get_size()
        #self.panel_bot.conf.labelfont.set_size(lsize-2)
        #self.panel_bot.yformatter = self.bot_yformatter

        self.panel_top.conf.theme_color_callback = self.onThemeColor
        self.panel_top.conf.margin_callback = self.onMargins

        for pan, pname in ((self.panel_top, 'top'), (self.panel_bot, 'bot')):
            pan.messenger = self.messenger
            pan.conf.auto_margins = True
            figpos = pan.axes.get_subplotspec().get_position(pan.canvas.figure)
            print('StackedPlotPanelEx::BuildPanel figpos: %s' % (figpos), file=sys.stderr)
            pan.axes.set_position(figpos)

            pan.set_viewlimits = partial(self.set_viewlimits, panel=pname)
            pan.unzoom_all = self.unzoom_all
            pan.unzoom = self.unzoom
            pan.canvas.figure.set_facecolor('#F4F4EC')

        # suppress mouse events on the bottom panel
        #null_events = {'leftdown': None, 'leftup': None, 'rightdown': None,
        #               'rightup': None, 'motion': None, 'keyevent': None}
        #self.panel_bot.cursor_modes = {'zoom': null_events}


        print('StackedPlotPanelEx::BuildPanel ratio: %s' % (round(0.75*self.ratio)), file=sys.stderr)
        self._sizer.Add(self.panel_top, round(0.75*self.ratio), wx.GROW|wx.EXPAND, 2)
        self._sizer.Add(self.panel_bot, 1, wx.GROW, 2)
        pack(self, self._sizer)
        self.SetSize(self.GetBestVirtualSize())

    def sizer(self):
        return self._sizer

    def toggle_legend(self, event=None, **kws):
        self.panel_top.toggle_legend()

    def toggle_grid(self, event=None, show=None):
        "toggle grid on top/bottom panels"
        if show is None:
            show = not self.panel_top.conf.show_grid
        for p in (self.panel_top, self.panel_bot):
            p.conf.enable_grid(show)

    def onThemeColor(self, color, item):
        """pass theme colors to bottom panel"""
        bconf = self.panel_bot.conf
        if item == 'grid':
            bconf.set_gridcolor(color)
        elif item == 'bg':
            bconf.set_facecolor(color)
        elif item == 'frame':
            bconf.set_framecolor(color)
        elif item == 'text':
            bconf.set_textcolor(color)
        bconf.canvas.draw()

    def onMargins(self, left=0.1, top=0.1, right=0.1, bottom=0.1):
        """ pass left/right margins on to bottom panel"""
        print('StackedPlotPanelEx::onMargin left: %s top: %s right: %s bottom:%s ' % (left, top, right, bottom), file=sys.stderr)
        bconf = self.panel_bot.conf
        l, t, r, b = bconf.margins
        bconf.set_margins(left=left, top=t, right=right, bottom=b)
        bconf.canvas.draw()

    def set_viewlimits(self, panel='top'):
        """update xy limits of a plot, as used with .update_line() """
        this_panel = self.get_panel(panel)

        xmin, xmax, ymin, ymax = this_panel.conf.set_viewlimits()[0]
        print('StackedPlotPanelEx::set_viewlimits[%s] x: %s:%s y: %s:%s ' % (panel, xmin, xmax, ymin, ymax), file=sys.stderr)
        # make top/bottom panel follow xlimits
        if this_panel == self.panel_top:
            other = self.panel_bot
            for _ax in other.fig.get_axes():
                _ax.set_xlim((xmin, xmax), emit=True)
            other.draw()

    def null_formatter(self, x, pos, type='x'):
        return ''

    def bot_yformatter(self, val, type=''):
        """custom formatter for FuncFormatter() and bottom panel"""
        fmt = '%1.5g'

        ax = self.panel_bot.axes.yaxis

        ticks = ax.get_major_locator()()
        dtick = ticks[1] - ticks[0]

        if   dtick > 29999:
            fmt = '%1.5g'
        elif dtick > 1.99:
            fmt = '%1.0f'
        elif dtick > 0.099:
            fmt = '%1.1f'
        elif dtick > 0.0099:
            fmt = '%1.2f'
        elif dtick > 0.00099:
            fmt = '%1.3f'
        elif dtick > 0.000099:
            fmt = '%1.4f'
        elif dtick > 0.0000099:
            fmt = '%1.5f'

        s =  fmt % val
        s.strip()
        s = s.replace('+', '')
        while s.find('e0')>0:
            s = s.replace('e0','e')
        while s.find('-0')>0:
            s = s.replace('-0','-')
        return s
