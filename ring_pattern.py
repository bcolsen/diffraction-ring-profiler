#!/usr/bin/env python
"""
Makes ring patterns from profiles
"""
from numpy import *

import matplotlib

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg

from matplotlib.backends.backend_wx import _load_bitmap
from matplotlib.figure import Figure
from numpy.random import rand

import wx
import os

from numpy import *
import scipy.constants as con
from scipy.optimize import leastsq
#import scipy.linalg
from matplotlib.pyplot import *
import matplotlib.patches as patches

from polar_pattern import *
from sim_index import *

import ring_pattern

import time

class Timer():
   def __enter__(self): self.start = time.time()
   def __exit__(self, *args): print time.time() - self.start

from matplotlib import rc

rc('savefig', dpi=600)

class MyNavigationToolbar2(NavigationToolbar2WxAgg):
    """
    Extend the default wx toolbar with your own event handlers
    """
    def __init__(self, parent, canvas, cankill):
        NavigationToolbar2WxAgg.__init__(self, canvas)
        
        self.parent = parent
           
    def mouse_move(self, event):
        #print 'mouse_move', event.button
                
        if event.inaxes:

            try: s = event.inaxes.format_coord(event.xdata, event.ydata)
            except ValueError: pass
            except OverflowError: pass
            else:
                if len(self.mode):
                    self.parent.statbar.SetStatusText('%s, %s' % (self.mode, s), 1)
                else:
                    self.parent.statbar.SetStatusText(s, 1)
        else: self.parent.statbar.SetStatusText(self.mode,1)
        
    def set_cursor(self, cursor):
        cursor =wx.StockCursor(cursord[cursor])
        self.canvas.SetCursor( cursor )

