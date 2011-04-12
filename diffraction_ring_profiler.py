#!/usr/bin/env python
"""
This program will measure electron diffration rings
and extract intensity profiles from the diffraction pattern.
This program averages the centers of the rings you mark to find the center of the pattern.
"""

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

import wx
import os

from numpy import *
import scipy.constants as con

from matplotlib.pyplot import *
import matplotlib.patches as patches
import matplotlib.image as mpimg

from profile import *

from matplotlib import rc

from dm3reader import getDM3FileInfo

rc('savefig', dpi=600)
rc("xtick", direction="out")
rc("ytick", direction="out")
rc("lines", markeredgewidth=1)

pattern = mpimg.imread('diff_profile_text.png')
pattern_open = array([])
size = pattern.shape
camlen = 100
accv = 200
imgcal = 278.1
img_con = 0.05
img_con16 = 0.0001

print "Welcome to Diffraction Ring Profiler. This program will measure electron diffration rings"
print " and extract intensity profiles from the diffraction pattern."
print "This program averages the centers of the rings you mark to find the center of the pattern."


ID_ABOUT=101
ID_OPEN=102
ID_MARK=103
ID_INT=104
ID_UNDO=108
ID_PREF=109
ID_CAL=110
ID_EXIT=200

accvm = 200 * 1000
wavelen = con.h/(sqrt(2 * con.m_e * con.e * accvm)) * 1/(sqrt(1 + (con.e * accvm)/(2 * con.m_e * con.c**2))) 

cid = 0
count = 0
circles = []
point3 = array([])


def onclick(event):
    #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
    #    event.button, event.x, event.y, event.xdata, event.ydata)
    global cid
    global circles
    global point3
    
    print point3.size
    if event.xdata != None and event.ydata != None:
        if not point3.size: point3 = array([event.xdata,event.ydata])
        else: point3 = vstack((point3, array([event.xdata,event.ydata])))
    
        print point3, point3.size
    
        axi = frame.canvas.figure.axes[0]
    
        axi.set_autoscale_on(False)
        point_mark = axi.plot(event.xdata, event.ydata, 'b+')
        #axi.set_ylim(0, size[0])
        axi.figure.canvas.draw()

    if point3.size >= 6:
        circle = Circ(point3, axi)
        
        if not len(circles): circles = [circle]
        else: circles += [circle]
        
        #axi.set_ylim(0, size[0])    
        axi.figure.canvas.draw()
        #frame.canvas.mpl_disconnect(cid)
        #frame.canvas.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        point3 = array([])
        
        #print "Press 'm' to mark more rings or 'enter' to integrate the pattern."


class Circ:
    """
    Circles for ring markers
    """
    def __init__(self, point3, axi):
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
        print (imgcal / 2.54) * 100, wavelen, float(camlen) / 100

        self.dspace = ((imgcal / 2.54) * 100) * wavelen * (float(camlen) / 100) / self.radius
        
        print self.dspace
        self.dspacestr = ur'%.2f \u00c5' % (self.dspace * 10**10)
        
        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.5)
        axi.text(self.point3[0,0], self.point3[0,1], self.dspacestr, ha="center", va="center", size=10,
            bbox=bbox_props)
            
    def mark_circle(self, axi):
        tri_mark = patches.Polygon(self.point3, closed=True, facecolor='red', alpha=0.5)
        circ_mark = patches.Circle(self.center, self.radius, fill = 0 , color='cyan', linewidth = 1, alpha=0.3)
        center_mark = axi.plot(self.center[0], self.center[1], 'g+')
        #axi.add_patch(tri)
        axi.add_patch(circ_mark)
        axi.set_autoscale_on(False)
    
