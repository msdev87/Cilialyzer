import numpy 
import os
from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

class activitymap:

    def __init__(self,parent,parentw, parenth):

        self.map = None

        
        self.parentw = parentw 
        self.parenth = parenth
        self.tkframe = Frame(parent,width=self.parentw,height=self.parenth) 
        self.tkframe.pack()

        self.firstimg = None  
        self.width = None
        self.height = None  
        self.nimgs = None  

        self.array = None  

        self.spec = None 
        self.freqs = None 
        
        self.freqmap = None  

        self.fig = None 
        self.ax1 = None 
        self.ax2 = None 

        self.canvas = None 

    def calc_activitymap(self,parent,PILseq,FPS,minf,maxf,powerspectrum): 

        # initialize attributes 

        pwspecplot = powerspectrum.pwspecplot 
        

        self.firstimg = PILseq[0] 
        self.width, self.height = self.firstimg.size # dimension of images 
        self.nimgs = len(PILseq) # number of images   

        #self.array = numpy.zeros((int(self.nimgs),int(self.height),int(self.width)))

        #for i in range(self.nimgs): 
        #    self.array[i,:,:] = numpy.array(PILseq[i]) # array holds image intensties 
       
        self.freqmap = numpy.zeros((int(self.height),int(self.width))) # activity map 


        self.tkframe.destroy()
        self.tkframe = Frame(parent,width=self.parentw,height=self.parenth)
        self.tkframe.pack()


        # fast-fourier-transform along time axis (pixel-wise) 
        #(nt,ni,nj) = numpy.shape(self.array)
        (nt,ni,nj) = numpy.shape(powerspectrum.pixelspectra)
        self.spec = numpy.zeros(nt)


        # calculate the frequencies: 
        self.freqs = numpy.zeros(self.spec.size)
        for i in range(self.spec.size):
            self.freqs[i] = (i+1) * float(FPS) / float(self.nimgs)


        bot =  int(round( (float(self.nimgs)*minf/float(FPS))-1 ))
        top =  int(round( (float(self.nimgs)*maxf/float(FPS))-1 ))
        
        #print "bot", bot 
        #print "top", top 

        # integral of the 'mean' powerspectrum over choosen frequency band 
        A_bar = numpy.sum(pwspecplot.yax[bot:top+1])
        
        
        for i in range(ni):
            for j in range(nj):

                #self.spec = numpy.square(numpy.absolute(numpy.fft.fft(self.array[:,i,j],axis=0)))
                self.spec = powerspectrum.pixelspectra[:,i,j]
                self.spec = self.spec[1:round(nt/2)-1] 
                self.spec = self.spec / numpy.sum(self.spec) 

                #peak = numpy.amax(self.spec)   
                #ind = numpy.where(self.spec == peak)

                # check the validity of each pixel: 
                # according to the procedure of the 'integral spectral density' 
                # presented in Ryser 2007 
                # (condition for invalidity: A_xy / A_bar < 0.15)  

                # threshold in Ryser was set to 0.15 
                threshold = 0.4
                
                A_xy = numpy.sum(self.spec[bot:top+1])

                if (A_xy > threshold * A_bar):
                    # valid pixel 
                    # calculate the mean freq in freq band (weighted mean)
                    
                    self.freqmap[i,j] = numpy.sum(numpy.multiply(self.freqs[bot:top+1], self.spec[bot:top+1])) / numpy.sum(self.spec[bot:top+1])
                    
                else:
                    # invalid pixel 
                    self.freqmap[i,j] = numpy.nan
     
            
        dpis = 150 

        #figw = int(round(self.tkframe.winfo_width() / dpis *0.8)) 
        #figh = int(round(self.tkframe.winfo_height() / dpis * 0.8)) 


        figw = round(1.5*self.parentw / dpis)   
        figh = round(self.parenth / dpis) 
    
        self.fig, (self.ax1, self.ax2) = plt.subplots(ncols=2, figsize=(figw,figh),dpi=dpis)
         
        # plot first image & overlay activity map  
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.tkframe)
        
        #cmap = matplotlib.cm.jet
        #cmap.set_bad('white',1.)

        # plot the activity map 
        
        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.

        divider = make_axes_locatable(self.ax1)
        cax = divider.append_axes("right", size="7%", pad=0.08)
        bla1=self.ax1.imshow(self.freqmap, alpha=1.0,cmap='coolwarm',interpolation='none') 
        self.ax1.set_title('Activity Map') 
        self.fig.colorbar(bla1,cax=cax)
        
        
        divider = make_axes_locatable(self.ax2)
        cax = divider.append_axes("right", size="7%", pad=0.08)
        bla2=self.ax2.imshow(numpy.asarray(self.firstimg),cmap='gray',alpha=1.0)
        self.ax2.set_title('Example Frame') 
        self.fig.colorbar(bla2,cax=cax)

        # plots should not overlap
        self.fig.tight_layout()

        self.canvas.draw()
        self.canvas.get_tk_widget().pack() 
        self.canvas._tkcanvas.pack()


