import numpy
from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

import autocorrelation_zeropadding
import math

import denoising

from skimage import filters
from scipy import ndimage
from scipy.ndimage import gaussian_filter


class activitymap:

    def __init__(self, parent, parentw, parenth, pixsize, active_percentage, active_area, fcparentframe):

        self.map = None
        self.parentw = parentw
        self.parenth = parenth
        self.tkframe = Frame(parent, width=self.parentw, height=self.parenth)
        self.tkframe.place(in_=parent, anchor='c', relx=0.5, rely=0.5)
        self.parent=parent

        self.fcparentframe = fcparentframe
        self.fc_tkframe = None

        self.firstimg = None
        self.width = None
        self.height = None
        self.nimgs = None

        self.array = None

        self.spec = None
        self.freqs = None

        self.freqmap = None

        self.fcfig = None # figure belonging to frequency corr plot

        self.fig = None
        self.ax1 = None
        self.ax2 = None

        self.canvas = None
        self.fps = None

        self.meantacorr = None # mean temporal autocorrelation

        self.validity_mask = None # mask containing the valid pixels

        self.freq_acorr = None # autocorrelation of the activity map 

        self.pixsize = pixsize

        self.active_percentage = active_percentage
        self.active_area = active_area

    def calc_activitymap(self, parent, PILseq, FPS, minf, maxf, powerspectrum, pixsize, threshold):
        """
        calculation of the activity map (spatially resolved CBF map)
        """
        self.pixsize = pixsize
        self.fps = FPS

        # initialize attributes
        pwspecplot = powerspectrum.pwspecplot

        self.firstimg = PILseq[0]
        self.width, self.height = self.firstimg.size # dimension of images 
        self.nimgs = len(PILseq) # number of images   

        
        # --------------- subtract mean image from PILseq ---------------------
        # convert stack of PIL images to numpy array
        array=[]
        for i in range(self.nimgs):
            array.append(numpy.array(PILseq[i]))
        array = numpy.array(array)

        ## calculate the mean image
        #for i in range(nimgs):
        #    sumimg = numpy.add(sumimg,array[i,:,:])
        #meanimg = numpy.multiply(1.0/float(nimgs), sumimg)
        #
        # subtract the mean image 
        #for i in range(nimgs):
        #    array[i,:,:] = numpy.subtract(array[i,:,:], meanimg)
        # ------------------------------------------------------------------- #

        # initialize the variance map
        # which holds the variance along the time t for each pixel
        varmap = numpy.zeros((int(self.height), int(self.width)))

        for i in range(int(self.height)):
            for j in range(int(self.width)):
                varmap[i,j] = numpy.var(array[:,i,j])

        # get variance threshold via otsu-method 
        hist = []
        p = numpy.percentile(varmap, 50)
        for i in range(int(self.height)):
            for j in range(int(self.width)):
                v = varmap[i,j]
                if (v < p):
                    hist.append(v)
        hist = numpy.array(hist)
        otsu_threshold = filters.threshold_otsu(hist)
        #plt.hist(hist,1000)
        #plt.show()



        # initialze the array, which will contain the activity map
        self.freqmap = numpy.zeros((int(self.height), int(self.width)))

        # initialize the boolean mask indicating the validity of each pixel 
        self.validity_mask = numpy.ones((int(self.height), int(self.width)))

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


        hist = []

        for i in range(ni):
            for j in range(nj):

                self.spec = powerspectrum.pixelspectra[:,i,j]
                self.spec = self.spec[1:round(nt/2)-1]
                self.spec = self.spec / numpy.sum(self.spec)

                # check the validity of each pixel: 
                # according to the procedure of the 'integral spectral density' 
                # presented in Ryser et al. 2007
                # (condition for invalidity: A_xy / A_bar < 0.15)  

                A_xy = numpy.sum(self.spec[bot:top+1])

                hist.append(A_xy)


                if (A_xy > threshold * A_bar):
                    # valid pixel
                    # calculate the mean freq in freq band (weighted mean)
                    self.freqmap[i,j] = numpy.sum(numpy.multiply(self.freqs[bot:top+1],
                        self.spec[bot:top+1])) / numpy.sum(self.spec[bot:top+1])
                else:
                    # mark pixel as invalid
                    #self.freqmap[i,j] = numpy.nan
                    self.validity_mask[i,j] = 0

                # 2ND CONDITION TO MARK A PIXEL AS VALID/INVALID
                # For a valid pixel, we FURTHERMORE demand that the peak 
                # frequency lies within the CBF-band

                # get location of peak frequency for each pixel
                maxind=numpy.argmax(self.spec)

                if (maxind.size > 1):
                    maxind=maxind[0]

                if ((maxind >= bot) and (maxind <= top)):
                    # pixel fullfills the criterium - nothing to do
                    pass
                else:
                    #self.freqmap[i,j] = numpy.nan
                    self.validity_mask[i,j] = 0


                # 3RD CONDITION otsu thresholding of variance
                #if (varmap[i,j] < otsu_threshold):
                #    self.validity_mask[i,j] = 0
                #    self.freqmap[i,j] = numpy.nan


        #hist = numpy.array(hist)
        #otsu_threshold = filters.threshold_otsu(hist)
        #plt.hist(hist,1000)
        #plt.vlines(otsu_threshold, 0, 1000)
        #plt.show()


        # smooth validity mask using a 2D-average 
        # window size = 5000 x 5000 nm (size of a cell)
        #sig = round(1000.0 / pixsize)
        self.validity_mask = numpy.round(gaussian_filter(self.validity_mask, 0.75))
        self.freqmap = numpy.round(gaussian_filter(self.freqmap, 0.75))


        print('---------- max of validity maks !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(numpy.max(self.validity_mask))


        # set frequency of invalid pixels to nan:
        for i in range(ni):
            for j in range(nj):
                if (not self.validity_mask[i,j]):
                    self.freqmap[i,j] = numpy.nan


        # plot the activity map (self.freqmap)
        dpis = 120

        figw = round(self.parentw / dpis)
        figh = round(self.parenth / dpis)

        #self.fig, (self.ax1, self.ax2) = plt.subplots(ncols=2, figsize=(figw-0.5, figh-0.5), dpi=dpis)
        self.fig, self.ax1 = plt.subplots(nrows=1, figsize=(figw-1, figh-1), dpi=dpis)

        # plot first image & overlay activity map  

        self.canvas = FigureCanvasTkAgg(self.fig, self.tkframe)

        #cmap = matplotlib.cm.jet
        #cmap.set_bad('white',1.)

        # plot the activity map 

        # get max and min frequency in activity map 
        minf = numpy.nanmin(self.freqmap)
        maxf = numpy.nanmax(self.freqmap)
        minf = math.floor(minf)-0.001
        maxf = math.ceil(maxf)+0.001

        # customize xticks and yticks
        print('self.pixsize: ',self.pixsize)
        xmax = round(self.width * self.pixsize / 1000.0)
        ymax = round(self.height * self.pixsize / 1000.0)

        # create an axes on the right side of ax. The width of cax will be 5%
        # of ax and the padding between cax and ax will be fixed at 0.05 inch.

        divider = make_axes_locatable(self.ax1)
        cax = divider.append_axes("right", size="7%", pad=0.08)
        bla1=self.ax1.imshow(self.freqmap, alpha=1.0, cmap='coolwarm', interpolation='none',vmin=minf,vmax=maxf, extent=[0,xmax,0,ymax])
        self.ax1.set_title('Activity Map')
        self.ax1.set_xlabel("x [$\mu$m]",labelpad=2)
        self.ax1.set_ylabel("y [$\mu$m]",labelpad=2)

        self.fig.colorbar(bla1,cax=cax,label='Frequency [Hz]')

        # write activity map to file:
        print('shape of activitymap: ', self.freqmap.shape)
        numpy.savetxt('activitymap.dat', self.freqmap)


        #divider = make_axes_locatable(self.ax2)
        #cax = divider.append_axes("right", size="7%", pad=0.08)
        arr = self.freqmap.flatten()
        #print ('shape of self.freqmap: ', self.freqmap.shape)
        #bla2 = self.ax2.hist(arr,bins=50)

        print('--------------------------------------------------------------')
        print('spatial mean CBF: ', numpy.nanmean(arr))
        #print('numpy variance: ', numpy.std(arr))
        #bla = numpy.sqrt(numpy.sum(numpy.subtract(arr, numpy.mean(arr))**2) / float(len(arr)))
        print('spatial variance in CBF (standard deviation): ',numpy.nanstd(arr))
        print('--------------------------------------------------------------')
        #bla2=self.ax2.imshow(numpy.asarray(self.firstimg),cmap='gray',alpha=1.0)
        #self.ax2.set_title('spatial CBF distribution')
        #self.fig.colorbar(bla2,cax=cax)
        #self.ax2.set_xlabel('CBF [Hz]')
        #self.ax2.set_ylabel('Ocurrence')

        ssd = numpy.nanstd(arr)

        """
        str1 = "CBF_SSD = "
        str2 = "$%.2f$" %ssd
        str3 = " Hz"
        xpos = 0.8
        ypos = 0.8
        self.ax1.text(xpos,ypos,str1+str2+str3,fontsize=10)
        """

        # Display the size of the 'active area'
        activearea = numpy.sum(self.validity_mask) * (self.pixsize / 1000.0)**2
        activearea = activearea / 1000.0 / 1000.0 # convert to square millim.

        bla = '%.6f' %activearea
        self.active_area.set(bla)

        # active percentage (nr of active pixels : nr of pixels in activitymap)
        percentage = numpy.sum(self.validity_mask) / self.freqmap.size * 100
        bla = '%.2f' %percentage
        self.active_percentage.set(bla)

        """
        str1 = "Active area = "
        str2 = "$%.2f$" %activearea
        str3 = " mm$^2$"
        xpos = 0
        ypos = 0.8 * ymax
        self.ax1.text(xpos,ypos,str1+str2+str3,fontsize=10)
        """

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

        # for extent keyword (to indicate the range of the x and y axis) 
        xmax = 0.5 * self.width * self.pixsize / 1000.0
        ymax = 0.5 * self.height * self.pixsize / 1000.0

        xmin = -xmax
        ymin = -ymax

        #print(self.freq_acorr)

        #fig = plt.figure()
        #plt.imshow(self.freq_acorr, alpha=1.0, cmap='gray', interpolation='none')
        #plt.show()

        dpi = 120

        figw = round(self.parentw / dpi)
        figh = round(self.parenth / dpi)

        self.fcfig, self.ax = plt.subplots(nrows=1, figsize=(figw-1, figh-1), dpi=dpi)

        # plot first image & overlay activity map  

        self.canvas = FigureCanvasTkAgg(self.fcfig, parent)

        print(' ------------------------------------------------------------ ')
        print('check normalization of frequency corr')
        print(numpy.max(self.freq_acorr))
        print(' ------------------------------------------------------------ ')

        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="7%", pad=0.08)
        bla=self.ax.imshow(self.freq_acorr, alpha=1.0, cmap='coolwarm', interpolation='none',extent=[xmin,xmax,ymin,ymax])
        #self.ax.set_title('Frequency autocorrelation')

        self.ax.set_xlabel("$\Delta$x [$\mu$m]",labelpad=0)
        self.ax.set_ylabel("$\Delta$y [$\mu$m]",labelpad=-4)

        self.fcfig.colorbar(bla,cax=cax,label="C($\Delta$x,$\Delta$y)")


        # write freq correlogram to file:
        numpy.savetxt('frequencycorrelogram.dat', self.freq_acorr)


        # Determine the frequency correlation length 
        # as the square root of all pixels > 1/e
        threshold = math.exp(-1)
        area = numpy.sum(self.freq_acorr >= threshold)
        xi = math.sqrt(area) * self.pixsize / 1000.0

        print('**************************************************************')
        print('Frequency correlation length:  ',xi)
        print('**************************************************************')

        str1 = r'$\xi_f$'
        str2 = " = $%.2f$" %xi
        str3 = " $\mu$m"
        xpos = -3
        ypos = 3
        self.ax.text(xpos,ypos,str1+str2+str3,fontsize=10)

        self.fcfig.tight_layout(pad=1.5)

        self.canvas.draw()
        self.canvas.get_tk_widget().place(anchor='c', relx=0.5, rely=0.5)
        self.canvas._tkcanvas.place(anchor='c', relx=0.5, rely=0.5)

        # print('frequency correlation length: ',xi)

        #fig = plt.figure()
        #ax = plt.axes(projection='3d')
        #(ni,nj) = self.freq_acorr.shape

        #x = numpy.linspace(0, nj, num=nj)
        #y = numpy.linspace(0,ni,num=ni)
        #X, Y = numpy.meshgrid(x, y)
        #ax.plot_surface(X,Y,self.freq_acorr) 
        #plt.show()

    def delete_content(self):
        """
        Deletes the displayed content in the activitmap tab & the freqcorr tab
        """

        # Delete all displayed content in acitivity map tab:
        self.tkframe.destroy()
        self.tkframe = Frame(self.parent, width=self.parentw, height=self.parenth)
        self.tkframe.place(in_=self.parent, anchor='c', relx=0.5, rely=0.5)
        self.tkframe.update()
        self.active_area.set('')
        self.active_percentage.set('')

        # Delete all displayed content fcorr tab
        self.fc_tkframe.destroy()
        self.fc_tkframe = Frame(self.fcparentframe, width=self.parentw, height=self.parenth)
        self.fc_tkframe.place(in_=self.fcparentframe, anchor='c', relx=0.5, rely=0.5)
        self.fc_tkframe.update()






