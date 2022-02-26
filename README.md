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


- TrainingApp
    - wx.App

Top level PlotFrame - two columns, left for devices sub-panels, right for stacked multiplot
    - wx_ex.BoxSizerVerticalEx
        - wx_ex.MultiPlotFrame
            - wx_ex.PlotFrameEx
                - wxmplot.PlotFrame
                    - wxmplot.BaseFrame
                        - wx.Frame

For each reporting device, e.g. HRM, PM, FEC:

- XXXPanel
    wx.Panel

Each panel builds up plots using PlotPanelEx

- wx_ex.WrapSizerPanelEx
    - wx_ex.MultiPlotPanelEx
        - wx_ex.PlotPanelex
            - wxmplot.PlotPanel
                - wxmplot.BasePanel

- wx_ex.GridBagPanelEx
    - wx_ex.MultiPlotPanelEx
        - wx_ex.PlotPanelEx


For Stacked Plot column:

- StackedPlotPanel
    wx.Panel

Uses StackedMultiPlotEx to build the stack of plots:

- wx_ex.StackedMultiPlotEx
    - wx_ex.StackedPlotEx
        - 