class MyNavigationToolbar(NavigationToolbar2WxAgg):
    """
    Extend the default wx toolbar with mark_rings, profile, and undo
    """
    ON_MARKRINGS = wx.NewId()
    ON_INTEGRATE = wx.NewId()
    ON_UNDO = wx.NewId()
    def __init__(self, parent, canvas, cankill, OnUndo):
        NavigationToolbar2WxAgg.__init__(self, canvas)
        
        self.statbar = None
        
        self.OnUndo = OnUndo
        self.parent = parent
        
        # for simplicity I'm going to reuse a bitmap from wx, you'll
        # probably want to add your own.
        self.AddCheckTool(self.ON_MARKRINGS, _load_bitmap('hand.png'),
                    shortHelp= 'Mark Rings',longHelp= "mark 3-points on a ring to find center")
        wx.EVT_TOOL(self, self.ON_MARKRINGS, self._on_markrings)
        self.AddSimpleTool(self.ON_INTEGRATE, _load_bitmap('stock_up.xpm'),
                        'Profile', 'Extract profiles from the diffraction pattern')
        wx.EVT_TOOL(self, self.ON_INTEGRATE, self._on_integrate)
        self.AddSimpleTool(self.ON_UNDO, _load_bitmap('stock_left.xpm'),
                        'Undo', 'Undo last point or ring')
        wx.EVT_TOOL(self, self.ON_UNDO, self._on_undo)
        
    def zoom(self, *args):
        self.ToggleTool(self._NTB2_PAN, False)
        self.ToggleTool(self.ON_MARKRINGS, False)
        NavigationToolbar2WxAgg.zoom(self, *args)

    def pan(self, *args):
        self.ToggleTool(self._NTB2_ZOOM, False)
        self.ToggleTool(self.ON_MARKRINGS, False)
        NavigationToolbar2WxAgg.pan(self, *args)
            
    def _on_markrings(self, evt):
        global cid
        global onclick
        self.ToggleTool(self._NTB2_ZOOM, False)
        self.ToggleTool(self._NTB2_PAN, False)
        #frame.canvas.mpl_disconnect(cid)
        print 'Select 3 points on a ring to mark it'
        print self._active
        
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
                'button_press_event', onclick)
            self.mode = 'mark circles'
            self.canvas.widgetlock(self)
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

            self.set_message(self.mode)

    def _on_integrate(self, evt):
        global integrate
        global centers
        print self.parent
        #print centers.size
        integrate(self.parent, pattern_open, circles, imgcal, wavelen, camlen, size)
        
    def _on_undo(self, evt):
        self.OnUndo(evt)
        
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

    def __init__(self):
        wx.Frame.__init__(self,None,-1,
            'Diffraction Ring Profiler',size=(550,350))
        
        self.Bind(wx.EVT_CLOSE, self.OnExit)


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
        toolsmenu.Append(ID_MARK, "&Mark Rings"," Mark diffraction rings to find the pattern center")
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
        
        #log_pattern = log(1+a*pattern)#/log(1+a*pattern).max()*255
        
        self.axes.imshow(pattern, cmap='gray', aspect='equal')
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
        
        # Define the code to be run when a menu option is selected
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_OPEN, self.OnOpen)
        wx.EVT_MENU(self, ID_MARK, self.toolbar._on_markrings)    
        wx.EVT_MENU(self, ID_INT, self.toolbar._on_integrate)
        wx.EVT_MENU(self, ID_UNDO, self.OnUndo)
        wx.EVT_MENU(self, ID_PREF, self.OnPref)
        wx.EVT_MENU(self, ID_CAL, self.OnCal)
        
        self.SetSizer(self.sizer)
        self.Fit()


    def OnPaint(self, event):
        self.canvas.draw()
        event.Skip()

    def OnAbout(self,e):
        # A modal show will lock out the other windows until it has
        # been dealt with. Very useful in some programming tasks to
        # ensure that things happen in an order that  the programmer
        # expects, but can be very frustrating to the user if it is
        # used to excess!
        self.aboutme = wx.MessageDialog( self, " This program is for extracting intensity\n"
                    " profiles from diffraction ring patterns","About Diffraction Ring Profiler", wx.OK)            
        self.aboutme.ShowModal() # Shows it
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
            
            print self.dirname
            
            global circles
            global pattern_open
            global size
            global point3
            global count
            global cid
            global camlen
            global wavelen
            global imgcal
            global accv
            
            count = 0
            circles = []
            point3 = array([])
            
            self.canvas.mpl_disconnect(cid)
            
            name, ext = os.path.splitext( self.filename )            
            #print count, centers, circle
            print ext
            
            if ext=='.dm3' or ext=='.DM3':
                imageData, pattern_open = getDM3FileInfo(os.path.join(self.dirname, self.filename), return_array=True)
                pattern_open = array(pattern_open)
                pattern_open.shape = int(imageData['y_res']), int(imageData['x_res'])
                #print pattern_open[[182],[1336]]
                a = img_con16
                print imageData['mag'],imageData['hv']
                accv = int(float(imageData['hv'])/1000.0)
                if imageData['mode'] == 'DIFFRACTION':
                    camlen = int(float(imageData['mag'])/10.0)
                print camlen, accv
            else:
                im = Image.open(os.path.join(self.dirname, self.filename))
                Image._initialized=2
                
                if im.mode=='L':
                    # return MxN luminance array
                    x_str = im.tostring('raw',im.mode,0,1)
                    pattern_open = fromstring(x_str,uint8)
                    pattern_open.shape = im.size[1], im.size[0]
                    a = img_con
                elif im.mode=='I;16':
                    # return MxN luminance array
                    x_str = im.tostring('raw',im.mode,0,1)
                    pattern_open = fromstring(x_str,uint16)
                    pattern_open.shape = im.size[1], im.size[0]
                    a = img_con16
                else:
                    # return MxN luminance array
                    try:
                        im = im.convert('L')
                        x_str = im.tostring('raw',im.mode,0,1)
                        pattern_open = fromstring(x_str,uint8)
                        pattern_open.shape = im.size[1], im.size[0]
                        a = img_con
                    except ValueError:
                        dlg.Destroy()
                        error_file = 'Image file must be grayscale.'
                        print error_file
                        error_int_dlg = Error(frame, -1, 'Error', error_file)
                        error_int_dlg.Show(True)
                        error_int_dlg.Centre()
                        self.axes.clear()
                        self.axes.imshow(pattern, cmap='gray', aspect='equal')
                        self.canvas.draw()
                        pattern_open = array([])
                        self.SetTitle("Diffraction Ring Profiler")
                        return

            log_pattern = log(1+a*pattern_open)#/log(1+a*pattern).max()*255
            size = pattern_open.shape
                        
            self.axes.clear()
            self.axes.imshow(log_pattern, cmap='gray', aspect='equal', origin='upper')
            self.axes.xaxis.set_ticks_position('bottom')
            self.axes.yaxis.set_ticks_position('left')
            self.canvas.draw()
            
            # Report on name of latest file read
            self.SetTitle("Diffraction Ring Profiler - "+self.filename)
            # Later - could be enhanced to include a "changed" flag whenever
            # the text is actually changed, could also be altered on "save" ...
            dlg.Destroy()

    def OnUndo(self,e):
        # Undo last point or circle
        global point3
        global circles
        global cid
        global axi

        print point3.size
        print self.axes.lines

        if point3.size == 0 and len(circles) == 0 and cid:
            self.canvas.mpl_disconnect(cid)
        elif point3.size == 0 and len(circles) != 0:
            circles.pop(-1)
            for circle in circles:print circle.radius
            self.axes.patches.pop(-1)
            self.axes.texts.pop(-1)
            del self.axes.lines[-4:]
            print self.axes.lines
            self.canvas.draw()
        elif point3.size == 2:
            point3 = array([])
            print point3
            self.axes.lines.pop(-1)
            self.canvas.draw()
            self.canvas.mpl_disconnect(cid)
        else:
            point3 = point3[:-1,:]
            print point3
            self.axes.lines.pop(-1)
            self.canvas.draw()    
        
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
    
        global camlen
        global wavelen
        global imgcal
        global accv
        
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(350, 320))
        
        wx.StaticText(self, -1, 'Pattern Properties', (20,20))
        wx.StaticText(self, -1, 'Accelerating Voltage (kV): ', (20, 80))
        #wx.StaticText(self, -1, 'Wavelength (m): ', (20, 130))
        wx.StaticText(self, -1, 'Camera Length (cm): ', (20, 180))
        wx.StaticText(self, -1, 'Resolution (dpi): ', (20, 230))    
        
        wavelen_btn = wx.Button(self, 3, 'Wavelength (m):', (20, 125))
        self.wavelen_text = wx.StaticText(self, -1, '', (200, 130))
        self.accv_sc = wx.SpinCtrl(self, -1, '',  (200, 75), (60, -1))
        self.accv_sc.SetRange(1, 500)
        self.accv_sc.SetValue(accv)        

        self.camlen_sc = wx.SpinCtrl(self, -1, '',  (200, 175), (60, -1))
        self.camlen_sc.SetRange(1, 5000)
        self.camlen_sc.SetValue(camlen)

        self.imgcal_tc = wx.TextCtrl(self, -1, '',  (200, 225), (60, -1))
        imagecal_text = '%.2f' % (imgcal)
        self.imgcal_tc.SetValue(imagecal_text)
    
        set_btn = wx.Button(self, 1, 'Set', (70, 275))
        set_btn.SetFocus()
        clear_btn = wx.Button(self, 2, 'Close', (185, 275))

        self.Bind(wx.EVT_BUTTON, self.OnSet, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnWavelen, id=3)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnWavelen(self, event):
        accv = self.accv_sc.GetValue() * 1000
        self.wavelen = con.h/(sqrt(2 * con.m_e * con.e * accv)) * 1/(sqrt(1 + (con.e * accv)/(2 * con.m_e * con.c**2)))
        wavelen_label = '%.3g m' % (self.wavelen)
        print self.wavelen
        self.wavelen_text.SetLabel(wavelen_label)
        
    def OnSet(self, event):
        global camlen
        global wavelen
        global imgcal
        global accv
        
        camlen = self.camlen_sc.GetValue()
        accv = self.accv_sc.GetValue()
        accvm = accv * 1000
        wavelen = con.h/(sqrt(2 * con.m_e * con.e * accvm)) * 1/(sqrt(1 + (con.e * accvm)/(2 * con.m_e * con.c**2)))
        imgcal = float(self.imgcal_tc.GetValue())
        
        del frame.axes.texts[-len(circles):]
        
        for circle in circles:
            circle.label_circle(frame.axes)
            
        frame.axes.figure.canvas.draw()
        
        self.Destroy()
        
    def OnClose(self, event):
        self.Destroy()

