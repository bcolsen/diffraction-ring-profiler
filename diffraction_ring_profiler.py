#!/usr/bin/env python
"""
This program will measure electron diffraction rings
and extract intensity profiles from the diffraction pattern.
This program averages the centers of the rings you mark to find the center of the pattern.
License: GPLv3 http://www.gnu.org/licenses/gpl.html
http://code.google.com/p/diffraction-ring-profiler/
"""
import wx
import os
import sys

pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname) 
os.chdir(fullpath)
args = sys.argv[1:] 

print fullpath + "/configs/"
os.environ['MPLCONFIGDIR'] = fullpath + "/configs/"


from numpy import *

import matplotlib
import Image
import TiffImagePlugin

import copy

matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg

from matplotlib.backends.backend_wx import _load_bitmap, cursord
from matplotlib.figure import Figure
from numpy.random import rand

from numpy import *
import scipy.constants as con
from scipy.ndimage.filters import median_filter

from matplotlib.pyplot import *
import matplotlib.patches as patches
import matplotlib.image as mpimg

import profile

from matplotlib import rc

import dm3lib_v099 as dm3

print matplotlib.get_configdir()


print args, fullpath
#with file('log.txt', 'w') as outfile:
#    outfile.write('# Args\n')
#    outfile.write(str(args))
    


rc('savefig', dpi=600)
rc("xtick", direction="out")
rc("ytick", direction="out")
rc("lines", markeredgewidth=1)

print "Welcome to Diffraction Ring Profiler. This program will measure electron diffraction rings"
print " and extract intensity profiles from the diffraction pattern."
print "This program averages the centers of the rings you mark to find the center of the pattern."


ID_ABOUT=101
ID_OPEN=102
ID_MARK=103
ID_INT=104
ID_UNDO=108
ID_PREF=109
ID_CAL=110
ID_PIX=111
ID_EXIT=200



class Circ:
    """
    Circles for ring markers
    """
    def __init__(self, parent, point3, axi):
        self.parent = parent
        
        self.point3 = point3[:]
        ax, ay = self.point3[0,:]
        bx, by = self.point3[1,:]
        cx, cy = self.point3[2,:]
        cird = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        cirx = ((ay**2 + ax**2) * (by - cy) + (by**2 + bx**2) * (cy - ay) + (cy**2 + cx**2) * (ay - by))/cird
        ciry = ((ay**2 + ax**2) * (cx - bx) + (by**2 + bx**2) * (ax - cx) + (cy**2 + cx**2) * (bx - ax))/cird
        cirr = sqrt((ax - cirx)**2 + (ay - ciry)**2)
        print 'circle radius=%f, circle x=%f, circle y=%f'%(cirr, cirx, ciry)

        self.center = (cirx, ciry)
        self.radius = cirr
        
        self.mark_circle(axi)
        
        self.label_circle(axi)
        
    def label_circle(self, axi):
        print self.parent.pixel_size #(self.parent.imgcal / 2.54) * 100, self.parent.wavelen, float(self.parent.camlen) / 100

        self.dspace = 1/(self.radius * self.parent.pixel_size)  #dspace in meters
        
        print self.dspace
        self.dspacestr = ur'%.2f \u00c5' % (self.dspace * 10**10)
        
        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.5)
        axi.text(self.point3[0,0], self.point3[0,1], self.dspacestr, ha="center", va="center", size=12,
            bbox=bbox_props)
            
    def mark_circle(self, axi):
        tri_mark = patches.Polygon(self.point3, closed=True, facecolor='red', alpha=0.7, linewidth = 2)
        circ_mark = patches.Circle(self.center, self.radius, fill = 0 , color='cyan', linewidth = 2, alpha=0.7)
        center_mark = axi.plot(self.center[0], self.center[1], 'g+')
        #axi.add_patch(tri)
        axi.add_patch(circ_mark)
        axi.set_autoscale_on(False)

class Line:
    """
    Lines for marking spots
    """
    def __init__(self, parent, point2, axi):
        self.parent = parent
        
        self.point2 = point2[:]
        ax, ay = self.point2[0,:]
        bx, by = self.point2[1,:]
        
        self.linelen = sqrt((ax - bx)**2 + (ay - by)**2)
        print 'line length=%f'%(self.linelen)
        
        self.mark_line(axi)
        
        self.label_line(axi)
        
    def label_line(self, axi):

        print self.parent.pixel_size #(self.parent.imgcal / 2.54) * 100, self.parent.wavelen, float(self.parent.camlen) / 100

        self.dspace = 1/(self.linelen * self.parent.pixel_size)  #dspace in meters
        
        print self.dspace
        self.dspacestr = ur'%.2f \u00c5' % (self.dspace * 10**10)
        
        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.5)
        axi.text(self.point2[0,0], self.point2[0,1], self.dspacestr, ha="center", va="center", size=12,
            bbox=bbox_props)
            
    def mark_line(self, axi):
        line_mark = patches.Polygon(self.point2, color='yellow', linewidth = 2, alpha=0.5)
        axi.add_patch(line_mark)
        axi.set_autoscale_on(False)

