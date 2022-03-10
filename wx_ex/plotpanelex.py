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
from wxmplot.config import PlotConfig
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.gridspec import GridSpec
from matplotlib.colors import colorConverter
from matplotlib.collections import CircleCollection



# Adds add_text_ex to PlotPanel
class PlotPanelEx(PlotPanel):

    def __init__(self, parent, name=None, build_panel=True, fontsize=4, axesmargins=(0,0,0,0), **kws):

        print('PlotPanelEx::__init__ name: %s kws: %s' % (name, kws), file=sys.stderr)

        self._name = name

        self.initFlag = True
        super(PlotPanelEx, self).__init__(parent, fontsize=fontsize, **kws)
        self.initFlag = False

        print('PlotPanelEx::__init__ self.conf: %s' % (self.conf), file=sys.stderr)

        #self.conf = PlotConfig(panel=self, theme=None, with_data_process=True)

        self.axesmargins = axesmargins
        #try:
        #    self.axes.tick_params(length=0, direction='in')
        #except:
        #    print('PlotPanelEx::__init__ self.axes.tick_params does not exist', file=sys.stderr)

        p1=wx.Panel(self)
        p1.BackgroundColor = 'pink'

        self.BuildPanel()

    def oBuildPanel(self):
        """ builds basic GUI panel and popup menu"""
        print('PlotPanelEx::BuildPanel ', file=sys.stderr)
        self.fig   = Figure(self.figsize, dpi=self.dpi)
        # 1 axes for now
        self.gridspec = GridSpec(1,1)
        self.axes  = self.fig.add_subplot(self.gridspec[0], facecolor=self.conf.facecolor)
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.canvas.SetClientSize((self.figsize[0]*self.dpi, self.figsize[1]*self.dpi))
        self.canvas.SetMinSize((100, 100))

        self.printer.canvas = self.canvas
        self.set_bg(self.conf.framecolor)
        self.conf.canvas = self.canvas
        self.canvas.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        #self.canvas.mpl_connect("pick_event", self.__onPickEvent)

        # overwrite ScalarFormatter from ticker.py here:
        self.axes.xaxis.set_major_formatter(FuncFormatter(self.xformatter))
        self.axes.yaxis.set_major_formatter(FuncFormatter(self.yformatter))

        # This way of adding to sizer allows resizing
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.ALIGN_CENTER|wx.RIGHT|wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, 0)
        # self.SetAutoLayout(True)
        self.autoset_margins()
        self.SetSizer(sizer)
        #self.SetSize(self.GetBestVirtualSize())

        canvas_draw = self.canvas.draw
        def draw(*args, **kws):
            self.autoset_margins()
            canvas_draw(*args, **kws)
        self.canvas.draw = draw
        self.addCanvasEvents()



    def BuildPanel(self):
        print('PlotPanelEx::BuildPanel ', file=sys.stderr)
        if self.initFlag is False:
            print('PlotPanelEx::BuildPanel calling super ', file=sys.stderr)
            super(PlotPanelEx, self).BuildPanel()

    def xwrite_message(self, s, panel=0):
        print('PlotPanelEx::xwrite_message[%s] %s' % (self._name, s), file=sys.stderr)
        self.SetStatusText(s, panel)

    def OnMessage(self, name, message):
        print('PlotPanelEx::OnMessage[%s:%s] message: %s' % (name, self._name, message), file=sys.stderr)

    def name(self):
        return self._name

    def scale(self, p, min, max):
        return min + ( (float(p)) * ( (max - min) if max > min else (min - max)))

    def add_text_ex(self, text, nobox=True, xp=0.0, yp=0.0, side='left', size=None,
                 rotation=None, ha='left', va='center',
                 family=None, draw=True, **kws):
        """add text at supplied x, y position
        """
        axes = self.get_right_axes() if side == 'right' else self.axes

        min, max = axes.get_xlim()
        x = self.scale(xp, min, max)
        min, max = axes.get_ylim()
        y = self.scale(yp, min, max)
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

    #def plot(self, x,y,axes_style='open', labelfontsize=4, **kws):
    #    print('PlotPanelEx::plot[%s]' % (self._name), file=sys.stderr)
    #    super(PlotPanelEx, self).plot(x, y, axes_style='open', labelfontsize=4, **kws) 
    #    #self.axes.tick_params(length=1, direction='in', bottom=False, left=False, labelbottom=False, labelleft=False)
    #    #self.axes.set_facecolor('lightgreen')



    def report_motion(self, event):
        print('PlotPanelEx::report_motion[%s] event: %s' % (self._name, event), file=sys.stderr)
        super(PlotPanelEx, self).report_motion(event)

    def Destroy(self):
        print('PlotPanelEx::Destroy[%s]' % (self._name), file=sys.stderr)
        super(PlotPanelEx, self).Destroy()