class Cal(wx.Dialog):
    def __init__(self, parent, id, title):
    
        global camlen
        global wavelen
        global imgcal
        global accv
        global circles
        
        self.radii = []
        
        for circle in circles:
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
            wx.StaticText(self, -1, str(accv) + ' kV', (200, 80))
            wx.StaticText(self, -1, 'Wavelength: ', (20, 110))
            wx.StaticText(self, -1, str('%.3g' % (wavelen)) + ' m', (200, 110))
            wx.StaticText(self, -1, 'Camera Length: ', (20, 140))
            wx.StaticText(self, -1, str(camlen) + ' cm', (200, 140))
            
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
        
            self.imgcal_tc = wx.TextCtrl(self, -1, '',  (200, window_height-105), (60, -1))
            imagecal_text = '%.2f' % (imgcal)
            self.imgcal_tc.SetValue(imagecal_text)
        
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
        global camlen
        global wavelen
        global imgcal
        
        old_imgcal = copy(imgcal)
        
        imgcals = []
        radius_angs = []
        for rad_tc in self.rad_ang_tc:
            radius_angs += [float(rad_tc.GetValue())]
        print radius_angs
        imgcals = (self.radii[:self.radiilen] * radius_angs * 10**-10 * 2.54)/((float(camlen)/100.) * wavelen * 100.)
        print imgcals    
        imgcal = imgcals.mean()
        
        imagecal_text = '%.2f' % (imgcal)
        self.imgcal_tc.SetValue(imagecal_text)
        
        del frame.axes.texts[-len(circles):]
        
        for circle in circles:
            circle.label_circle(frame.axes)
            
        frame.axes.figure.canvas.draw()

    def OnClose(self, event):
        self.Destroy()
        
class App(wx.App):

    def OnInit(self):
        'Create the main window and insert the custom frame'
        global frame
        frame = diffaction_int()
        frame.Show(True)

        return True

        
app = App(0)
app.MainLoop()