class Param:
    """
    The idea of the "Param" class is that some parameter in the GUI may have
    several knobs that both control it and reflect the parameter's state, e.g.
    a slider, text, and dragging can all change the value of the frequency in
    the waveform of this example.  
    The class allows a cleaner way to update/"feedback" to the other knobs when 
    one is being changed.  Also, this class handles min/max constraints for all
    the knobs.
    Idea - knob list - in "set" method, knob object is passed as well
      - the other knobs in the knob list have a "set" method which gets
        called for the others.
    """
    def __init__(self, initialValue=None, minimum=0., maximum=1.):
        self.minimum = minimum
        self.maximum = maximum
        if initialValue != self.constrain(initialValue):
            raise ValueError('illegal initial value')
        self.value = initialValue
        self.knobs = []
        
    def attach(self, knob):
        self.knobs += [knob]
        
    def set(self, value, knob=None):
        self.value = value
        self.value = self.constrain(value)
        for feedbackKnob in self.knobs:
            if feedbackKnob != knob:
                feedbackKnob.setKnob(self.value)
        return self.value

    def constrain(self, value):
        if value <= self.minimum:
            value = self.minimum
        if value >= self.maximum:
            value = self.maximum
        return value

class SliderGroup:
    def __init__(self, parent, label, param):
        
        self.panel = wx.Panel(parent, style=wx.SUNKEN_BORDER)
        
        self.parent = parent
        self.sliderLabel = wx.StaticText(self.panel, label=label)
        self.sliderText = wx.TextCtrl(self.panel, -1, style=wx.TE_PROCESS_ENTER)
        self.slider = wx.Slider(self.panel, -1, style=wx.SL_AUTOTICKS)
        self.slider.SetMax(param.maximum*1000)
        #self.slider.SetTick(1000)
        self.slider.SetTickFreq(1000, 1)
        self.setKnob(param.value)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.sliderLabel, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.sliderText, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=2)
        sizer.Add(self.slider, 1, wx.EXPAND)
        self.sizer = sizer
        
        self.panel.SetSizer(sizer)
        self.panel.Layout()
        
        self.slider.Bind(wx.EVT_SLIDER, self.sliderHandler)
        self.sliderText.Bind(wx.EVT_TEXT_ENTER, self.sliderTextHandler)

        self.param = param
        self.param.attach(self)

    def sliderHandler(self, evt):
        value = evt.GetInt() / 1000.
        self.param.set(value)
        
    def sliderTextHandler(self, evt):
        value = float(self.sliderText.GetValue())
        self.param.set(value)

    def repaint(self):
        self.parent.canvas.draw()

    def setKnob(self, value):
        if self.parent.pattern_open.any():
            pattern = self.parent.pattern_open
        elif self.parent.pattern.any():
            pattern = self.parent.pattern
            
        self.sliderText.SetValue('%g'%value)
        self.slider.SetValue(value*1000)
        #print value, self.parent.img_con.value
        gamma_pattern =  (pattern-pattern.min())**self.parent.img_con.value   #log(1+self.parent.img_con.value*pattern)
        #print pattern.max(), pattern.min()
        #print gamma_pattern.max(), gamma_pattern.min()
        self.parent.img.set_data(gamma_pattern)
        self.repaint()
            