# Adds panels dictionary to store multiple sub PlotPanelEx panels in. Redirect
# calls via that.
class MultiPlotPanelEx(PlotPanelEx):
    """
    MatPlotlib Array of 2D plot as a wx.Panel, using Panel
    """
    default_panelopts = dict(labelfontsize=7, legendfontsize=6)

    def __init__(self, name=None, parent=None, sizer=None, panelsize=None, panelopts=None, size=wx.DefaultSize, **kws):

        print('MultiPlotPanelEx::__init__[%s] size: %s kws: %s' % (name, size, kws), file=sys.stderr)
        #super(MultiPlotPanel, self).__init__(self, parent, -1, **kws)
        self._sizer = None
        super(MultiPlotPanelEx, self).__init__(parent, name=name, build_panel=False, size=size, **kws)

        self._name = name
        self._sizer = sizer
        self.popup_menu = None
        self.panels = {}
        self.panelsize = panelsize

        self.panelopts = self.default_panelopts
        if panelopts is not None:
            self.panelopts.update(panelopts)

        self.current_panel = (0, 0)
        #self.BuildPanel()

    def BuildPanel(self):
        print('MultiPlotPanelEx::BuildPanel self._sizer=%s' % (self._sizer), file=sys.stderr)
        if self._sizer is not None:
                print('MultiPlotPanelEx::BuildPanel ' , file=sys.stderr)
                self.SetSizer(self._sizer)
                self._sizer.Layout()
                self.Layout()

    def add_panel(self, name=None, panel=None):
        print('MultiPlotPanelEx::add_panel %s' % (name), file=sys.stderr)
        self.panels[name] = panel

    def panels_add(self, name=None, panel=None):
        self.add_panel(name=name, panel=panel)

    def add_panels(self, panellist=None):
        for p in panellist:
            print('MultiPlotPanelEx::add_panels %s' % (p.name), file=sys.stderr)
            self.panels[p._name] = p

    def Detach(self, name, panel):
        print('MultiPlotPanelEx::Detach name: %s panel: %s' % (name, panel), file=sys.stderr)
        self._sizer.Detach(panel)
        panel.Destroy()
        del panel

    def DetachAll(self):
        print('MultiPlotPanelEx::DetachAll', file=sys.stderr)
        for n, p in self.panels.items():
            self.Detach(n, p)


    def add_text(self,name, x,y,text,**kws):
        self.panels[name].add_text(x, y, text, **kws)

    def add_text_ex(self,name,  text, x=None, y=None, xp=0.0, yp=0.0, **kws):
        self.panels[name].add_text_ex(text, x=x, y=y, xp=xp, yp=yp, **kws)

    def plot(self, x,y,name,*kws):
        """plot after clearing current plot """
        print('PlotPanelEx::plot[%s]' % (self._name), file=sys.stderr)
        self.panels[name].plot(x, y, **kws)

    def oplot(self, x,y,name,*kws):
        """generic plotting method, overplotting any existing plot """
        print('PlotPanelEx::oplot[%s]' % (self._name), file=sys.stderr)
        self.panels[name].oplot(x,y,**kws)

    def update_line(self,  t, x, y,name=None, **kw):
        """overwrite data for trace t """
        print('PlotPanelEx::update_line[%s]' % (self._name), file=sys.stderr)
        self.panels[name].update_line(t,x,y,**kws)

    def set_xylims(self, lims, axes=None, name=None, ):
        """overwrite data for trace t """
        print('PlotPanelEx::set_xylims[%s]' % (self._name), file=sys.stderr)
        self.panels[name].set_xylims(lime,axes=axes,)

    def clear(self,name=None):
        """clear plot """
        print('PlotPanelEx::clear[%s]' % (self._name), file=sys.stderr)
        self.panels[name].clear()

    def unzoom_all(self, event=None,name=None):
        """zoom out full data range """
        print('PlotPanelEx::unzoom_all[%s] event: %s' % (self._name, event), file=sys.stderr)
        self.panels[name].clear(x,y,event=event)

    def unzoom(self, event=None, name=None):
        """zoom out 1 level, or to full data range """
        print('PlotPanelEx::unzoom[%s] event: %s' % (self._name, event), file=sys.stderr)
        self.panels[name].unzoom(event=event)

    def onZoomStyle(self, name=None, event=None, style='both x and y'):
        self.panels[name].onZoomStyle(event=event,style=style)

    def set_title(self, s,name=None):
        "set plot title"
        self.panels[name].set_title(s,)

    def axes_set_title(self,  label, name=None,fontdict=None, loc=None, pad=None, *, y=None, **kwargs):
        if panel is None: panel = self.current_panel
        self.panels[name].axes_set_title(label, ontdict=fontdict, loc=loc, pad=pad, y=y, **kwargs)

    def set_xlabel(self, s,name=None,):
        "set plot xlabel"
        self.panels[name].set_xlabel(s,)

    def set_ylabel(self, s,name=None,):
        "set plot ylabel"
        self.panels[name].set_ylabel(s,)

    def save_figure(self, event=None,name=None,):
        """ save figure image to file"""
        self.panels[name].save_figure(event=event,)

    def configure(self, event=None,name=None,):
        self.panels[name].configure(event=event,)


    def report_motion(self, event):
        print('MultiPlotPanelEx::report_motion[%s] event: %s' % (self._name, event), file=stderr)
        super(MultiPlotPanelEx, self).report_motion(event)


