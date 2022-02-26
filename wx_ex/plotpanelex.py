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

# Adds add_text_ex to PlotPanel
class PlotPanelEx(PlotPanel):

    #def __init__(self, parent, name=None, size=(700, 450), dpi=150, axisbg=None,
    #             facecolor=None, fontsize=9, trace_color_callback=None,
    #             output_title='plot', with_data_process=True, theme=None,
    #             **kws):

    def __init__(self, name=None, parent=None, **kws):

        #super(PlotPanelEx, self).__init__(parent, size=size, dpi=dpi, axisbg=axisbg,
        #    facecolor=facecolor, fontsize=fontsize, trace_color_callback=trace_color_callback,
        #    output_title=output_title, with_data_process=with_data_process, theme=theme, **kws)

        super(PlotPanelEx, self).__init__(parent, **kws)

        self.axesmargins = (20, 20, 20, 20)
        self._name = name

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


# Adds panels dictionary to store multiple sub PlotPanelEx panels in. Redirect
# calls via that.
class MultiPlotPanelEx(PlotPanelEx):
    """
    MatPlotlib Array of 2D plot as a wx.Panel, using Panel
    """
    default_panelopts = dict(labelfontsize=7, legendfontsize=6)

    def __init__(self, name=None, frame=None, parent=None, messenger=None, framesize=None, panelsize=(400, 320), panelopts=None, **kws):

        #super(MultiPlotPanel, self).__init__(self, parent, -1, **kws)
        PlotPaneEx.__init__(self, frame, -1, **kws)

        #self.messenger = messenger if messenger is not None else self.__def_messenger
        #self.parent = parent
        self.name = name
        self.frame = frame
        self.messenger = messenger
        self.popup_menu = None
        self.panels = {}
        #if framesize is None:
        #    framesize = (panelsize[0]*cols, panelsize[1]*rows)
        #self.framesize = framesize
        self.panelsize = panelsize

        self.panelopts = self.default_panelopts
        if panelopts is not None:
            self.panelopts.update(panelopts)

        self.current_panel = (0, 0)
        self.BuildPanel()

    def Add(self, panel=None):
        self.panels[panel.name()] = panel

    def AddMany(self, panellist=None):
        for p in panellist:
            panel, *junk = p
            self.panels[panel.name()] = panel

    def add_text(self,name, x,y,text,**kws):
        self.panels[name].add_text(x, y, text, **kws)

    def add_text_ex(self,name,  text, x=None, y=None, xp=0.0, yp=0.0, **kws):
        self.panels[name].add_text_ex(text, x=x, y=y, xp=xp, yp=yp, **kws)

    def plot(self, x,y,name,*kws):
        """plot after clearing current plot """
        self.panels[name].plot(x,y,**kws)

    def oplot(self, x,y,name,*kws):
        """generic plotting method, overplotting any existing plot """
        self.panels[name].oplot(x,y,**kws)

    def update_line(self,  t, x, y,name=None, **kw):
        """overwrite data for trace t """
        self.panels[name].update_line(t,x,y,**kws)

    def set_xylims(self, lims, axes=None, name=None, ):
        """overwrite data for trace t """
        self.panels[name].set_xylims(lime,axes=axes,)

    def clear(self,name=None):
        """clear plot """
        self.panels[name].clear()

    def unzoom_all(self, event=None,name=None):
        """zoom out full data range """
        self.panels[name].clear(x,y,event=event)

    def unzoom(self, event=None, name=None):
        """zoom out 1 level, or to full data range """
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




class GridBagSizerPanel(MultiPlotPanelEx):

    def __init__(self, name=None, frame=None, parent=None, messenger=None, framesize=None, panelsize=(400, 320), panelopts=None, **kws):
        MultiPlotPanelEx.__init__(self, name=name, frame=frame, parent=parent, messenger=messenger, 
                framesize=framesize, panelsize=panelsize, panelopts=panelopts, **kws)

        self.panels = {}
        self.rows = 0
        self.cols = cols
        self._sizer = wx.GridBagSizer(3, 3)
        self.SetSizer(self._sizer)

    def BuildPanel(self):


        for i in range(self.rows):
            for j in range(self.cols):
                self.panels[(i,j)] = PlotPanelEx(self.frame, name='"%s_%02d-%02d'%(self.name, i, j), 
                    size=self.panelsize, messenger=self.write_message)
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



class WrapSizerPanel(MultiPlotPanelEx):

    def __init__(self, name=None, frame=None, parent=None, messenger=None, orient=wx.HORIZONTAL, framesize=None, panelsize=(400, 320), panelopts=None, **kws):

        MultiPlotPanelEx.__init__(self, name=name, frame=frame, parent=parent, messenger=messenger,
                framesize=framesize, panelsize=panelsize, panelopts=panelopts, **kws)

        self.orient = orient
        self._sizer = wx.WrapSizer(orient=self.orient)
        self.SetSizer(self._sizer)

    def BuildPanel(self):
        pass

    def Add(self, panel=None, proportion=1):
        super(BoxFrameEx, self).Add(panel)
        self._sizer.Add(panel, proportion=proportion)

    def AddMany(self, panellist=None):
        super(BoxFrameEx, self).AddMany(panellist)
        self._sizer.AddMany(panellist)