class MyNavigationToolbar(NavigationToolbar2WxAgg):
    """
    Extend the default wx toolbar with mark_rings, profile, and undo
    """
    ON_MARKSPOTS = wx.NewId()
    ON_MARKRINGS = wx.NewId()
    ON_INTEGRATE = wx.NewId()
    ON_UNDO = wx.NewId()
    def __init__(self, parent, canvas, cankill, OnUndo):
        
        self.cid = 0
        self.circles = []
        self.point3 = array([])
        self.point2 = array([])
        self.lines = []
        self.hist = ['start']
        
        
        NavigationToolbar2WxAgg.__init__(self, canvas)
        
        self.statbar = None
        
        self.OnUndo = OnUndo
        self.parent = parent
        
        self.AddSeparator()
        
        self.AddCheckTool(self.ON_MARKRINGS, _load_bitmap(os.path.join(self.parent.iconspath, '3_point.png')),
                    shortHelp= 'Mark Rings',longHelp= "mark 3-points on a ring to find center")
        wx.EVT_TOOL(self, self.ON_MARKRINGS, self._on_markrings)
        self.AddCheckTool(self.ON_MARKSPOTS, _load_bitmap(os.path.join(self.parent.iconspath, '2_point.png')),
                    shortHelp= 'Mark Spots',longHelp= "mark 2 spots to measure distance")
        wx.EVT_TOOL(self, self.ON_MARKSPOTS, self._on_markspots)
        
        self.AddSeparator()
        
        self.AddSimpleTool(self.ON_INTEGRATE, _load_bitmap(os.path.join(self.parent.iconspath, 'profile.png')),
                        'Profile', 'Extract profiles from the diffraction pattern')
        wx.EVT_TOOL(self, self.ON_INTEGRATE, self._on_integrate)
        undo_ico = wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, (16,16))
        self.AddSimpleTool(self.ON_UNDO, undo_ico,
                        'Undo', 'Undo last point or ring')
        wx.EVT_TOOL(self, self.ON_UNDO, self._on_undo)
        
    def zoom(self, *args):
        self.ToggleTool(self._NTB2_PAN, False)
        self.ToggleTool(self.ON_MARKRINGS, False)
        self.ToggleTool(self.ON_MARKSPOTS, False)
        NavigationToolbar2WxAgg.zoom(self, *args)

    def pan(self, *args):
        self.ToggleTool(self._NTB2_ZOOM, False)
        self.ToggleTool(self.ON_MARKRINGS, False)
        self.ToggleTool(self.ON_MARKSPOTS, False)
        NavigationToolbar2WxAgg.pan(self, *args)
            
    def _on_markrings(self, evt):
        self.ToggleTool(self._NTB2_ZOOM, False)
        self.ToggleTool(self._NTB2_PAN, False)
        self.ToggleTool(self.ON_MARKSPOTS, False)
        #frame.canvas.mpl_disconnect(cid)
        print 'Select 3 points on a ring to mark it'
        #print self._active
        
        #cid = frame.canvas.mpl_connect('button_press_event', onclick)
        #frame.canvas.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))
        
        # set the pointer icon and button press funcs to the
        # appropriate callbacks

        if self._active == 'MARK':
            self._active = None
        else:
            self._active = 'MARK'
        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect(
                'button_press_event', self.onclick)
            self.mode = 'mark circles'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

            self.set_message(self.mode)

    def _on_markspots(self, evt):
        self.ToggleTool(self._NTB2_ZOOM, False)
        self.ToggleTool(self._NTB2_PAN, False)
        self.ToggleTool(self.ON_MARKRINGS, False)

        print 'Select 2 spots to measure the distance'
        #print self._active
        
        # set the pointer icon and button press funcs to the
        # appropriate callbacks

        if self._active == 'SPOT':
            self._active = None
        else:
            self._active = 'SPOT'
        if self._idPress is not None:
            self._idPress = self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._active:
            self._idPress = self.canvas.mpl_connect(
                'button_press_event', self.onclickspot)
            self.mode = 'mark spots'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

            self.set_message(self.mode)

    def _on_integrate(self, evt):
        print self.parent
        profile.integrate(self.parent, self.parent.pattern_open, self.circles, self.parent.pixel_size, self.parent.size)
        
    def _on_undo(self, evt):
        self.OnUndo(evt)
        
    def onclickspot(self, event):
        print self.point2.size
        if event.xdata != None and event.ydata != None:
            if not self.point2.size: self.point2 = array([event.xdata,event.ydata])
            else: self.point2 = vstack((self.point2, array([event.xdata,event.ydata])))
        
            print self.point2, self.point2.size
        
            axi = self.parent.canvas.figure.axes[0]
        
            axi.set_autoscale_on(False)
            point_mark = axi.plot(event.xdata, event.ydata, 'r+')
            #axi.set_ylim(0, size[0])
            axi.figure.canvas.draw()
            
            self.hist += ['point2']

        if self.point2.size >= 4:
            line = Line(self.parent, self.point2, axi)
            
            self.hist += ['line']
            
            if not len(self.lines): self.lines = [line]
            else: self.lines += [line]
            
            #axi.set_ylim(0, size[0])    
            axi.figure.canvas.draw()
            #frame.canvas.mpl_disconnect(cid)
            #frame.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            self.point2 = array([])
            
            #print "Press 'm' to mark more rings or 'enter' to integrate the pattern."
            
    def onclick(self, event):
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #    event.button, event.x, event.y, event.xdata, event.ydata)
        
        print self.point3.size
        if event.xdata != None and event.ydata != None:
            if not self.point3.size: self.point3 = array([event.xdata,event.ydata])
            else: self.point3 = vstack((self.point3, array([event.xdata,event.ydata])))
        
            print self.point3, self.point3.size
        
            axi = self.parent.canvas.figure.axes[0]
        
            axi.set_autoscale_on(False)
            point_mark = axi.plot(event.xdata, event.ydata, 'b+')
            #axi.set_ylim(0, size[0])
            axi.figure.canvas.draw()
            
            self.hist += ['point3']

        if self.point3.size >= 6:
            circle = Circ(self.parent, self.point3, axi)
            
            self.hist += ['circ']
            
            if not len(self.circles): self.circles = [circle]
            else: self.circles += [circle]
            
            #axi.set_ylim(0, size[0])    
            axi.figure.canvas.draw()
            #frame.canvas.mpl_disconnect(cid)
            #frame.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            self.point3 = array([])
            
            #print "Press 'm' to mark more rings or 'enter' to integrate the pattern."
            
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
                
            elif (self._active=='SPOT' and 
                    self._lastCursor != cursors.BULLSEYE):
                self.set_cursor(cursors.BULLSEYE)

                self._lastCursor = cursors.BULLSEYE    
                
        if event.inaxes and event.inaxes.get_navigate():

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