#    def on_configure(self, event=None, **kws):
#        self.multipanel.on_configure(event=event, **kws)
#
#    def on_toggle_legend(self, event=None, **kws):
#        self.multipanel.on_toggle_legend(event=event, **kws)
#
#    def on_toggle_grid(self, event=None, **kws):
#        self.multipanel.on_toggle_grid(event=event, **kws)
#
#    def on_unzoom(self, event=None, **kws):
#        self.multipanel.on_unzoom(event=event, **kws)
#
#    def report_leftdown(self, event=None, panelkey=None,**kw):
#        self.multipanel.report_leftdown(event=event, panelkey=panelkey, **kw)




class GridBagSizerPanelEx(MultiPlotPanelEx):

    def __init__(self, name=None, parent=None, panelsize=None, panelopts=None, **kws):


        self._sizer = None
        super(GridBagSizerPanelEx, self).__init__(name=name, parent=parent, **kws)

        self._sizer = wx.GridBagSizer(3, 3)
        self.SetSizer(self._sizer)
        self.Layout()

        self.panels = {}
        self.rows = 0
        self.cols = 0

#    def BuildPanel(self):
#        print('GridBagSizerPanelEx::BuildPanel self._sizer=%s' % (self._sizer), file=sys.stderr)
#        self.SetSizer(self._sizer)
#        self._sizer.Layout()
#        self.Layout()

    def sizer_add(self, panel, loc=(0,0), span=(1,1), flag=wx.EXPAND|wx.ALIGN_CENTER):
        print('GridBagSizerPanelEx::AddSizer loc=%s span=%s' % (loc, span), file=sys.stderr)
        self._sizer.Add(panel, loc, span, flag=flag)

    @property
    def Sizer(self):
        return self._sizer



class BoxSizerPanelEx(MultiPlotPanelEx):

    def __init__(self, name=None, parent=None, orient=wx.HORIZONTAL, panelsize=None, panelopts=None, **kws):

        self.orient = orient
        self._sizer = None
        self._sizer = wx.BoxSizer(orient=self.orient)
        super(WrapSizerPanelEx, self).__init__(name=name, parent=parent, panelsize=panelsize, panelopts=panelopts, **kws)

#    def BuildPanel(self):
#        print('WrapSizerPanelEx::BuildPanel', file=sys.stderr)
#        print('WrapSizerPanelEx::BuildPanel _sizer: %s' % (self._sizer), file=sys.stderr)
#        self.SetSizer(self._sizer)
#        #self.SetSize(self.GetBestVirtualSize())
#        self._sizer.Layout()
#        self.Layout()
#        pass

    def sizer_add(self, panel, proportion=1):
        print('WrapSizerPanelEx::Add proportion: %s' % (proportion), file=sys.stderr)
        super(WrapSizerPanelEx, self).Add(name=name, panel=panel)
        if self._sizer is not None:
            self._sizer.Add(panel, proportion=proportion, flag=wx.EXPAND|wx.ALIGN_CENTER)

