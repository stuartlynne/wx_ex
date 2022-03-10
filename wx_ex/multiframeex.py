#!/usr/bin/python
# vim: shiftwidth=4 tabstop=4 expandtab textwidth=0
##
## MPlot PlotFrame: a wx.Frame for 2D line plotting, using matplotlib
##

import sys
import traceback
import wx
from wx import Panel
import matplotlib
from functools import partial

from wxmplot.baseframe import BaseFrame
from wxmplot.utils import MenuItem

import threading
import queue
from threading import Thread
from queue import Empty
# for debugging
import platform
if platform.system() == 'Linux':
    import prctl


class InDataThreadEx(Thread):

    def __init__(self, appname='', name='InDataThreadEx', control_queue=None, in_queue=None, OnMessage=None, kwargs=None):

        print('ThreadEx::__init__', file=sys.stderr)
        super(InDataThreadEx, self).__init__(name=name, kwargs=kwargs)

        self.in_queue = in_queue
        self.control_queue = control_queue
        self.stopFlag = False
        self.flushing = True
        self.OnMessage = OnMessage
        self.name = name
        self.appname = appname

    def check_control(self):
        try:
            message = self.control_queue.get(block=False, timeout=0)
            print('ThreadEx::check_control message: %s' % (message), file=sys.stderr)
            return False
        except Empty:
            print('ThreadEx::check_control Empty', file=sys.stderr)
            return True

    def check_data(self, block, timeout):
        try:
            message = self.in_queue.get(block=block, timeout=timeout)
            print('ThreadEx::check_data message: %s' % (message), file=sys.stderr)
            return message
        except Empty:
            print('ThreadEx::check_data Empty', file=sys.stderr)
            return None

    def run(self):
        if platform.system() == 'Linux':
            prctl.set_proctitle(f'{self.appname}:{self.name}')
        try:
            print('ThreadEx::run', file=sys.stderr)
            while self.check_control():
                message = self.check_data(block=True, timeout=2)
                if self.OnMessage is not None:
                    print('ThreadEx::run sending message: %s' % (message), file=sys.stderr)
                    wx.CallAfter(self.OnMessage, message)

        except KeyboardInterrupt:
            print('ThreadEx::run KeyboardInterrupt', file=sys.stderr)
        except exception as e:
            print('ThreadEx::run exception: %s' % (e), file=sys.stderr)
            print('ThreadEx::run %s' % (traceback.format_exc()), file=sys.stderr)

        print('ThreadEx::run finished exiting', file=sys.stderr)



# extend BaseFrame to support multiple named sub-panels.
#
class MultiFrameEx(BaseFrame):
    """
    2D grid of PlotPanels
    """
    default_panelopts = dict(labelfontsize=7, legendfontsize=6)

    def __init__(self, parent=None, in_queue=None, rows=1, cols=1, framesize=None, panelsize=(400, 320), size=None, panelopts=None, **kws):

        self.in_queue = in_queue
        kws['style'] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER

        super(MultiFrameEx, self).__init__(parent=parent, **kws)

        if framesize is None:
            framesize = (panelsize[0]*cols, panelsize[1]*rows)
        self.framesize = framesize
        #self.multipanel = MultiPlotPanel(frame=self, rows=rows, cols=cols, panelsize=panelsize, panelopts=panelopts, **kws)
        print('MultiFrameEx::__init__ framesize: %s panelsize: %s size: %s' % (framesize, panelsize, size), file=sys.stderr)
        self.panels = {}

        self.sbar = self.CreateStatusBar(2, wx.CAPTION)
        sfont = self.sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        self.sbar.SetFont(sfont)

        self.BuildMenu()
        self.SetStatusWidths([-3, -1])
        self.SetStatusText('',0)
        self.SetSize(self.framesize)
        self.SetAutoLayout(True)

        if self.in_queue is not None:
            print('MultiFrameEx::__init__ starting InDataThreadEx', file=sys.stderr)
            self.control_queue = queue.Queue()
            self.thread = InDataThreadEx(name='Frame Data', control_queue=self.control_queue, in_queue=self.in_queue, OnMessage = self._OnMessage )
            self.thread.start()
        else:
            print('MultiFrameEx::__init__ not starting InDataThreadEx', file=sys.stderr)
            self.thread = None


    #def write_message(self, txt, panel=0):
    #    print('MultiFrameEx::write_message txt: %s' % (txt), file=sys.stderr)
    #    #super(MultiFrameEx, self).write_message(txt, panel)
    #    self.SetStatusText(txt, panel)

    def _OnMessage(self, message=None):
        print('MultiFrameEx::_OnMessage message:', file=sys.stderr)
        self.OnMessage(message)

    def OnMessage(self, message=None):
        print('MultiFrameEx::OnMessage message:', file=sys.stderr)
        #for k, p in self.panels.items():
        #    p.OnMessage(message=message)
        #pass

    def OnClose(self, event):
        print('MultiFrameEx::OnClose', file=sys.stderr)
        if self.thread is not None:
            print('MultiFrameEx::OnClose sending Stop', file=sys.stderr)
            self.control_queue.put('stop')
            print('MultiFrameEx::OnClose calling join', file=sys.stderr)
            self.thread.join()
            print('MultiFrameEx::OnClose joined', file=sys.stderr)
            self.thread = None


    def panels_add(self, name=None, panel=None):
        #self.panels[panel.name()] = panel
        print('MultiFrameEx::Add name: %s' % (name), file=sys.stderr)
        self.panels[name] = panel

    def Pop(self, name):
        print('MultiFrameEx::Pop name: %s' % (name), file=sys.stderr)
        return self.panels.pop(name)

    def Del(self, name):
        print('MultiFrameEx::Del name: %s' % (name), file=sys.stderr)
        self.panels[name]


    def AddMany(self, panellist=None):
        for p in panellist:
            panel, *junk = p
            self.panels[panel.name()] = panel


    ####
    ## create GUI
    ####
    def BuildFrame(self):
        #self.SetSizerAndFit(self._sizer)
        self.SetSizer(self._sizer)
        self.Layout()
        pass

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
        print('MultiFrameEx::report_leftdown event: %s panelkey: %s kw: %s' % (event, panel, kw), file=sys.stder)
        self.multipanel.report_leftdown(event=event, panelkey=panelkey, **kw)