class ring_pattern(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self,parent,-1,"Ring Figure - "+parent.filename ,size=(550,350))
                
        self.parent = parent
        
        iconFile = os.path.join(parent.parent.iconspath, "diff_profiler_ico.ico")
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        
        self.SetIcon(icon1)
        
        self.mpl_old = self.parent.mpl_old
        
        self.background_sub = self.parent.background_sub
        self.prosim = self.parent.prosim
        self.plot_sim = self.parent.plot_sim
        self.ring_patt = []
        self.back_patt = []
        
        self.dirname = self.parent.dirname

        self.statbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
        self.statbar.SetFieldsCount(2)
        self.statbar.SetStatusText("None", 1)

        # Setting up the menu. filemenu is a local variable at this stage.
        figmenu= wx.Menu()
        # use ID_ for future easy reference - much better than "48", "404" etc
        # The & character indicates the short cut key
        self.Save_evt = figmenu.Append(wx.NewId(), "&Save Figure","Save the figure as vestor or highres image")
        self.BGSub_evt = figmenu.AppendCheckItem(wx.NewId(), "&Background Subtract","Subtract the profile fitted background from the pattern image")
        self.ProSim_evt = figmenu.AppendCheckItem(wx.NewId(), "&Profile Simulation","Show the ring pattern from a profile simulation")
        self.PeakSim_evt = figmenu.AppendCheckItem(wx.NewId(), "Peak &Simulation","Show a peak simulation as rings")
        
        if self.parent.background_sub:
            self.BGSub_evt.Check(True)
        else:
            self.BGSub_evt.Enable(False)
            
        if self.parent.prosim:
            self.ProSim_evt.Check(True)
        else:
            self.ProSim_evt.Enable(False)
            
        if self.parent.plot_sim:
            self.PeakSim_evt.Check(True)
        else:
            self.PeakSim_evt.Enable(False)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(figmenu,"&Figure") # Adding the "patternmenu" to the MenuBar

        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        # Note - previous line stores the whole of the menu into the current object
        
        self.SetBackgroundColour(wx.NamedColour("WHITE"))

        self.figure = Figure(figsize=(6,6), dpi=76)
        self.axes = self.figure.add_axes([0,0,1,1],yticks=[],xticks=[],frame_on=False)#
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        
        # Capture the paint message
        wx.EVT_PAINT(self, self.OnPaint)
        
        self.toolbar = MyNavigationToolbar2(self, self.canvas, True)
        self.toolbar.Realize()

        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
            
        # update the axes menu on the toolbar
        self.toolbar.update()        
        
        # Define the code to be run when a menu option is selected
        if self.mpl_old:
            self.Bind(wx.EVT_MENU, self.toolbar.save, self.Save_evt)
        self.Bind(wx.EVT_MENU, self.toolbar.save_figure, self.Save_evt)
        self.Bind(wx.EVT_MENU, self.OnBGSub, self.BGSub_evt)
        self.Bind(wx.EVT_MENU, self.OnProSim, self.ProSim_evt)
        self.Bind(wx.EVT_MENU, self.OnPeakSim, self.PeakSim_evt)

        self.SetSizer(self.sizer)
        self.Fit()
        
        self.ring_plot()
        
    def OnBGSub(self, event):
        #self.id = event.GetId() 
        if self.BGSub_evt.IsChecked():
            self.background_sub = 1
        else:
            self.background_sub = 0
        self.ring_plot()
        
    def OnProSim(self, event):
        #self.id = event.GetId() 
        if self.ProSim_evt.IsChecked():
            self.prosim = 1
        else:
            self.prosim = 0
        self.ring_plot()
        
    def OnPeakSim(self, event):
        #self.id = event.GetId() 
        if self.PeakSim_evt.IsChecked():
            self.plot_sim = 1
        else:
            self.plot_sim = 0
        
        self.axes.cla()
        self.ring_plot()
        
    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()
        
    def ring_plot(self):
        
        #rc('font', size=16)
        
        if self.parent.latex:
            rc('text', usetex=True)
            rc('font', family='serif')
        else:
            rc('text', usetex=False)
            rc('font', family='sans-serif')
            rc('mathtext', fontset = 'custom')
        
        self.origin =  [round(self.parent.C[1]), round(self.parent.C[0])]
        
        #self.pattern_open_crop = self.parent.pattern_open[origin[0]-(self.parent.boxs-6):origin[0]+(self.parent.boxs-3),origin[1]-(self.parent.boxs-6):origin[1]+(self.parent.boxs-3)]
        self.pattern_open_crop = self.parent.pattern_open[self.origin[0]-(self.parent.boxs):self.origin[0]+(self.parent.boxs),self.origin[1]-(self.parent.boxs):self.origin[1]+(self.parent.boxs)]
        
        if self.background_sub == 1: 
            self.do_background_sub()

        self.axes.imshow(self.pattern_open_crop, cmap = 'gray',
                extent=(-self.parent.drdf.max(), self.parent.drdf.max(), -self.parent.drdf.max(), self.parent.drdf.max()))
        
        if self.prosim == 1:
            self.do_prosim()
        if self.plot_sim == 1:
            self.do_plot_sim()

        #self.axes.plot(0,0,'+')
        #self.axes.axis('equal')
        self.axes.set_xlim(-self.parent.limit, self.parent.limit)
        self.axes.set_ylim(-self.parent.limit, self.parent.limit)
        #self.axes.xaxis.set_ticks_position('bottom')
        #self.axes.yaxis.set_ticks_position('left')
        
        
        self.axes.figure.canvas.draw()

    def do_background_sub(self):
        if self.back_patt == []:
            self.back_patt = make_profile_rings(self.parent.background - self.parent.background.min(), self.parent.drdf, self.origin, self.parent.boxs, True)
            #figure()
            #imshow(self.back_patt, cmap = 'gray')
            #show()
            print self.pattern_open_crop.shape, self.back_patt.shape, self.origin
            print self.parent.rdf.max(), self.back_patt.max(), self.pattern_open_crop.max(), self.parent.rdf_max
            
            middle_x = self.back_patt.shape[1]/2
            
            self.back_patt = self.back_patt * self.parent.rdf_max
            #figure()
            #plot(self.back_patt[:,middle_x])
            #plot(self.pattern_open_crop[:,middle_x])
            #line = self.pattern_open_crop[:,middle_x] - self.back_patt[:,middle_x]
            #plot(line)
            #line[line < 0] = 0
            #plot(line)
        
        self.pattern_open_crop = self.pattern_open_crop.astype(float32)

        self.pattern_open_crop -= self.back_patt
        #plot(self.pattern_open_crop[:,middle_x])
        self.pattern_open_crop[self.pattern_open_crop < 0] = 0
        #plot(self.pattern_open_crop[:,middle_x])
        #show()
        print self.pattern_open_crop.min(), self.pattern_open_crop.max()
        
    def do_plot_sim(self):
        sim_name = []
        marks = []
        color = ['#42D151','#2AA298','#E7E73C']
        marker = ['o','^','s']
        print len(self.parent.simulations)#, self.srdfb
        if len(self.parent.simulations) >= 3:
            sim_len_i = 3
        else:
            sim_len_i = len(self.parent.simulations)
        print sim_len_i#,self.srdfb[sim_len_i[0]],self.sdrdfb[sim_len_i[0]]
        for col_index, simulation in enumerate(self.parent.simulations[-sim_len_i:]):
            sim_color = simulation.sim_color if simulation.sim_color else color[col_index]
            sim_name += [simulation.sim_label]
            sim = simulation.srdf
            sim_norm = sim/float(max(sim))
            #print sim, max(sim[1:]), min(sim[1:]), sim_norm
            marks += [self.axes.plot(0,0,'-',color=sim_color, zorder = -10)[0]]
            rect = Rectangle((-self.parent.limit,-self.parent.limit),self.parent.limit,self.parent.limit, facecolor="none", edgecolor="none")
            self.axes.add_patch(rect)
            if not simulation.peak_index_labels:
                for radius in simulation.sdrdf:
                    #print radius
                    circ_mark = patches.Circle((0,0), radius, fill = 0 , color=sim_color, linewidth = 2, alpha=.7)
                    self.axes.add_patch(circ_mark)
                    circ_mark.set_clip_path(rect)
                    self.axes.set_autoscale_on(False)
                #sim_index = nonzero(self.srdfb[i]!=0)
            else:
                j=0
                for i,label in enumerate(simulation.peak_index_labels[::-1]):
                    #print label
                    if label:
                        circ_mark = patches.Circle((0,0), simulation.sdrdf[::-1][i], fill = 0 , color=sim_color, linewidth = 2, alpha=.7)
                        self.axes.add_patch(circ_mark)
                        circ_mark.set_clip_path(rect)
                        self.axes.set_autoscale_on(False)
                        
                        if label.find('-') == -1:
                            label = r'('+label+')'
                        else:
                            label = r'$\mathsf{('+label.replace('-',r'\bar ')+')}$'
                        #print label
                        bbox_props = dict(boxstyle="round", fc=sim_color, ec="0.5", alpha=1, lw=1.5)
                        arrowprops=dict(arrowstyle="wedge,tail_width=1.",
                            fc=sim_color, ec="0.5",
                            alpha=.7,
                            patchA=None,
                            patchB=circ_mark,
                            relpos=(0.5, 0.5),
                            )
                        an = self.axes.annotate(label, xy=(0, 0),xytext=(.1+col_index/10.0, .1+j/15.0),textcoords='axes fraction', ha="center", va="center", size=16, rotation=0, zorder = 90-col_index, picker=True,
                            bbox=bbox_props, arrowprops=arrowprops)
                        an.draggable()
                        j+=1

        print sim_name, marks 
        leg = self.axes.legend(marks , sim_name, loc='upper left', shadow=0, fancybox=True, numpoints=1, prop={'size':16})    
        frame = leg.get_frame()
        frame.set_alpha(0.7)
        for handle in leg.legendHandles:
            handle.set_linewidth(3.0)
            
    def do_prosim(self):
        if self.ring_patt == []:
            self.ring_patt = make_profile_rings(self.parent.prosim_int, self.parent.prosim_theta_2, self.origin, self.parent.boxs)
        self.axes.imshow(self.ring_patt[:,:self.ring_patt.shape[1]/2], cmap='gray', origin='lower',
            extent=(-self.parent.prosim_inv_d.max(), 0, -self.parent.prosim_inv_d.max(), self.parent.prosim_inv_d.max()))
        print self.parent.prosim_inv_d.max()