class diffaction_int(wx.Frame):

    def __init__(self, filename = None):
        
        self.fullpath = fullpath
        self.iconspath = os.path.join(self.fullpath,'icons')
        
        im = Image.open(os.path.join(self.iconspath, 'diff_profile_text.png'))
        im = im.convert('L')
        x_str = im.tostring('raw',im.mode,0,1)
        self.pattern = fromstring(x_str,uint8)
        self.pattern.shape = im.size[1], im.size[0]
        
        self.pattern_open = array([])
        self.size = self.pattern.shape
        self.camlen = 100
        self.accv = 200
        self.imgcal = 244
        #self.img_con = 0.05
        #self.img_con16 = 0.0001
        self.img_con = Param(1, minimum=0.01, maximum=1.9)
        accvm = self.accv * 1000
        self.wavelen = con.h/(sqrt(2 * con.m_e * con.e * accvm)) * 1/(sqrt(1 + (con.e * accvm)/(2 * con.m_e * con.c**2))) 
        self.PixelSize()
        print self.pixel_size
        
        wx.Frame.__init__(self,None,-1,
            'Diffraction Ring Profiler',size=(550,350))
        
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        iconFile = os.path.join(self.iconspath, "diff_profiler_ico.ico")
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)

        # dirname is an APPLICATION variable that we're choosing to store
        # in with the frame - it's the parent directory for any file we
        # choose to edit in this frame
        self.dirname = ''

        self.statbar = self.CreateStatusBar() # A Statusbar in the bottom of the window
        self.statbar.SetFieldsCount(2)
        self.statbar.SetStatusText("None", 1)
        
        # Setting up the menu. filemenu is a local variable at this stage.
        patternmenu= wx.Menu()
        # use ID_ for future easy reference - much better that "48", "404" etc
        # The & character indicates the short cut key
        patternmenu.Append(ID_OPEN, "&Open"," Open a file to edit")
        patternmenu.AppendSeparator()
        patternmenu.Append(ID_EXIT,"E&xit"," Terminate the program")
        
        # Setting up the menu. filemenu is a local variable at this stage.
        editmenu= wx.Menu()
        # use ID_ for future easy reference - much better that "48", "404" etc
        # The & character indicates the short cut key
        editmenu.Append(ID_UNDO, "&Undo"," Remove last point or circle")
        editmenu.AppendSeparator()
        editmenu.Append(ID_PREF,"&Preferences"," Edit Program Preferences")
        
        # Setting up the menu. filemenu is a local variable at this stage.
        toolsmenu= wx.Menu()
        # use ID_ for future easy reference - much better that "48", "404" etc
        # The & character indicates the short cut key
        toolsmenu.Append(ID_CAL, "&Calibrate"," Calibrate image resolution using marked rings and known d-spacing")
        toolsmenu.AppendSeparator()
        toolsmenu.Append(ID_PIX, "&Dead Pixel Fix"," Remove dead and hot pixels from the pattern")
        #toolsmenu.Append(ID_MARK, "&Mark Rings"," Mark diffraction rings to find the pattern center")
        toolsmenu.Append(ID_INT, "&Profile"," Extract profiles from the diffraction pattern")
                    
        # Setting up the menu. filemenu is a local variable at this stage.
        helpmenu= wx.Menu()
        # use ID_ for future easy reference - much better that "48", "404" etc
        # The & character indicates the short cut key
        helpmenu.Append(ID_ABOUT, "&About"," Information about this program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(patternmenu,"&Pattern") # Adding the "patternmenu" to the MenuBar
        menuBar.Append(editmenu,"&Edit")
        menuBar.Append(toolsmenu,"&Tools") # Adding the "patternmenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the "patternmenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        # Note - previous line stores the whole of the menu into the current object

        self.SetBackgroundColour(wx.NamedColor("WHITE"))

        self.figure = Figure(figsize=(8,8), dpi=76)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_aspect(1)
        
        #log_pattern = log(1+a*self.pattern)#/log(1+a*self.pattern).max()*255
        
        self.img = self.axes.imshow(self.pattern, cmap='gray', aspect='equal')
        #axi.set_xlim(0, size[1])
        #axi.set_ylim(0, size[0])
        #canvas = axi.figure.canvas
        self.axes.set_autoscale_on(False)
        self.axes.xaxis.set_ticks_position('bottom')
        self.axes.yaxis.set_ticks_position('left')
        
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.TOP | wx.LEFT | wx.EXPAND)
        # Capture the paint message
        wx.EVT_PAINT(self, self.OnPaint)

        self.toolbar = MyNavigationToolbar(self, self.canvas, True, self.OnUndo)
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
        
        self.img_conSliderGroup = SliderGroup(self, label='Image gamma:', param=self.img_con)
        self.sizer.Add(self.img_conSliderGroup.panel, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, border=0)
        
        # Define the code to be run when a menu option is selected
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_OPEN, self.OnOpen)
        #wx.EVT_MENU(self, ID_MARK, self.toolbar._on_markrings)    
        wx.EVT_MENU(self, ID_INT, self.toolbar._on_integrate)
        wx.EVT_MENU(self, ID_UNDO, self.OnUndo)
        wx.EVT_MENU(self, ID_PREF, self.OnPref)
        wx.EVT_MENU(self, ID_CAL, self.OnCal)
        wx.EVT_MENU(self, ID_PIX, self.OnPix)
        
        self.SetSizer(self.sizer)
        self.Fit()
        
        if filename:
            print filename[0]
            self.filename = filename[0]
            self.openimage()

    def PixelSize(self):
        self.pixel_size = 1/(((self.imgcal / 2.54) * 100) * self.wavelen * (float(self.camlen) / 100)) #computes 1/m per pixel
        #1/(2*sin(.5*(arctan((arange(B)*Dd)/((float(camlen) / 100)*((imgcal / 2.54) * 100))))))/(wavelen * 10**10)

    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()

    def OnAbout(self,e):

        info = wx.AboutDialogInfo()
        info.Name = "Diffraction Ring Profiler"
        info.Version = "1.2"
        info.Copyright = "(C) 2011 Brian Olsen"
        info.Description = "This program is for extracting intensity\n profiles from diffraction ring patterns\n"
        info.WebSite = ("http://code.google.com/p/diffraction-ring-profiler/", "Diffraction Ring Profiler Website")
        info.Developers = [ "Brian Olsen"]

        # change the wx.ClientDC to use self.panel instead of self
        info.License = 'Licensed under GPL 3.0 \n http://www.gnu.org/licenses/gpl.html'

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

