# wx_extras
# Sat 12 Feb 2022 12:11:19 PM PST
# stuart.lynne@gmail.com


The wxmplot library contains two interesting classes to instantiate graphs into
a multi-plot frame and stacked-plot frame.

The wx heirarchy does not allow frames to be nested, so this will take a subset
of these that use the wx Panel and make that available allowing them to be added
to other wx frames.


## MultiPanel

Derived Panel version of wxmplot MultiFrame.



## StackedPlotPanel

Derived Panel version of wxmplot StackedPlotPanel.




## Heirarchy

Three levels with specific classes:

- Top Window - wxmplot.BaseFrame derived class for overall layout.
- Column 1 - bespoke wx.Panel derived classes for devices
- Column 2 - bespoke wx.Panel derived classes for stacked plot
- Bottom - plotting is done with wxmplot.PlotPanel derived classes.


## MultiFrameEx

- wx.Frame(... wx.Window)
- wxmplot.BaseFrame(wx.Frame)
- wxmplot.PlotFrame(wxmplot.BaseFrame)
- wx\_ex.MultiFrameEx(wxmplot.BaseFrame)
- wx\_ex.BoxFrameEx(wx\_ex.MultiFrameEx)

## PlotPanelEx

- wx.Panel(... wx.Window)
- wxmplot.BasePanel(wx.Panel)
- wxmplot.PlotPanel(wxmplot.BasePanel)
- wx\_ex.PlotPanelEx(wxmplot.PlotFrame)
- wx\_ex.MultiPlotPanelEx(wx\_ex.PlotPanelEx)
- wx\_ex.GridBagSizerPanelEx(wx\_ex.MultiPlotPanelEx)
- wx\_ex.WrapSizerPanelEx(wx\_ex.MultiPlotPanelEx)

## StackedPlotPanelEx

- wx.Panel(... wx.Window)
- wxmplot.BasePanel(wx.Panel)
- wxmplot.PlotPanel(wxmplot.BasePanel)
- wx\_ex.PlotPanelEx(wxmplot.PlotFrame)
- wx\_ex.StackedPlotPanelEx(wx\_ex.PlotPanelEx)

## Column 1 - Devices

Each device type (HRM, PM, FEC) has its own class:

- wx\_ex.HRMPanel(wx.Panel)
- wx\_ex.PMPanel(wx.Panel)
- wx\_ex.FECPanel(wx.Panel)

These are created to contain various PlotPanelEx derived plotting panels.

They are added to the MultiFrameEx sizer.

## Colum  2 - Stacked Plots

A single(?) StackedPlots panel is created to contain multiple StackedPlotEx panels.

- wx\_ex.StackedPlots(wx.Panel)

