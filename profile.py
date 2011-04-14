#!/usr/bin/env python
"""
Calculates and displays diffraction pattern profiles
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

import time
class Timer():
   def __enter__(self): self.start = time.time()
   def __exit__(self, *args): print time.time() - self.start

from matplotlib import rc

rc('savefig', dpi=600)
rc("xtick", direction="out")
rc("ytick", direction="out")
rc("lines", markeredgewidth=1)

ID_SAVE=105
ID_LABEL=106
ID_SUB=107
ID_RECEN=111
ID_CLRP=112
ID_PUN=113
ID_POL=114
ID_SIM=115
ID_SIML=116
ID_PPREF=117
ID_CLRS=118
ID_BSC=119

global radframe
global centers

def integrate(frame, pattern_open, circles, imgcal, wavelen, camlen, size):
    
    global radframe
    print frame
    if pattern_open.any(): 
        if circles:
            print 'Integration started. please wait...'
            radframe = radial(frame, pattern_open, circles, imgcal, wavelen, camlen, size)
            radframe.Show(True)
        else:
            error_cir = 'Please mark at lease one ring.'
            print error_cir
            error_int_dlg = Error(frame, -1, 'Error', error_cir)
            error_int_dlg.Show(True)
            error_int_dlg.Centre()
    else:
        error_pat = 'Please open a diffraction image file.'
        print error_pat
        error_int_dlg = Error(frame, -1, 'Error', error_pat)
        error_int_dlg.Show(True)
        error_int_dlg.Centre()
            
class Error(wx.Dialog):
    def __init__(self, parent, id, title, message):
        wx.Dialog.__init__(self, parent, -1, 'Integrate', wx.DefaultPosition, wx.Size(450, 125))
        wx.StaticText(self, -1, message, (20,20))
        clear_btn = wx.Button(self, 2, 'Close', (190, 75))
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def OnClose(self, event):
        self.Destroy()
            
class MyNavigationToolbar2(NavigationToolbar2WxAgg):
    """
    Extend the default wx toolbar with your own event handlers
    """
    ON_LABELPEAKS = wx.NewId()
    ON_CLEAR = wx.NewId()
    ON_UNDO = wx.NewId()
    def __init__(self, parent, canvas, cankill):
        NavigationToolbar2WxAgg.__init__(self, canvas)
        
        self.parent = parent
        
        self.AddCheckTool(self.ON_LABELPEAKS, _load_bitmap('hand.png'),
                shortHelp= 'Label Peaks',longHelp= 'Click on a peak to label the d-spacing')
        wx.EVT_TOOL(self, self.ON_LABELPEAKS, self._on_labelpeaks)
        self.AddSimpleTool(self.ON_CLEAR, _load_bitmap('stock_down.xpm'),
                        'Clear Profiles', 'Clear all except the last profile')
        wx.EVT_TOOL(self, self.ON_CLEAR, self._on_clear)
        self.AddSimpleTool(self.ON_UNDO, _load_bitmap('stock_left.xpm'),
                        'Undo', 'Go back to the previous profile')
        wx.EVT_TOOL(self, self.ON_UNDO, self._on_undo)
        
    def zoom(self, *args):
        self.ToggleTool(self._NTB2_PAN, False)
        self.ToggleTool(self.ON_LABELPEAKS, False)
        NavigationToolbar2WxAgg.zoom(self, *args)

    def pan(self, *args):
        self.ToggleTool(self._NTB2_ZOOM, False)
        self.ToggleTool(self.ON_LABELPEAKS, False)
        NavigationToolbar2WxAgg.pan(self, *args)

    def _on_labelpeaks(self, evt):
        print 'Select peaks to label'
        
        self.ToggleTool(self._NTB2_ZOOM, False)
        self.ToggleTool(self._NTB2_PAN, False)
        
        #eid = radframe.canvas.mpl_connect('button_press_event', onclick_lable)
        
        if self._active == 'MARK':
            self._active = None
        else:
            self._active = 'MARK'
        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect(
                'button_press_event', self.parent.onclick_lable)
            self.mode = 'label peaks'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

            self.set_message(self.mode)
        

    def _on_subtract(self, evt):
        self.parent.bgfitp = array([])
        print 'Select points on the background'
        try:
            #print self.fid
            if self.fid != None:
                self.fid = self.canvas.mpl_disconnect(self.fid)
            self.fid = self.canvas.mpl_connect('button_press_event', self.parent.onclick_fitback)
        except AttributeError:
            self.fid = self.canvas.mpl_connect('button_press_event', self.parent.onclick_fitback)
        #print self.fid
        
    def _on_clear(self, evt):
        self.parent.OnClearPro(evt)
        
    def _on_undo(self, evt):
        self.parent.OnUndo(evt)


    def mouse_move(self, event):
        #print 'mouse_move', event.button

        if not event.inaxes or not self._active:
            if self._lastCursor != cursors.POINTER:
                self.set_cursor(cursors.POINTER)
                self._lastCursor = cursors.POINTER
        else:
            if self._active=='ZOOM':
                if self._lastCursor != cursors.SELECT_REGION:
                    self.set_cursor(cursors.SELECT_REGION)
                    self._lastCursor = cursors.SELECT_REGION
                if self._xypress:
                    x, y = event.x, event.y
                    lastx, lasty, a, ind, lim, trans = self._xypress[0]
                    self.draw_rubberband(event, x, y, lastx, lasty)
            elif (self._active=='PAN' and
                    self._lastCursor != cursors.MOVE):
                self.set_cursor(cursors.MOVE)

                self._lastCursor = cursors.MOVE

            elif (self._active=='MARK' and 
                    self._lastCursor != cursors.BULLSEYE):
                self.set_cursor(cursors.BULLSEYE)

                self._lastCursor = cursors.BULLSEYE    
                
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

# cursors
class Cursors:  #namespace
    HAND, POINTER, SELECT_REGION, MOVE, BULLSEYE = range(5)
cursors = Cursors()

#print cursord
cursord = {
    cursors.MOVE : wx.CURSOR_HAND,
    cursors.HAND : wx.CURSOR_HAND,
    cursors.POINTER : wx.CURSOR_ARROW,
    cursors.SELECT_REGION : wx.CURSOR_CROSS,
    cursors.BULLSEYE : wx.CURSOR_BULLSEYE,        
    }
    
print cursord

class radial(wx.Frame):

    def __init__(self, parent, pattern_open, circles, imgcal, wavelen, camlen, size):
        wx.Frame.__init__(self,parent,-1,
            "Intensity Profile - "+parent.filename ,size=(550,350))
                
        iconFile = "diff_profiler_ico.ico"
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        
        self.SetIcon(icon1)
        self.simulations = []
        self.plot_sim = 0
        
        self.dirname = parent.dirname
        self.filename = parent.filename
        self.parent = parent
        self.pattern_open = pattern_open
        self.circles = circles
        self.imgcal = imgcal 
        self.wavelen = wavelen
        self.camlen = camlen
        self.plot_polar = 0
        self.show_polar = 1
        self.limit = 0
        self.gamma = 0.1        
        self.latex = 0
        self.polar_neg = 1
        self.angstrom = u'\u00c5'
            
        # dirname is an APPLICATION variable that we're choosing to store
        # in with the frame - it's the parent directory for any file we
        # choose to edit in this frame
        self.dirname = ''

        self.statbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
        self.statbar.SetFieldsCount(2)
        self.statbar.SetStatusText("None", 1)
        
        # Setting up the menu. filemenu is a local variable at this stage.
        intmenu= wx.Menu()
        # use ID_ for future easy reference - much better than "48", "404" etc
        # The & character indicates the short cut key
        intmenu.Append(ID_SIM, "&Import Simulation"," Open a Desktop Microscopist simulation")
        intmenu.Append(ID_SAVE, "&Export Data"," Export Profile Data to a text file")
        
        # Setting up the menu. filemenu is a local variable at this stage.
        editmenu= wx.Menu()
        # use ID_ for future easy reference - much better than "48", "404" etc
        # The & character indicates the short cut key
        editmenu.Append(ID_PUN, "&Undo Profile"," Go back to the previous profile")        
        editmenu.Append(ID_SIML, "Simulation &Labels"," Edit simulation labels and indices")
        editmenu.Append(ID_PPREF, "&Profile Prefrences"," Edit profile prefrences and limits")        
        editmenu.Append(ID_CLRP, "&Clear Profiles"," Clear all except the last profile")        
        editmenu.Append(ID_CLRS, "&Remove Simulation"," Remove the last simulation")
        
        # Setting up the menu. filemenu is a local variable at this stage.
        toolsmenu= wx.Menu()
        # use ID_ for future easy reference - much better than "48", "404" etc
        # The & character indicates the short cut key
        toolsmenu.Append(ID_LABEL, "&Label Peaks"," Label peak on the diffraction")
        toolsmenu.Append(ID_SUB, "&Background Subtract"," Subtract background from the diffraction")
        toolsmenu.Append(ID_RECEN, "&Recenter(Sharpen Peaks)"," Sharpen profile peaks by recentering")
        toolsmenu.Append(ID_POL, "&Polar Pattern"," Display polar pattern to compare with the profile")        
        toolsmenu.Append(ID_BSC, "Beam Stop &Correction"," Use the polar pattern to correct for a beam stopper")
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(intmenu,"&Profile") # Adding the "patternmenu" to the MenuBar
        menuBar.Append(editmenu,"&Edit")
        menuBar.Append(toolsmenu,"&Tools") # Adding the "patternmenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        # Note - previous line stores the whole of the menu into the current object
        
        self.SetBackgroundColour(wx.NamedColor("WHITE"))

        self.figure = Figure(dpi=76)
        self.axes = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        # Capture the paint message
        wx.EVT_PAINT(self, self.OnPaint)

        self.toolbar = MyNavigationToolbar2(self, self.canvas, True)
        self.toolbar.Realize()
        if wx.Platform == '__WXMAC__':
            # Mac platform (OSX 10.3, MacPython) does not seem to cope with
            # having a toolbar in a sizer. This work-around gets the buttons
            # back, but at the expense of having the toolbar at the top
            self.SetToolBar(self.toolbar)
        else:
            # On Windows platform, default window size is incorrect, so set
            # toolbar width to figure width.
            tw, th = self.toolbar.GetSizeTuple()
            fw, fh = self.canvas.GetSizeTuple()
            # By adding toolbar in sizer, we are able to put it at the bottom
            # of the frame - so appearance is closer to GTK version.
            # As noted above, doesn't work for Mac.
            self.toolbar.SetSize(wx.Size(fw, th))
            self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()
        
        # Define the code to be run when a menu option is selected
        wx.EVT_MENU(self, ID_SAVE, self.OnSave)
        wx.EVT_MENU(self, ID_SIM, self.OnSimOpen)
        wx.EVT_MENU(self, ID_LABEL, self.toolbar._on_labelpeaks)    
        wx.EVT_MENU(self, ID_SUB, self.toolbar._on_subtract)
        wx.EVT_MENU(self, ID_RECEN, self.OnRecenter)
        wx.EVT_MENU(self, ID_CLRP, self.OnClearPro)
        wx.EVT_MENU(self, ID_PUN, self.OnUndo)
        wx.EVT_MENU(self, ID_POL, self.OnPolar)
        wx.EVT_MENU(self, ID_SIML, self.OnSimLabel)
        wx.EVT_MENU(self, ID_PPREF, self.OnPro_Pref)
        wx.EVT_MENU(self, ID_CLRS, self.OnClearSim)        
        wx.EVT_MENU(self, ID_BSC, self.OnBeamStop)                    
        self.SetSizer(self.sizer)
        self.Fit()

        self.center(pattern_open, circles, imgcal, wavelen, camlen)
        self.plot()
    
    def center(self, pattern_open, circles, imgcal, wavelen, camlen):
        
        centers = array([])
        dspace = []
        
        for circle in circles:
            if not centers.size: centers = array([circle.center])
            else: centers = vstack((centers, array([circle.center])))
            dspace += [circle.dspace]
        
        dspace = array(dspace)* 10**10    
        dspace.sort()
        print 1/dspace[-1]
        
        C = centers[:].sum(axis=0)/centers[:].shape[0]
        self.C = C
        print centers, C
        
        self.intensity(pattern_open, C, imgcal, wavelen, camlen)
        
        self.rdfb = [self.rdf.copy()]
        self.drdfb = [self.drdf.copy()]
        
    def OnRecenter(self, event):
        centers = array([])
        dspace = []
        
        for circle in self.circles:
            if not centers.size: centers = array([circle.center])
            else: centers = vstack((centers, array([circle.center])))
            dspace += [circle.dspace]
        
        dspace = array(dspace)* 10**10    
        dspace.sort()
        print 1/dspace[-1]
        
        C = centers[:].sum(axis=0)/centers[:].shape[0]
        
        print centers, C
        
        self.intensity(self.pattern_open, C, self.imgcal, self.wavelen, self.camlen)
        self.plot(3,'r')
        
        search_range = 2
        divs = [[2,'g'],[1,'c'],[.5,'m']]
        dialog = wx.ProgressDialog('Recentering (May take a few minutes)', 
                'Depending on the size of your image this may take a few minutes.', maximum = 27, parent = self)
        x = 0
        y = 0
        for div in divs:
            dialog.Update ( x + 1, 'On Division ' + str ( y + 1 ) + ' of ' + str(len(divs)) + '.' )
            clin = (arange(search_range + 1) - search_range/2) * div[0]
            C_arrayx = ones((search_range + 1,search_range + 1)) * (C[0] + clin).reshape(-1,1)
            C_arrayy = ones((search_range + 1,search_range + 1)) * (C[1] + clin)    
            C_array = c_[C_arrayx.reshape(-1,1),C_arrayy.reshape(-1,1)]
            #print div, clin, C_array
            peak=[]
            
            for cen in C_array:
                self.intensity(self.pattern_open, cen, self.imgcal, self.wavelen, self.camlen)
                peak_i = self.peak_fit(1/dspace[-1])
                #print self.peak_parab[peak_i]
                peak += [self.peak_parab[peak_i]]
                self.plot(1,div[1])
                dialog.Update ( x + 1 )
                x += 1
                
            peak = array(peak)
            index = nonzero(peak == peak.max())
        
            print peak, peak.max(), C_array[index]
            C = C_array[index][0]
            self.C = C
            y += 1
            
        self.intensity(self.pattern_open, C_array[index][0], self.imgcal, self.wavelen, self.camlen)
        
        self.rdfb += [self.rdf.copy()]
        self.drdfb += [self.drdf.copy()]
        
        self.plot_polar = 0
        
        self.plot(5,'k')        
        self.axes.figure.canvas.draw()
            
    def intensity(self, pattern_open, C, imgcal, wavelen, camlen):
        
        Nx = pattern_open.shape[1]
        Ny = pattern_open.shape[0]
        print C, C[0], C[1]        
        boxx = Nx/2. - abs(Nx/2. - C[0])-2
        boxy = Ny/2. - abs(Ny/2. - C[1])-2
        if boxx <= boxy:
            boxs = floor(boxx)
        else:
            boxs = floor(boxy)
            
        self.boxs = boxs
    
        B = int(floor(boxs/2))
        Dd = boxs/B
        rdf = zeros((B))
    
        #x = random.rand(N)*lx
        #y = random.rand(N)*ly
        
        print Nx, Ny, boxs, Dd, C, len(range(Nx)), len(range(Ny))
        
        y = ((ones((Ny,Nx)) * arange(Ny).reshape(-1,1)) - C[1])**2
        x = ((ones((Ny,Nx)) * arange(Nx)) - C[0])**2
        with Timer():
            d = around(sqrt(x + y)/Dd)
        #print d.shape

        r = arange(B)
        #print d, pattern_open/255.
        with Timer():
            self.rdf, bin_edge = histogram(d, bins = B, range=(0,B-1), weights=pattern_open/float(pattern_open.max()))
        #print rdf, rdf.size, bin_edge, bin_edge.size

        r[0] = 1
        self.rdf /= r
                
        self.drdf = (arange(B)*Dd)/(((imgcal / 2.54) * 100) * wavelen * (float(camlen) / 100) * 10**10)
        
        #print self.rdf
        #print self.rdf, self.drdf , len(self.rdf), len(self.drdf)
        
    def plot(self, lw=1, col='b'):
        
        if self.latex:
            rc('text', usetex=True)
            rc('font', family='serif')
            self.angstrom = r'\AA'
        else:
            rc('text', usetex=False)
            rc('font', family='sans-serif')
            self.angstrom = u'\u00c5'
        
        self.rdf /= self.rdf.max()
            
        self.axes.plot(self.drdf, self.rdf, c=col, alpha=1, linewidth=lw, zorder = 50)
        self.axes.set_title('Diffraction Pattern Intensity Profile')
        self.axes.set_xlabel('Scattering Vector (1/'+self.angstrom+')')
        self.axes.set_ylabel('Intensity')
        self.axes.set_yticks([])
        #print "Press 'm' mark peaks."
        #axi2.set_xlim(0,5)
        if self.plot_polar and self.show_polar:
            if self.polar_neg: cmap='binary'
            else: cmap='gray'
            #print cmap, self.polar_neg
            log_polar = rot90(log(1+self.gamma*self.polar_grid))
            self.axes.imshow(log_polar, cmap=cmap, origin='lower',
                extent=(0, self.drdf.max(), 0, self.rdf.max()+self.rdf.max()*.2))
                    
        if self.plot_sim:
            points = []
            sim_name = []
            col_index = 0
            color = ['#2AA298','#E7E73C','#42D151']
            marker = ['o','^','s']
            print len(self.simulations)#, self.srdfb
            if len(self.simulations) >= 3:
                sim_len_i = 3
            else:
                sim_len_i = len(self.simulations)
            print sim_len_i#,self.srdfb[sim_len_i[0]],self.sdrdfb[sim_len_i[0]]
            for simulation in self.simulations[-sim_len_i:]:
                sim_name += [simulation.sim_label]
                sim = simulation.srdf/simulation.sdrdf**1.5
                sim_norm = sim/float(max(sim))
                #print sim, max(sim[1:]), min(sim[1:]), sim_norm
                self.axes.vlines(simulation.sdrdf, 0, sim_norm*simulation.sim_intens, color[col_index] ,linewidth = 2, zorder = 2)
                #sim_index = nonzero(self.srdfb[i]!=0)
                points += [self.axes.plot(simulation.sdrdf, sim_norm*simulation.sim_intens, marker[col_index],  c=color[col_index], ms = 8, zorder = 3)]
                i=0
                for label in simulation.peak_index_labels:
                    #print label
                    bbox_props = dict(boxstyle="round", fc=color[col_index], ec="0.5", alpha=0.7)
                    self.axes.text(simulation.sdrdf[i], sim_norm[i]*simulation.sim_intens + .05, label, ha="center", va="bottom", size=10, rotation=90, zorder = 100,
                        bbox=bbox_props)
                    i+=1
                col_index += 1
        
            print sim_name, points 
            leg = self.axes.legend(points , sim_name, loc='upper right', shadow=0, fancybox=True, numpoints=1)    
            frame = leg.get_frame()
            frame.set_alpha(0.4)
        
        if not self.limit: self.limit = self.drdf.max()
        
        self.axes.axis('auto')
        self.axes.set_xlim(0, self.limit+0.0001)
        self.axes.set_ylim(0, self.rdf.max()+self.rdf.max()*.2)
        self.axes.xaxis.set_ticks_position('bottom')
        self.axes.yaxis.set_ticks_position('left')
        show()
        #self.axes.figure.canvas.draw()
        
    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()

    def OnSave(self,e):
    # Save away the edited text
    # Open the file, do an RU sure check for an overwrite!
        filename = os.path.splitext(self.filename)
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, filename[0] + '.txt', "*.*", \
            wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            # Grab the content to be saved
            #itcontains = self.control.GetValue()
            
            
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            with file(os.path.join(self.dirname, self.filename), 'w') as outfile:
                data = array([self.rdf, self.drdf])
                outfile.write('# Pattern Center\n')
                savetxt(outfile, self.C.reshape((1,-2)))
                outfile.write('# Pattern Profile {0}\n'.format(data.shape))
                savetxt(outfile, rot90(data ,k=3))
                if self.plot_sim:
                    if len(self.simulations) >= 3:
                        sim_len_i = 3
                    else:
                        sim_len_i = len(self.simulations)
                    simulation = self.simulations[-sim_len_i]
                    sim = simulation.srdf/simulation.sdrdf**1.5
                    sim_norm = sim/float(max(sim))
                    #print sim, max(sim[1:]), min(sim[1:]), sim_norm
                    #simulation.sdrdf, 0, sim_norm*simulation.sim_intens, color[col_index] ,linewidth = 2, zorder = 2)
                    sim = array([sim_norm*simulation.sim_intens, simulation.sdrdf])
                    outfile.write('# Pattern Simulation {0}\n'.format(sim.shape))
                    print sim.shape, sim
                    savetxt(outfile, rot90(sim ,k=3))
            # Open the file for write, write, close
#            self.filename=dlg.GetFilename()
#            self.dirname=dlg.GetDirectory()
#            filehandle=open(os.path.join(self.dirname, self.filename),'w')
#            filehandle.write(itcontains)
#            filehandle.close()
            # Get rid of the dialog to keep things tidy
            dlg.Destroy()
        
    def onclick_lable(self,event):
        #global eid
        #global radframe
        
        num_inter = 40
        text_offset = 0.07
        
        axi2 = self.canvas.figure.axes[0]
                
        print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
            event.button, event.x, event.y, event.xdata, event.ydata)
        ax = event.xdata
        ay = event.ydata
        
        peak_i = self.peak_fit(ax, num_inter = num_inter)
        
        axi2.set_autoscale_on(False)
        axi2.plot(self.t, self.peak_parab)
        
        if peak_i == 0 or peak_i == num_inter-1:
            peak = ax
            text_pos = self.peak_parab[abs(self.t - peak).argmin(0)]+text_offset
        else:
            peak = self.t[peak_i]
            text_pos = self.peak_parab[peak_i]+text_offset
        
        dspace = 1/peak
        print dspace
        
        axi2.plot(peak, text_pos-text_offset, 'b+')
        
        dspace_str = '%.2f' % dspace + self.angstrom
        bbox_props = dict(boxstyle="round", fc="c", ec="0.5", alpha=0.5)
        axi2.text(peak, text_pos, dspace_str, ha="center", va="bottom", size=10, rotation=90,
            bbox=bbox_props)
        axi2.figure.canvas.draw()
        #radframe.canvas.mpl_disconnect(eid)
        #print "Press 'm' mark additional peaks."    
    
    def peak_fit(self, ax, poly_degree = 4, fit_range = 2, num_inter = 40):
        
        points = abs(self.drdf - ax)
        i = points.argmin(0)
        
        if self.plot_polar:
            fit_range = 4
        
        #print self.drdf, ax, self.drdf[i-fit_range:i+fit_range+1]
        
        # form the Vandermonde matrix
        A = vander(self.drdf[i-fit_range:i+fit_range+1], poly_degree)
 
        # find the x that minimizes the norm of Ax-y
        (coeffs, residuals, rank, sing_vals) = linalg.lstsq(A, self.rdf[i-fit_range:i+fit_range+1])
 
        # create a polynomial using coefficients
        parab = poly1d(coeffs)
        
        self.t = linspace(self.drdf[i-fit_range],self.drdf[i+fit_range],num_inter)
        
        self.peak_parab = parab(self.t)
        
        return parab(self.t).argmax(0)
        
    def onclick_fitback(self,event):
        
        axi2 = self.canvas.figure.axes[0]
        
        print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
            event.button, event.x, event.y, event.xdata, event.ydata)
        ax = event.xdata
        
        points = abs(self.drdf - ax)
        i = points.argmin(0)
            
        if event.xdata != None and event.ydata != None and event.button == 1:
            if not self.bgfitp.size: self.bgfitp = array([ax,self.rdf[i]])
            else: self.bgfitp = vstack((self.bgfitp, array([ax,self.rdf[i]])))
    
            print self.bgfitp, self.bgfitp.size
    
            axi2.set_autoscale_on(False)
            point_mark = axi2.plot(ax, self.rdf[i], 'b+')
            #axi.set_ylim(0, size[0])
            axi2.figure.canvas.draw()

        if self.bgfitp.size >= 6:
    
            r = self.bgfitp[:,0]
            d = self.bgfitp[:,1]
            
            def func(d,p):
                return(p[0]*d**(-p[1]))
    
            def residuals(p, r, d):
                err = r - func(d, p)
                return err
           
            p0 = [10,1] # initial guesses
            guessfit = func(self.drdf,p0)
            pbest = leastsq(residuals,p0,args=(d,r),full_output=1)
            
            bestparams = pbest[0]
            cov_x = pbest[1]
            print 'best fit parameters ',bestparams
            print cov_x
        
            datafit = func(self.drdf,bestparams)
            
            #if plot_sub:
            #    axi2.lines.pop(-2)
            #    axi2.figure.canvas.draw()
            
            plot_sub = axi2.plot(self.drdf,datafit,'r')
            
            axi2.figure.canvas.draw()
            
            self.rdf -= datafit
            
            start = nonzero(self.rdf>0)[0][0]
            
            print self.rdf[start:].min()
            
            self.rdf -= self.rdf[start:].min()
            
            self.rdf[0:start] = 0
            
            self.rdfb += [self.rdf.copy()]
            self.drdfb += [self.drdf.copy()]
            
            axi2.plot(self.drdf,self.rdf,'k')
            
            axi2.figure.canvas.draw()
            
            self.bgfitp = array([])
            print self.toolbar.fid
            self.toolbar.fid = self.canvas.mpl_disconnect(self.toolbar.fid)
            print self.toolbar.fid
    def OnClearPro(self,e):
        self.axes.cla()
        
        self.plot(2)
        self.axes.figure.canvas.draw()
        
    def OnClearSim(self,e):
    
        self.simulations.pop(-1)
        if len(self.simulations) <= 0:
            self.plot_sim = 0
        
        self.axes.cla()
        
        self.plot(2)
        self.axes.figure.canvas.draw()    
                
            
    def OnUndo(self,e):
        axi2 = self.canvas.figure.axes[0]
        
        axi2.cla()
        print len(self.rdfb), len(self.rdfb[-1]), len(self.drdfb[-1])
        if len(self.rdfb) > 1:
            print self.rdfb[-1]
            self.rdfb.pop(-1)
            self.drdfb.pop(-1)
        print len(self.rdfb), len(self.rdfb[-1]), len(self.drdfb[-1]) , self.rdfb[-1]
        self.rdf = self.rdfb[-1].copy()
        self.drdf = self.drdfb[-1].copy()
            
        self.plot(2)
        axi2.figure.canvas.draw()
        
    def OnPolar(self,e):
        self.axes.cla()
        #plot_polar_pattern(self.pattern_open, self.C, self.boxs, self.rdf, self.drdf)
        origin =  [self.C[1], self.C[0]]
    
        polar_grid, r, theta, pmrdf, self.psrdf = reproject_image_into_polar(self.pattern_open, origin, self.boxs)
        self.plot_polar = 1
        
        self.polar_grid = polar_grid

        rdf = array(self.rdf)
        drdf = array(self.drdf)
        #print pmrdf.shape, psrdf.max()
        self.dpmrdf = linspace(drdf.min(), drdf.max(), pmrdf.shape[0])
        #print dpmrdf.shape
    
        rdf /= rdf.max()
        pmrdf /= pmrdf.max()
        self.psrdf /= self.psrdf.max()
        
        self.rdf = rdf
        self.drdf = drdf
        
        self.rdfb += [self.rdf.copy()]
        self.drdfb += [self.drdf.copy()]
        
        self.plot(2,'b')        
        
        self.rdf = pmrdf
        self.drdf = self.dpmrdf
        
        self.rdfb += [self.rdf.copy()]
        self.drdfb += [self.drdf.copy()]
        
        self.plot(2,'r')
        
        #self.rdf = self.psrdf
        #self.drdf = dpmrdf
        
        #self.rdfb += [self.rdf.copy()]
        #self.drdfb += [self.drdf.copy()]        
        
        #self.plot(2,'g')        
        
        self.axes.figure.canvas.draw()
    def OnBeamStop(self,e):
        if not self.plot_polar:
            self.OnPolar(e)
        self.rdf = self.psrdf
        self.drdf = self.dpmrdf
        
        self.rdfb += [self.rdf.copy()]
        self.drdfb += [self.drdf.copy()]        
        
        self.plot(2,'g')
        
        self.axes.figure.canvas.draw()
                
    def OnSimOpen(self,e):
        # In this case, the dialog is created within the method because
        # the directory name, etc, may be changed during the running of the
        # application. In theory, you could create one earlier, store it in
        # your frame object and change it when it was called to reflect
        # current parameters / values
        dlg = wx.FileDialog(self, "Choose a Desktop Microscopist ring simulation screen shot(cropped tif) with camera length of 400cm & 200kV",
            self.dirname, "", "TIF|*.tif;*.TIF|All Files|*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            
            img_con = 0.05
            img_con16 = 0.0001
                        
            filename=dlg.GetFilename()
            dirname=dlg.GetDirectory()
            
            print dirname
            
            #print count, centers, circle
            
            im = Image.open(os.path.join(dirname, filename))
            
            name, ext = os.path.splitext(filename)
            
            #self.sim_nameb += [name]
            
            Image._initialized=2

            if im.mode=='L':
                # return MxN luminance array
                x_str = im.tostring('raw',im.mode,0,-1)
                sim_open = fromstring(x_str,uint8)
                sim_open.shape = im.size[1], im.size[0]
                a = img_con
            elif im.mode=='I;16':
                # return MxN luminance array
                x_str = im.tostring('raw',im.mode,0,-1)
                sim_open = fromstring(x_str,uint16)
                sim_open.shape = im.size[1], im.size[0]
                a = img_con16
            else:
                # return MxN luminance array
                try:
                    im = im.convert('L')
                    x_str = im.tostring('raw',im.mode,0,-1)
                    sim_open = fromstring(x_str,uint8)
                    sim_open.shape = im.size[1], im.size[0]
                    a = img_con
                except ValueError:
                    dlg.Destroy()
                    error_file = 'Image file must be grayscale.'
                    print error_file
                    error_int_dlg = Error(self, -1, 'Error', error_file)
                    error_int_dlg.Show(True)
                    error_int_dlg.Centre()
                    return
            
            c_index = nonzero(sim_open==20)
            print len(c_index[0])
            if len(c_index[0]) == 25:
                self.simulations += [Simulation(sim_open, name)]
                
                self.plot_sim = 1
                
                self.axes.cla()
                self.plot(2,'b')        
                
                self.axes.figure.canvas.draw()
                
                dlg.Destroy()
            else:
                dlg.Destroy()
                error_file = 'Image must be a Digital Microscopist screen shot.'
                print error_file
                error_int_dlg = Error(self, -1, 'Error', error_file)
                error_int_dlg.Show(True)
                error_int_dlg.Centre()
    
    def OnSimLabel(self,e):
        dlg = Index(self, -1, 'Index Peaks')
        dlg.Show(True)
        
    def OnPro_Pref(self,e):
        dlg = Pro_Pref(self, -1, 'Profile Preferences')
        dlg.Show(True)
        dlg.Centre()

class Pro_Pref(wx.Dialog):
    def __init__(self, parent, id, title):
    
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(350, 350))
        
        self.parent = parent
        
        wx.StaticText(self, -1, u'Scattering Vector Limit (1/\u00c5): ', (20, 20))
        #wx.StaticText(self, -1, 'Latex Text Rendering: ', (20, 70))
        #wx.StaticText(self, -1, 'Show Polar Pattern: ', (20, 120))
        #wx.StaticText(self, -1, 'Polar Pattern Negative: ', (20, 170))    
        wx.StaticText(self, -1, 'Polar Pattern Gamma: ', (20, 220))
        
        limit_string =     '%.2f' % self.parent.limit    
        self.limit_tc = wx.TextCtrl(self, -1, '',  (250, 15), (60, -1))
        self.limit_tc.SetValue(limit_string)        

        self.latex_cb = wx.CheckBox(self, -1, 'Latex Text Rendering', (20, 65))
        self.latex_cb.SetValue(self.parent.latex)
        
        self.polar_cb = wx.CheckBox(self, -1, 'Show Polar Pattern', (20, 115))
        self.polar_cb.SetValue(self.parent.show_polar)
        
        self.polar_neg_cb = wx.CheckBox(self, -1, 'Polar Pattern Negative', (20, 165))
        self.polar_neg_cb.SetValue(self.parent.polar_neg)
        
        self.gamma_tc = wx.TextCtrl(self, -1, '',  (250, 215), (60, -1))
        self.gamma_tc.SetValue(str(self.parent.gamma))                    
        
        set_btn = wx.Button(self, 1, 'Set', (70, 275))
        set_btn.SetFocus()
        close_btn = wx.Button(self, 2, 'Close', (185, 275))

        self.Bind(wx.EVT_BUTTON, self.OnSet, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def OnSet(self, event):
        
        self.parent.limit = float(self.limit_tc.GetValue())
        self.parent.latex = self.latex_cb.GetValue()
        self.parent.show_polar = self.polar_cb.GetValue()
        self.parent.polar_neg = self.polar_neg_cb.GetValue()
        self.parent.gamma = float(self.gamma_tc.GetValue())
        
        #print self.parent.polar_neg
        
        self.parent.axes.cla()
        self.parent.plot(2)            
        self.parent.axes.cla()
        self.parent.plot(2)
        self.parent.axes.figure.canvas.draw()
        self.Destroy()
        
    def OnClose(self, event):
        self.Destroy()