#        self.aboutme = wx.MessageDialog( self, "This program is for extracting intensity\n"
#                    " profiles from diffraction ring patterns\n\n" "Diffraction Ring Profiler 1.2\n\n" 
#                    "(c) Brian Olsen, Licensed under GPL 3.0\n\n" "http://code.google.com/p/diffraction-ring-profiler/",
#                    "About Diffraction Ring Profiler", wx.OK)            
#        self.aboutme.ShowModal() # Shows it
        # widget / frame defined earlier so it can come up fast when needed

    def OnExit(self,e):
        # A modal with an "are you sure" check - we don't want to exit
        # unless the user confirms the selection in this case ;-)        
        self.doiexit = wx.MessageDialog( self, "Do you want to quit?\n",
                    "Warning", wx.YES_NO)
        igot = self.doiexit.ShowModal() # Shows it
        self.doiexit.Destroy()
        if igot == wx.ID_YES:
            self.Destroy()  # Closes out this simple application

    def OnOpen(self,e):
        # In this case, the dialog is created within the method because
        # the directory name, etc, may be changed during the running of the
        # application. In theory, you could create one earlier, store it in
        # your frame object and change it when it was called to reflect
        # current parameters / values
        dlg = wx.FileDialog(self, "Choose a diffraction image", self.dirname, "", "Image Files|*.tif;*.TIF;*.jpg;*.JPG;*.png;*.PNG;*.bmp;*.BMP;*.dm3;*.DM3|All Files|*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            self.openimage()
            print self.dirname
        dlg.Destroy()
        
    def openimage(self):
    
        self.toolbar.circles = []
        self.toolbar.point3 = array([])
        
        self.canvas.mpl_disconnect(self.toolbar.cid)
        if self.dirname == '':
            self.dirname, self.filename = os.path.split( self.filename )
        name, ext = os.path.splitext( self.filename )            
        print ext, name, self.dirname
        
        if ext=='.dm3' or ext=='.DM3':
            dm3f = dm3.DM3(os.path.join(self.dirname, self.filename))
            imageData = dm3f.getInfo()
            print imageData, dm3f.pxsize
            
            self.pattern_open = dm3f.getImageData()
            #self.pattern_open = array(self.pattern_open)
            self.pattern_open.shape
            #print self.pattern_open[[182],[1336]]
            a = self.img_con.value
            print imageData['mag'],imageData['hv']
            self.accv = int(float(imageData['hv'])/1000.0)
            if imageData['mode'] == 'DIFFRACTION':
                self.camlen = int(float(imageData['mag'])/10.0)
            print self.camlen, self.accv
            
            if dm3f.pxsize[0]:
                if dm3f.pxsize[1] == '1/nm':
                    self.pixel_size = dm3f.pxsize[0] * 10**9
                elif dm3f.pxsize[1] == '1/A':
                    self.pixel_size = dm3f.pxsize[0] * 10**10
                elif dm3f.pxsize[1] == '1/m':
                    self.pixel_size = dm3f.pxsize[0]
                print '.dm3 set pixel_size:', self.pixel_size
            else:
                self.PixelSize()
                print 'calculated pixel_size:', self.pixel_size
        else:
            im = Image.open(os.path.join(self.dirname, self.filename))
            Image._initialized=2
            
            if im.mode=='L':
                # return MxN luminance array
                x_str = im.tostring('raw',im.mode,0,1)
                self.pattern_open = fromstring(x_str,uint8)
                self.pattern_open.shape = im.size[1], im.size[0]
            elif im.mode=='I;16':
                # return MxN luminance array
                x_str = im.tostring('raw',im.mode,0,1)
                self.pattern_open = fromstring(x_str,uint16)
                self.pattern_open.shape = im.size[1], im.size[0]
            else:
                # return MxN luminance array
                try:
                    im = im.convert('L')
                    x_str = im.tostring('raw',im.mode,0,1)
                    self.pattern_open = fromstring(x_str,uint8)
                    self.pattern_open.shape = im.size[1], im.size[0]
                except ValueError:
                    dlg.Destroy()
                    error_file = 'Image file must be grayscale.'
                    print error_file
                    error_int_dlg = Error(self, -1, 'Error', error_file)
                    error_int_dlg.Show(True)
                    error_int_dlg.Centre()
                    self.axes.clear()
                    self.axes.imshow(self.pattern, cmap='gray', aspect='equal', origin='upper')
                    self.canvas.draw()
                    self.pattern_open = array([])
                    self.SetTitle("Diffraction Ring Profiler")
                    return

        #log_pattern = log(1+a*self.pattern_open)#/log(1+a*pattern).max()*255
        self.size = self.pattern_open.shape
        print 'shape: ', self.size
                    
        self.axes.clear()
        self.img = self.axes.imshow(self.pattern_open, cmap='gray', aspect='equal', origin='upper')
        self.axes.xaxis.set_ticks_position('bottom')
        self.axes.yaxis.set_ticks_position('left')
        self.canvas.draw()
        
        self.SetTitle("Diffraction Ring Profiler - "+self.filename)
        self.statbar.SetStatusText("CamL: {0} cm | AccV: {1} kV | Res: {2}".format(self.camlen, self.accv, self.imgcal), 0)
        self.img_con.set(1)



    def OnUndo(self,e):
        # Undo last point or circle
        
        print self.toolbar.point3.size
        print self.axes.lines
        print self.toolbar.hist
        
        undo = self.toolbar.hist[-1]

        if undo == 'start':
            print 'back to start'
        elif undo == 'circ':
            self.toolbar.circles.pop(-1)
            for circle in self.toolbar.circles:print circle.radius
            self.axes.patches.pop(-1)
            self.axes.texts.pop(-1)
            del self.axes.lines[-4:]
            del self.toolbar.hist[-4:]
            print self.toolbar.hist
            self.canvas.draw()
        elif undo == 'point3' and self.toolbar.point3.size == 2:
            self.toolbar.point3 = array([])
            print self.toolbar.point3
            self.axes.lines.pop(-1)
            self.canvas.draw()
            del self.toolbar.hist[-1:]
        elif undo == 'point3':
            self.toolbar.point3 = self.toolbar.point3[:-1,:]
            print self.toolbar.point3
            self.axes.lines.pop(-1)
            self.canvas.draw()
            del self.toolbar.hist[-1:]
        elif undo == 'line':
            self.axes.patches.pop(-1)
            self.axes.texts.pop(-1)
            del self.axes.lines[-2:]
            del self.toolbar.hist[-3:]
            print self.toolbar.hist
            self.canvas.draw()
        elif undo == 'point2':
            self.toolbar.point2 = array([])
            print self.toolbar.point2
            self.axes.lines.pop(-1)
            self.canvas.draw()
            del self.toolbar.hist[-1:]
        else:
            print 'undo error'
        
    def OnPix(self,e):
        std_cutoff = 80
        filter_size = 3
        self.pattern_open, num_filter, pattern_diff = self.filter_outliers(self.pattern_open, filter_size, std_cutoff)
        self.img.set_data(self.pattern_open)
        self.canvas.draw()
        print num_filter
        #figure()
        #imshow(pattern_diff, cmap='gray')
        #show()
        
    def filter_outliers(self, pattern, filter_size, std_cutoff):
        pattern[nonzero(pattern>1e9)] = 0
        pattern_filter = median_filter(pattern,size=filter_size)
        pattern_diff = pattern - pattern_filter
        pattern_index = nonzero(logical_or(-std(pattern_diff)*std_cutoff+pattern_diff.mean() > pattern_diff, pattern_diff > std(pattern_diff)*std_cutoff+pattern_diff.mean()))
        print pattern_index
        if pattern[pattern_index].any():
            pattern_final = np.copy(pattern)
            print pattern_final[pattern_index]
            num_filter = len(pattern_final[pattern_index])
            print num_filter
            pattern_final[pattern_index] = pattern_filter[pattern_index]
            pattern_diff_final = pattern - pattern_final
            print nonzero(pattern > pattern.max()*.8), pattern.max(), pattern_filter.max(), median(pattern_diff_final), (pattern_diff_final).max()
        else:
            pattern_final = copy(pattern)
            num_filter = 0
        return pattern_final, num_filter, pattern_diff

    def OnPref(self,e):
        dlg = Pref(self, -1, 'Preferences')
        dlg.Show(True)
        dlg.Centre()

    def OnCal(self,e):
        dlg = Cal(self, -1, 'Calibration')
        dlg.Show(True)
        dlg.Centre()

#def Message(axes, message):
#    bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.5)
#    axes.text(0, 0, message, ha="center", va="center", size=10,
#            bbox=bbox_props)
#    axes.figure.canvas.draw()

class Pref(wx.Dialog):
    def __init__(self, parent, id, title):
    
        self.parent = parent
        
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(350, 350))
        
        wx.StaticText(self, -1, 'Pattern Properties', (20,20))
        wx.StaticText(self, -1, 'Accelerating Voltage (kV): ', (20, 80))
        #wx.StaticText(self, -1, 'Wavelength (m): ', (20, 130))
        wx.StaticText(self, -1, 'Camera Length (cm): ', (20, 180))
        wx.StaticText(self, -1, 'Resolution (PPI): ', (20, 230))    
        
        wavelen_btn = wx.Button(self, 3, 'Wavelength (m):', (20, 125))
        self.wavelen_text = wx.StaticText(self, -1, '', (200, 130))
        self.accv_sc = wx.SpinCtrl(self, -1, '',  (200, 75), (60, -1))
        self.accv_sc.SetRange(1, 500)
        self.accv_sc.SetValue(self.parent.accv)        

        self.camlen_sc = wx.SpinCtrl(self, -1, '',  (200, 175), (60, -1))
        self.camlen_sc.SetRange(1, 5000)
        self.camlen_sc.SetValue(self.parent.camlen)

        self.imgcal_tc = wx.TextCtrl(self, -1, '',  (200, 225), (60, -1))
        imagecal_text = '%.2f' % (self.parent.imgcal)
        self.imgcal_tc.SetValue(imagecal_text)
    
        set_btn = wx.Button(self, 1, 'Set', (70, 275))
        set_btn.SetFocus()
        clear_btn = wx.Button(self, 2, 'Close', (185, 275))

        self.Bind(wx.EVT_BUTTON, self.OnSet, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnWavelen, id=3)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnWavelen(self, event):
        self.parent.accv = self.accv_sc.GetValue() * 1000
        self.parent.wavelen = con.h/(sqrt(2 * con.m_e * con.e * self.parent.accv)) * 1/(sqrt(1 + (con.e * self.parent.accv)/(2 * con.m_e * con.c**2)))
        wavelen_label = '%.3g m' % (self.parent.wavelen)
        print self.parent.wavelen
        self.wavelen_text.SetLabel(wavelen_label)
        
    def OnSet(self, event):
        
        circles = self.parent.toolbar.circles
        lines = self.parent.toolbar.lines
        
        self.parent.camlen = self.camlen_sc.GetValue()
        self.parent.accv = self.accv_sc.GetValue()
        accvm = self.parent.accv * 1000
        self.parent.wavelen = con.h/(sqrt(2 * con.m_e * con.e * accvm)) * 1/(sqrt(1 + (con.e * accvm)/(2 * con.m_e * con.c**2)))
        self.parent.imgcal = float(self.imgcal_tc.GetValue())
        
        self.parent.PixelSize()
        
        del self.parent.axes.texts[-len(circles)-len(lines):]
        
        for circle in circles:
            circle.label_circle(self.parent.axes)
                        
        for line in lines:
            line.label_line(self.parent.axes)
            
        self.parent.axes.figure.canvas.draw()
        self.parent.statbar.SetStatusText("CamL: {0} cm | AccV: {1} kV | Res: {2}".format(self.parent.camlen, self.parent.accv, self.parent.imgcal), 0)
        self.Destroy()
        
    def OnClose(self, event):
        self.Destroy()

