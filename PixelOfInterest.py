from PIL import ImageTk
import os, io 
import Flipbook
import PIL
import PIL.Image
if os.sys.version_info.major > 2:
    from tkinter import *
    from tkinter.filedialog import askdirectory
else:
    from tkinter import *
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog   import asksaveasfilename

 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTk, NavigationToolbar2Tk
from matplotlib.figure import Figure


import matplotlib.pyplot as plt
import numpy
import math



       
class PixOI: 
    # class for ROI selection
    def __init__(self,root,plotframe,FPS):

        # tuple holding the edges of the ROI selection! 
        
        self.pixelbox = (0,0,0,0)
        self.root = root # Tk() root 
        #self.roiseq = None # cropped image sequence
        

        # helper variables
        self.anchor = None  
        self.item = None  
        self.bbox = None  
        self.win = None # Toplevel() toplevel window  
        self.plotframe = plotframe 
        self.fps = FPS 
        
        
        self.fig = Figure(figsize=(6,5), dpi=100)
        self.ax1 = None
        self.ax = None 
        self.counter = 0 


    def pixelplots(self, roiseq):
        
        
        #self.fig.clear() 
        #if self.ax1 is not None:
        #    self.ax1.clear() 
 
        
        # row and column of clicked pixel : 
        pix_j = int(self.anchor[0]) 
        pix_i = int(self.anchor[1])
 
        nimgs = 160
    
        timeaxis = numpy.zeros(nimgs)
        
        
        ixy = numpy.zeros(nimgs) 
        
        firstimg = roiseq[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        #nimgs = len(roiseq) # number of images   
   
        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs),int(height),int(width)))  

        #array = numpy.array(array,dtype=float) 

        
        for i in range(nimgs):
            #array[i,:,:] = float(numpy.array(roiobj.roiseq[i]))   
            array[i,:,:] = numpy.array(roiseq[i])
            timeaxis[i] = i * (float(self.fps))**(-1)
    
        for t in range(nimgs):
            ixy[t] = array[t,pix_i,pix_j]
    
        
        
        
        
        if (self.counter == 0):
            self.ax1 = self.fig.add_subplot(211) 
            self.counter = 1 
        
        self.ax1.text(0.5,0.9,'Pixel Intensities',fontsize=10,transform=self.ax1.transAxes)
        self.ax1.plot(timeaxis,ixy,linewidth=0.9) 
        plt.xlabel('time [s]')        
        
        # calculate temporal autocorrelation of ixy -> autocorr
        deltat = 1.0 / self.fps   
        
        acorr = numpy.zeros(2*nimgs) 

        ixy = numpy.subtract(ixy,numpy.mean(ixy))

        # zero-padding 'vec' 
        zs = numpy.zeros(len(ixy),dtype=float) 
        vec = numpy.concatenate((ixy,zs))  
                        
        fft = numpy.fft.fft(vec)
        prod = numpy.multiply(fft,numpy.conjugate(fft)) / float(len(vec)) 
        ifft = numpy.real(numpy.fft.ifft(prod))
    
        meansq = (numpy.mean(vec))**2  
        stdv = numpy.std(vec)
        
        acorr = numpy.add(acorr,ifft/(stdv**2))  
        
        acorr = acorr[0:len(acorr)/2]
        
        
        self.ax = self.fig.add_subplot(212) 
        self.ax.text(0.5,0.9,'Temporal Autocorrelation',fontsize=10,transform=self.ax.transAxes)
        self.ax.plot(timeaxis,acorr,linewidth=0.9) 
        plt.xlabel('time [s]')
        
        # calc and plot power spectral density 
        
        
        
        
        
        
        self.fig.tight_layout()
        canvas = FigureCanvasTkAgg(self.fig, self.plotframe)
        canvas.draw()
        canvas.get_tk_widget().pack()
        canvas._tkcanvas.pack()
        
        
       
        
        
        
        
        
        
        
    
    
    
