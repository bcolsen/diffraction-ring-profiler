#!/usr/bin/python

# sim_index.py
from numpy import *
import wx
import wx.lib.scrolledpanel as scrolled
      
class Sim_Index(scrolled.ScrolledPanel):

    def __init__(self, parent, simulation, color):
        scrolled.ScrolledPanel.__init__(self, parent, id = -1,  style = wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        
        sim_color = simulation.sim_color if simulation.sim_color else color
        
        self.sdrdf = simulation.sdrdf#[2.5,1.5,1,.8,2.5,1.5,1,.8,2.5,1.5,1,.8,2.5,1.5,1,.8]
        self.sdrdflen = len(self.sdrdf)
        
        self.srdf = simulation.srdf

        #fcc_sim = [111,122,220,400,111,122,220,400,111,122,220,400,111,122,220,400]
        self.peak_index_labels = simulation.peak_index_labels

        wx.StaticText(self, -1, 'Legend Label: ', (20, 5))

        self.sim_label_tc = wx.TextCtrl(self, -1, '',  (130, 0), (130, -1))
        sim_label_text = simulation.sim_label
        self.sim_label_tc.SetValue(sim_label_text)

        wx.StaticText(self, -1, 'Simulation Intensity: ', (20, 35))

        self.sim_intens_tc = wx.TextCtrl(self, -1, '',  (200, 30), (60, -1))
        sim_intens_text = str(simulation.sim_intens)
        self.sim_intens_tc.SetValue(sim_intens_text)		
        
        wx.StaticText(self, -1, 'Simulation Color: ', (20, 65))
        
        self.colorpicker = wx.ColourPickerCtrl(self, -1, colour=sim_color, pos=(200, 60),
                 size=(60, 30), name='Simulation Color')
        #self.sim_color_tc = wx.TextCtrl(self, -1, '',  (150, 60), (90, -1))
        #self.colorDlgBtn = wx.Button(self,  -1, "...",  (240, 60), (20, -1))
        #self.colorDlgBtn.Bind(wx.EVT_BUTTON, self.onColorDlg)
        #self.sim_color_tc.SetValue('#ffffff')		
        
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        offset = 4
        sp = 30
        i = offset
        for peak, intens in zip(self.sdrdf,self.srdf):
            static = wx.StaticText(self, -1, str(i-offset+1) + '-', (20, sp*i+5))
            static1 = wx.StaticText(self, -1, 'd:', (60, sp*i+5))
            dspace = 1/peak
            wx.StaticText(self, -1, str('%.2f' % dspace) + u' \u00c5', (75, sp*i+5))
            
            static2 = wx.StaticText(self, -1,'i:', (140, sp*i+5))
            wx.StaticText(self, -1, str('%.2f' % intens), (153, sp*i+5))
            i += 1

        vbox.Add((250,sp*i+5), wx.EXPAND, 0)

        if len(self.peak_index_labels)==0:		
            i = offset
            self.peak_index_tc=[]				
            for peak_index_label in self.sdrdf:
                self.peak_index_tc += [wx.TextCtrl(self, -1, '',  (200, sp*i), (60, -1))]
                #self.peak_index_tc[i-1].SetValue(str(au_radius))		
                i += 1
        else:
            i = offset
            self.peak_index_tc=[]				
            for peak_index_label in self.peak_index_labels[:self.sdrdflen]:
                self.peak_index_tc += [wx.TextCtrl(self, -1, '',  (200, sp*i), (60, -1))]
                self.peak_index_tc[i-offset].SetValue(str(peak_index_label))		
                i += 1

        self.SetSizer(vbox)
        self.SetupScrolling()
        
#    def onColorDlg(self, event):
#        """
#        This is mostly from the wxPython Demo!
#        """
#        dlg = wx.ColourDialog(self)
# 
#        # Ensure the full colour dialog is displayed, 
#        # not the abbreviated version.
#        dlg.GetColourData().SetChooseFull(True)
# 
#        if dlg.ShowModal() == wx.ID_OK:
#            data = dlg.GetColourData()
#            self.sim_color_tc.SetValue('#%02x%02x%02x' % data.GetColour().Get())
#            print ('#%02x%02x%02x' % data.GetColour().Get())
# 
#        dlg.Destroy()

class Index(wx.Dialog):
    def __init__(self, parent, id, title):

        window_height = 500
        wx.Dialog.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(350, window_height))

        wx.StaticText(self, -1, 'Enter or edit the peak indices and title\nfor the imported simulations', (20,20))
			
        nb = wx.Notebook(self, -1, pos = (25, 70), size = (300, 350), style=wx.NB_TOP)

        self.parent = parent
        self.simulations = parent.simulations

        if len(self.simulations) >= 3:
            sim_len_i = 3
        else:
            sim_len_i = len(self.simulations)
        print(sim_len_i)#,self.srdfb[sim_len_i[0]],self.sdrdfb[sim_len_i[0]])
        
        color = ['#42D151','#2AA298','#E7E73C']
        
        for i, simulation in enumerate(self.simulations[-sim_len_i:]):
            sim = Sim_Index(nb,simulation,color[i])
            simulation.sim_tcs = sim
            nb.AddPage(sim, simulation.sim_name)

        set_btn = wx.Button(self, 1, 'Edit Labels', (70, window_height-55))
        set_btn.SetFocus()
        clear_btn = wx.Button(self, 2, 'Cancel', (185, window_height-55))

        self.Bind(wx.EVT_BUTTON, self.OnIndex, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnIndex(self, event):
        if len(self.simulations) >= 3:
            sim_len_i = 3
        else:
            sim_len_i = len(self.simulations)
        print(sim_len_i)#,self.srdfb[sim_len_i[0]],self.sdrdfb[sim_len_i[0]])
        for simulation in self.simulations[-sim_len_i:]:	
            peak_index_labels = []

            for peak_index_tc in simulation.sim_tcs.peak_index_tc:
                peak_index_labels += [peak_index_tc.GetValue()]
            print(simulation.sim_tcs.colorpicker.GetColour(), simulation.sim_tcs.colorpicker.GetColour()[0:3])
            simulation.edit_index_labels(peak_index_labels, simulation.sim_tcs.sim_label_tc.GetValue(), simulation.sim_tcs.sim_intens_tc.GetValue(), simulation.sim_tcs.colorpicker.GetColour())
        self.Destroy()

        self.parent.axes.cla()
        self.parent.plot(2,'b')		

        self.parent.axes.figure.canvas.draw()

    def OnClose(self, event):
        self.Destroy()


class Simulation:
    """
    Simulation label and index
    """
    def __init__(self, sim_open, sim_name):
        c_index = nonzero(sim_open==20)
        if len(c_index[0]) == 25:
            sim_open[nonzero(sim_open==20)] = 0
            print(c_index, c_index[0][12], c_index[1][2])
            Cs = [c_index[1][2],c_index[0][12]]

            Nx = sim_open.shape[1]
            Ny = sim_open.shape[0]
            print(Cs, Cs[0], Cs[1])		
            boxx = (Nx - Cs[0])-2
    #		boxy = Ny/2. - abs(Ny/2. - Cs[1])-2
    #		if boxx <= boxy:
    #			boxs = floor(boxx)
    #		else:
    #			boxs = floor(boxy)

            boxs = int(boxx)
            #print(boxs)

            Cr = copy(Cs)

            #print(Cr[1],Cr[1]+boxs,Cr[0])
            sim_open -= 40
            sim_open[nonzero(sim_open>=195)] = 0
            #print(sim_open)
            srdf = sim_open[Cr[1],Cr[0]:Cr[0]+boxs]
            #self.srdfb += [self.srdf.copy()]
            #cens_pattern[:4]=0
            #print(self.srdf.shape, self.srdf, sim_open.shape)
            wavelen = 2.50793394487e-12
            camlen = 400
            imgcal = 72 #(radii[0] * radius_angs * 10**-10 * 2.54)/((float(camlen)/100.) * self.wavelen * 100.)
            sdrdf = (arange(boxs))/(((imgcal / 2.54) * 100) * wavelen * (float(camlen) / 100) * 10**10)
            #self.sdrdfb += [self.sdrdf.copy()]
            self.sim_intens = 0.7
            print(srdf, srdf.max())
            srdf = srdf/float(srdf.max())
            sim_index = nonzero(srdf!=0)
            
            sdrdf = sdrdf[sim_index]
            srdf = srdf[sim_index]
            
            srdf = srdf/sdrdf**1.5
            
        else:
            theta_2 = sim_open[:,0]
            inv_d = (2*sin(((theta_2/180)*pi)/2.))/.5
            
            intensity = sim_open[:,1]
            intensity /= intensity.max()

            print(sim_open.shape, len(theta_2), len(intensity))

            srdf = intensity
            sdrdf = inv_d
            self.sim_intens = 1
        
            sim_index = nonzero(srdf!=0)

            sdrdf = sdrdf[sim_index]
            srdf = srdf[sim_index]
            
        self.sdrdf = sdrdf
        self.srdf = srdf
        
        self.sim_name = sim_name
        self.sim_label = sim_name
        
        self.peak_index_labels = []
        self.sim_tcs = []
        self.sim_color = 0

        #print(1/array(sim_scatter))

        #print(imgcal)

        #filen=(simname + '.txt')
        #data = loadtxt(filen,skiprows=0)
        ##print(data)

        #srdf = data[:,1]
        #sdrdf = data[:,0]

        #start =20
        #dsdrdf = linspace(0,sdrdf[-1],boxs)

        print(self.sdrdf, self.srdf)

    def edit_index_labels(self, index_labels, sim_label, sim_intens, sim_color):
        self.peak_index_labels = index_labels
        self.sim_label = sim_label
        self.sim_intens = float(sim_intens)
        self.sim_color = '#%02x%02x%02x' % sim_color[0:3]

#app = wx.App()
#dlg = Index(None, -1, 'Index Peaks')
#dlg.Show(True)
#app.MainLoop()