class Cal(wx.Dialog):
    def __init__(self, parent, id, title):
        
        self.parent = parent
        
        self.radii = []
        self.circles = self.parent.toolbar.circles
        self.lines = self.parent.toolbar.lines
        
        for circle in self.circles:
            self.radii += [circle.radius]
        
        self.radii = array(self.radii)
        
        print self.radii.size
            
        au_radii = array([2.350,2.035,1.4390,1.2272])
        
        if self.radii.size == 0:
            self.radiilen = 0
        elif self.radii.size > 4:
            self.radiilen = 4
            window_height = 320 + 30 * self.radiilen
        else:
            self.radiilen = self.radii.size
            window_height = 320 + 30 * self.radiilen
        
        if self.radiilen != 0:
            self.radii.sort() 
            print self.radii[:self.radiilen]
        
            wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(350, window_height))

            wx.StaticText(self, -1, 'Calibrate image resolution using marked rings\nand known d-spacing in angstroms', (20,20))
            wx.StaticText(self, -1, 'Accelerating Voltage: ', (20, 80))
            wx.StaticText(self, -1, str(self.parent.accv) + ' kV', (200, 80))
            wx.StaticText(self, -1, 'Wavelength: ', (20, 110))
            wx.StaticText(self, -1, str('%.3g' % (self.parent.wavelen)) + ' m', (200, 110))
            wx.StaticText(self, -1, 'Camera Length: ', (20, 140))
            wx.StaticText(self, -1, str(self.parent.camlen) + ' cm', (200, 140))
            
            i = 1
            sp = 30
            for radius in self.radii[:self.radiilen]:
                wx.StaticText(self, -1, 'radius '+str(i)+':', (20, 170+sp*i))
                wx.StaticText(self, -1, str('%.2f' % radius) + ' pixels', (100, 170+sp*i))
                i += 1
                
            i = 1
            self.rad_ang_tc=[]                
            for au_radius in au_radii[:self.radiilen]:
                self.rad_ang_tc += [wx.TextCtrl(self, -1, '',  (200, 165+sp*i), (60, -1))]
                self.rad_ang_tc[i-1].SetValue(str(au_radius))        
                i += 1
            
            wx.StaticText(self, -1, 'Pattern Resolution (dpi): ', (20, window_height-100))
        
            self.imgcal_tc = wx.StaticText(self, -1, '',  (200, window_height-100), (60, -1))
            imagecal_text = '%.2f' % (self.parent.imgcal)
            self.imgcal_tc.SetLabel(imagecal_text)
        
            set_btn = wx.Button(self, 1, 'Calibrate', (70, window_height-55))
            set_btn.SetFocus()
            clear_btn = wx.Button(self, 2, 'Close', (185, window_height-55))

            self.Bind(wx.EVT_BUTTON, self.OnCal, id=1)
            self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
            self.Bind(wx.EVT_CLOSE, self.OnClose)
        else:
            wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(450, 125))
            wx.StaticText(self, -1, 'Please select one ring with a known d-spacing in angstroms', (20,20))
            clear_btn = wx.Button(self, 2, 'Close', (190, 75))
            self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            
    def OnCal(self, event):
        
        old_imgcal = copy(self.parent.imgcal)
        
        imgcals = []
        radius_angs = []
        for rad_tc in self.rad_ang_tc:
            radius_angs += [float(rad_tc.GetValue())]
        print radius_angs
        imgcals = (self.radii[:self.radiilen] * radius_angs * 10**-10 * 2.54)/((float(self.parent.camlen)/100.) * self.parent.wavelen * 100.)
        print imgcals    
        self.parent.imgcal = imgcals.mean()
        
        imagecal_text = '%.2f' % (self.parent.imgcal)
        self.imgcal_tc.SetLabel(imagecal_text)
        
        self.parent.PixelSize()
        
        del self.parent.axes.texts[-len(self.circles)-len(self.lines):]
        
        
        for circle in self.circles:
            circle.label_circle(self.parent.axes)
            
        for line in self.lines:
            line.label_line(self.parent.axes)
        
        self.parent.statbar.SetStatusText("CamL: {0} cm | AccV: {1} kV | Res: {2}".format(self.parent.camlen, self.parent.accv, self.parent.imgcal), 0)
        self.parent.axes.figure.canvas.draw()

#    def OnSave(self, event):
#        self.parent.cal_list =+ [{'name':cal_name, 'def': 0, 'value':self.parent.imgcal

    def OnClose(self, event):
        self.Destroy()
        
class App(wx.App):

    def OnInit(self):
        'Create the main window and insert the custom frame'
##Splash Screen
#        splashImage = nsc_bmp.getNscBmp()
#        wx.SplashScreen(splashImage, wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 1000, None, wx.ID_ANY)
#        wx.Yield()
#Main Window
        fileOpen = sys.argv[1:]
        frame = diffaction_int(fileOpen)
        frame.Show(True)
        return True
        
    
def main():
    app = App(redirect=False)
    app.MainLoop()
    return True

if __name__ == '__main__':
    main()        
#app = App(0)
#app.MainLoop()

