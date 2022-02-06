import numpy
from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import autocorrelation_zeropadding


class activitymap:

    def __init__(self, parent, parentw, parenth):

        self.map = None
        self.parentw = parentw
        self.parenth = parenth
        self.tkframe = Frame(parent, width=self.parentw, height=self.parenth)
        self.tkframe.place(in_=parent, anchor='c', relx=0.5, rely=0.5)

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
        self.fps = None

        self.meantacorr = None # mean temporal autocorrelation

        self.validity_mask = None # mask containing the valid pixels

        self.freq_acorr = None # autocorrelation of the activity map 


    def calc_activitymap(self, parent, PILseq, FPS, minf, maxf, powerspectrum):
        """
        calculation of the activity map (spatially resolved CBF map)
        """

        self.fps = FPS

        # initialize attributes
        pwspecplot = powerspectrum.pwspecplot

        self.firstimg = PILseq[0]
        self.width, self.height = self.firstimg.size # dimension of images 
        self.nimgs = len(PILseq) # number of images   

        #self.array = numpy.zeros((int(self.nimgs),int(self.height),int(self.width)))
        #for i in range(self.nimgs): 
        #    self.array[i,:,:] = numpy.array(PILseq[i]) # array holds image intensties 

        # initialze the array holding the activity map
        self.freqmap = numpy.zeros((int(self.height), int(self.width)))

        # initialize the boolean mask indicating the validity of each pixel 
        self.validity_mask = numpy.zeros((int(self.height), int(self.width)))

        # delete the priorly drawn activity map
        self.tkframe.destroy()
        self.tkframe = Frame(parent, width=self.parentw, height=self.parenth)
        self.tkframe.place(in_=parent, anchor='c', relx=0.5, rely=0.5)


        # fast-fourier-transform along time axis (pixel-wise) 
        # (nt,ni,nj) = numpy.shape(self.array)
        (nt, ni, nj) = numpy.shape(powerspectrum.pixelspectra)
        self.spec = numpy.zeros(nt)

        # calculate the frequencies: 
        self.freqs = numpy.zeros(self.spec.size)
        for i in range(self.spec.size):
            self.freqs[i] = (i+1) * float(FPS) / float(self.nimgs)

        bot = int(round( (float(self.nimgs)*minf/float(FPS))-1 ))
        top = int(round( (float(self.nimgs)*maxf/float(FPS))-1 ))

        # integral of the 'mean' powerspectrum over choosen frequency band 
        A_bar = numpy.sum(pwspecplot.yax[bot:top+1])

        for i in range(ni):
            for j in range(nj):

                self.spec = powerspectrum.pixelspectra[:,i,j]
                self.spec = self.spec[1:round(nt/2)-1] 
                self.spec = self.spec / numpy.sum(self.spec) 

                # check the validity of each pixel: 
                # according to the procedure of the 'integral spectral density' 
                # presented in Ryser et al. 2007
                # (condition for invalidity: A_xy / A_bar < 0.15)  

                # threshold in Ryser was set to 0.15 
                threshold = 0.25

                A_xy = numpy.sum(self.spec[bot:top+1])

                if (A_xy > threshold * A_bar):
                    # valid pixel
                    # calculate the mean freq in freq band (weighted mean)
                    self.freqmap[i,j] = numpy.sum(numpy.multiply(self.freqs[bot:top+1],
                        self.spec[bot:top+1])) / numpy.sum(self.spec[bot:top+1])

                    # validity-mask:
                    self.validity_mask[i,j] = 1
                else:
                    # invalid pixel 
                    self.freqmap[i,j] = numpy.nan

        # plot the activity map (self.freqmap)
        dpis = 150

        figw = round(self.parentw / dpis)
        figh = round(self.parenth / dpis)

        self.fig, (self.ax1, self.ax2) = plt.subplots(nrows=2, figsize=(figw, figh), dpi=dpis)

        # plot first image & overlay activity map  

        self.canvas = FigureCanvasTkAgg(self.fig, self.tkframe)

        #cmap = matplotlib.cm.jet
        #cmap.set_bad('white',1.)

        # plot the activity map 

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.

        divider = make_axes_locatable(self.ax1)
        cax = divider.append_axes("right", size="7%", pad=0.08)
        bla1=self.ax1.imshow(self.freqmap, alpha=1.0, cmap='coolwarm', interpolation='none')
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
        self.canvas.get_tk_widget().place(anchor='c', relx=0.5, rely=0.5)
        self.canvas._tkcanvas.place(anchor='c', relx=0.5, rely=0.5)


    def frequency_correlogram(self, parent, pixsize):
        """
        Computes the autocorrelation of the activity map
        """
        print('frequency correlation gets computed...')

        # we mainly need the validity_mask and the acitivity map freqmap
        # 2D autocorrelation with zero-padding!

        #activitymap = numpy.array(self.freqmap)
        #mask = numpy.array(self.validity_mask)

        if (self.freqmap is not None):
            self.freq_acorr = autocorrelation_zeropadding.acorr2D_zp(self.freqmap,
                self.validity_mask)


        #print(self.freq_acorr)

        #fig = plt.figure()
        #plt.imshow(self.freq_acorr, alpha=1.0, cmap='gray', interpolation='none')
        #plt.show()

        dpi = 150

        figw = round(self.parentw / dpi)
        figh = round(self.parenth / dpi)

        self.fig, self.ax = plt.subplots(nrows=1, figsize=(figw, figh), dpi=dpi)

        # plot first image & overlay activity map  

        self.canvas = FigureCanvasTkAgg(self.fig, parent)

        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="7%", pad=0.08)
        bla=self.ax.imshow(self.freq_acorr, alpha=1.0, cmap='coolwarm', interpolation='none')
        self.ax.set_title('Frequency autocorrelation')
        self.fig.colorbar(bla,cax=cax)

        self.fig.tight_layout()

        self.canvas.draw()
        self.canvas.get_tk_widget().place(anchor='c', relx=0.5, rely=0.5)
        self.canvas._tkcanvas.place(anchor='c', relx=0.5, rely=0.5)




