import numpy
from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from math_utils import autocorrelation_zeropadding
import math
import os
import re
from skimage import filters
from scipy import ndimage
from scipy.ndimage import gaussian_filter
import cv2
from PIL import Image
from math_utils.bytescl import bytescl

class activitymap:

    def __init__(self, parent, parentw, parenth, pixsize, active_percentage,
                 active_area, fcparentframe):

        self.map = None
        self.parentw = parentw
        self.parenth = parenth
        self.tkframe = Frame(parent, width=self.parentw, height=self.parenth)
        self.tkframe.place(in_=parent, anchor='center', relx=0.5, rely=0.5)
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
        self.freq_clength = None
        self.pixsize = pixsize
        self.active_percentage = active_percentage
        self.active_area = active_area

    def calc_activitymap(self, parent, PILseq, FPS, minf, maxf, powerspectrum,
                         pixsize, automated=0):
        """
        Calculation of the activity map (spatially resolved CBF map)
        """

        # threshold for the condition to mark pixel as valid or invalid
        # based on the integral in the pixelspectra
        threshold = 0.15

        self.pixsize = pixsize
        self.fps = FPS

        # initialize attributes
        pwspecplot = powerspectrum.pwspecplot

        self.firstimg = PILseq[0]
        self.width, self.height = self.firstimg.size # dimension of images 
        self.nimgs = len(PILseq) # number of images   

        # -------------- determine dense optical flow -------------------------
        u_flow = []
        v_flow = []

        nimgs = self.nimgs

        # ws: window size in Farneback's optical flow 
        ws = round(1750.0/pixsize) # we set the window size to about 2 microns
        if (ws < 5): ws = 5

        # subtract the mean (Note: it is necessary to subtract the mean
        # before the optical flow calculation!)

        array = numpy.zeros((int(self.nimgs), int(self.height), int(self.width)), dtype=numpy.float32)
        # convert stack of PIL images to numpy array
        for i in range(nimgs):
            array[i, :, :] = numpy.array(PILseq[i])

        # determine average image (static background)
        mean_image = numpy.mean(array, axis=0)

        # subtract average image
        for i in range(nimgs):
            array[i, :, :] = numpy.subtract(array[i,:,:], mean_image)

        array = numpy.subtract(array, numpy.amin(array))
        array = numpy.uint8(bytescl(array))

        for i in range(nimgs):
            img = Image.fromarray(array[i, :, :])
            PILseq[i] = img

        del array

        for t in range( int(nimgs)-1 ):

            img1 = gaussian_filter(PILseq[t], sigma=(1, 1), truncate=1.0)
            img2 = gaussian_filter(PILseq[t+1], sigma=(1, 1), truncate=1.0)

            # get optical flow between image1 and image2
            flow = cv2.calcOpticalFlowFarneback(
                    img1, img2, None, 0.99, 1, ws, 7, 7, 1.5, 0)
            flow = flow.astype(numpy.float32)

            v_flow.append(flow[...,1])
            u_flow.append(flow[...,0])

        # Outlier removal in optical flow by median filtering (kernel size = 3):
        u_flow = ndimage.median_filter(u_flow, size=3)
        v_flow = ndimage.median_filter(v_flow, size=3)

        # smooth optical flow by (primarily spatial) Gaussian filtering
        ws = 1500.0 / pixsize
        wt = FPS / 150.0
        u_flow = gaussian_filter(u_flow, sigma=(wt,ws,ws), truncate=1.0)
        v_flow = gaussian_filter(v_flow, sigma=(wt,ws,ws), truncate=1.0)

        # Speedmat contains the optical flow speed [nt,ni,nj]
        speedmat = numpy.zeros_like(u_flow) # initialize speed matrix
        for t in range(nimgs-1):
            speedmat[t,:,:] = numpy.sqrt(u_flow[t][:,:]**2 + v_flow[t][:,:]**2)

        # Delete u_flow and v_flow
        del u_flow
        del v_flow
        del flow

        (nt,ni,nj) = numpy.shape(speedmat)

        # initialze the array, which will contain the activity map
        self.freqmap = numpy.zeros((int(self.height), int(self.width)))

        # initialize the boolean mask indicating the validity of each pixel 
        self.validity_mask = numpy.ones((int(self.height), int(self.width)))

        # ------------ Temporal variance condition intensity -------------------
        array = numpy.zeros((nimgs, self.height, self.width), dtype=numpy.float32)
        for t in range(nimgs):
            array[t,:,:] = numpy.array(PILseq[t])

        # Average temporal variance (averaged over all pixels)
        variance_threshold = filters.threshold_otsu(numpy.sqrt(numpy.var(array, axis=0)))
        variance_threshold /= 2.0 # conservative Otsu-threshold

        for i in range(ni):
            for j in range(nj):
                var_ij = numpy.sqrt(numpy.var(array[:,i,j]))
                if (var_ij < variance_threshold):
                    self.validity_mask[i,j] = 0
        del array

        # print('valid percentage after temporal variance: ',
        #      numpy.sum(self.validity_mask)/self.validity_mask.size)

        # ----------------------------------------------------------------------

        # ----------- Temporal variance condition optical flow  ----------------
        # Average temporal variance (averaged over all pixels)
        variance_threshold = filters.threshold_otsu(numpy.sqrt(numpy.var(speedmat,axis=0)))
        variance_threshold /= 2.0 #25.0
        for i in range(ni):
            for j in range(nj):
                var_ij = numpy.sqrt(numpy.var(speedmat[:,i,j]))
                if (var_ij < variance_threshold):
                    self.validity_mask[i,j] = 0

        # print('valid percentage after optical flow: ',
        #      numpy.sum(self.validity_mask) / self.validity_mask.size)
        # ----------------------------------------------------------------------

        # Delete the priorly drawn activity map
        self.tkframe.destroy()
        self.tkframe = Frame(parent, width=self.parentw, height=self.parenth)
        self.tkframe.place(in_=parent, anchor='c', relx=0.5, rely=0.5)

        # Fast-fourier-transform along time axis (pixel-wise)
        # (nt,ni,nj) = numpy.shape(self.array)
        (nt, ni, nj) = numpy.shape(powerspectrum.pixelspectra)
        self.spec = numpy.zeros(nt)

        # Calculate the frequencies:
        self.freqs = numpy.zeros(self.spec.size)
        for i in range(self.spec.size):
            self.freqs[i] = (i+2) * float(FPS) / float(self.nimgs)

        bot = int(round( (float(self.nimgs)*minf/float(FPS))-2 ))
        top = int(round( (float(self.nimgs)*maxf/float(FPS))-2 ))

        # integral of the 'mean' powerspectrum over choosen frequency band
        # (including the 2nd harmonics)
        bot2nd = bot # lower frequency limit for 1st and 2nd harmonics
        top2nd = round((0.5*bot) + (1.5 * top)) # upper freq limit for 1st and 2nd harms
        A_bar = numpy.sum(pwspecplot.yax[bot2nd:top2nd+1])

        dirname = 'test_pixelautocorr'
        if (os.path.exists(dirname)):
            pass
        else:
            os.mkdir(dirname)

        for i in range(ni):
            for j in range(nj):

                # Note here that 'pixelspectra' are not cropped, meaning that
                # they contain the zero-frequency contribution and the lowest
                # frequency contribution
                self.spec = powerspectrum.pixelspectra[:,i,j]
                self.spec = self.spec[2:round(nt/2)-2] # here we cut them away
                self.spec = self.spec / numpy.sum(self.spec)

                # Check the validity of each pixel: 
                # according to the procedure of the 'integral spectral density' 
                # presented in Ryser et al. 2007, However, note that here we
                # use a larger frequency bandwidth (including the 2nd harmonics)
                # (condition for invalidity: A_xy / A_bar < 0.15)

                A_xy = numpy.sum(self.spec[bot2nd:top2nd+1])

                if (A_xy > threshold * A_bar):
                    # valid pixel
                    # calculate the mean freq in CBF-freq band (weighted mean)
                    self.freqmap[i,j] = numpy.sum(numpy.multiply(self.freqs[bot:top+1],
                        self.spec[bot:top+1])) / numpy.sum(self.spec[bot:top+1])
                else:
                    # Mark pixel as invalid by setting validity mask to zero
                    self.validity_mask[i,j] = 0
                    #print('condition 1 not satisfied')

                # --------------------------------------------------------------
                # 2ND CONDITION TO MARK A PIXEL AS VALID/INVALID
                # For a valid pixel, we FURTHERMORE demand that the peak 
                # frequency originates from the fundamental CBF peak or its
                # second harmonic

                # Get location of peak frequency for each pixel
                maxind=numpy.argmax(self.spec)

                if (maxind.size > 1):
                    maxind = maxind[0]
                if not (maxind <= top2nd+1):
                    # The condition above checks whether the peak frequency
                    # (maxind) lies within the fundamental CBF bandwidth
                    # or the bandwidth of the second harmonics
                    self.validity_mask[i,j] = 0
                    #print('condition 2 not satisfied')
                # --------------------------------------------------------------

                # variance of optical flow

                # --------------------------------------------------------------
                """
                # 3RD CONDITION considering the optical flow speed
                if (self.validity_mask[i,j]):
                    # For a pixel to be valid, it is required that its spectral
                    # power within the CBF bandwidth is at least twice as high
                    # as it would be for white noise

                    # Calculate powerspectrum of pixel i,j based on OptFl speed
                    speed = numpy.squeeze(speedmat[:,i,j])
                    speed = (speed-numpy.mean(speed)) / numpy.sum(speed)
                    pix_fft = numpy.fft.fft(speed)
                    of_spec = numpy.absolute(numpy.square(pix_fft))
                    # of_spec now contains the powerspectrum of the optical flow
                    # speed for pixel i,j

                    # Get rid of the first two frequencies
                    of_spec = of_spec[2:round(len(of_spec)/2)-2]
                    # Normalize the spectrum
                    of_spec = of_spec / numpy.sum(of_spec)

                    # Now we demand that the integral power over the CBF bandw.
                    # is twice as high as in white noise
                    cbf_power = numpy.sum(of_spec[bot:top2nd+1])
                    power_total = numpy.sum(of_spec)

                    ratio1 = cbf_power / power_total
                    ratio2 =  (1.5*maxf-0.5*minf)/(0.5*FPS)
                    cond3 = (ratio1 > 2 * ratio2)

                    if (not cond3):
                        # If 3rd condition is not satisfied
                        self.validity_mask[i,j] = 0
                        #print('condition 3 not satisfied')
                        #print('ratio1: ',ratio1)
                        #print('ratio2: ',ratio2)

                    #plt.figure(figsize=(4, 3))  # Set figure size
                    #plt.plot(self.freqs[0:len(of_spec)], of_spec)
                    #plt.xlim([0, 30])
                    #fname = 'spec' + str(i) + str(j) + '.png'
                    #path = os.path.join(dirname, fname)
                    #plt.savefig(path, dpi=100)  # Save a
                    #plt.close()
                    """
        # --------------------------------------------------------------------

        # smooth validity mask using a 2D-average 
        # self.validity_mask = numpy.round(gaussian_filter(self.validity_mask, 1.0, truncate=1.0))
        self.freqmap = gaussian_filter(self.freqmap,1.0, truncate=1.0)
        # slightly smooth the validity mask
        self.validity_mask = ndimage.median_filter(self.validity_mask, size=round(5000.0/pixsize))

        #  ----------------- check histogram for of_speed / cbf --------------
        #hist=numpy.zeros(1000)
        #for i in range(ni):
        #    for j in range(nj):
        #        if (self.validity_mask[i,j]):
        #            hist=hist+ numpy.histogram(speedmat[:,i,j]/self.freqmap[i,j],bins=1000,range=(0,0.5))[0]
        #
        #plt.plot(hist)
        #plt.show()
        # --------------------------------------------------------------------

        #print('---------- max of validity maks !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #print(numpy.max(self.validity_mask))

        # set frequency of invalid pixels to nan:
        for i in range(ni):
            for j in range(nj):
                if (not self.validity_mask[i,j]):
                    self.freqmap[i,j] = numpy.nan

        # plot the activity map (self.freqmap)
        dpis = 120

        figw = round(self.parentw / dpis)
        figh = round(self.parenth / dpis)


        self.fig, self.ax1 = plt.subplots(nrows=1, figsize=(figw-1, figh-1), dpi=dpis)

        # plot first image & overlay activity map  

        self.canvas = FigureCanvasTkAgg(self.fig, self.tkframe)

        # plot the activity map 

        # get max and min frequency in activity map 
        minf = numpy.nanmin(self.freqmap)
        maxf = numpy.nanmax(self.freqmap)
        minf = math.floor(minf)-0.001
        maxf = math.ceil(maxf)+0.001

        # customize xticks and yticks
        # print('self.pixsize: ',self.pixsize)
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
        # print('shape of activitymap: ', self.freqmap.shape)
        # numpy.savetxt('activitymap.dat', self.freqmap)

        #divider = make_axes_locatable(self.ax2)
        #cax = divider.append_axes("right", size="7%", pad=0.08)
        arr = self.freqmap.flatten()
        #print ('shape of self.freqmap: ', self.freqmap.shape)
        #bla2 = self.ax2.hist(arr,bins=50)

        #print('--------------------------------------------------------------')
        #print('spatial mean CBF: ', numpy.nanmean(arr))
        #print('numpy variance: ', numpy.std(arr))
        #bla = numpy.sqrt(numpy.sum(numpy.subtract(arr, numpy.mean(arr))**2) / float(len(arr)))
        #print('spatial variance in CBF (standard deviation): ',numpy.nanstd(arr))
        #print('--------------------------------------------------------------')
        #bla2=self.ax2.imshow(numpy.asarray(self.firstimg),cmap='gray',alpha=1.0)
        #self.ax2.set_title('spatial CBF distribution')
        #self.fig.colorbar(bla2,cax=cax)
        #self.ax2.set_xlabel('CBF [Hz]')
        #self.ax2.set_ylabel('Ocurrence')

        ssd = numpy.nanstd(arr)

        # Display the size of the 'active area'
        activearea = numpy.sum(self.validity_mask) * (self.pixsize / 1000.0)**2
        activearea = activearea / 1000.0 / 1000.0 # convert to square millim.

        bla = '%.6f' %activearea
        self.active_area.set(bla)

        # active percentage (nr of active pixels : nr of pixels in activitymap)
        percentage = numpy.sum(self.validity_mask) / self.freqmap.size * 100
        bla = '%.2f' %percentage
        self.active_percentage.set(bla)

        # plots should not overlap
        self.fig.tight_layout()

        self.canvas.draw()
        self.canvas.get_tk_widget().place(anchor='c', relx=0.5, rely=0.5)
        self.canvas._tkcanvas.place(anchor='c', relx=0.5, rely=0.5)


    def frequency_correlogram(self, parent, pixsize):
        """
        Computes the spatial autocorrelation of the activity map
        """

        # we mainly need the validity_mask and the acitivity map 'freqmap'
        # 2D autocorrelation with zero-padding!

        if (self.freqmap is not None):
             self.freq_acorr = autocorrelation_zeropadding.acorr2D_zp(self.freqmap,
                centering=True, normalize=True, mask=self.validity_mask)

        # Slightly smooth autocorrelogram: 
        self.freq_acorr = gaussian_filter(self.freq_acorr, 1.0, truncate=1.0)

        # For extent keyword (to indicate the range of the x and y axis) 
        xmax = 0.5 * self.width * self.pixsize / 1000.0
        ymax = 0.5 * self.height * self.pixsize / 1000.0

        xmin = -xmax
        ymin = -ymax

        dpi = 120

        figw = round(self.parentw / dpi)
        figh = round(self.parenth / dpi)

        self.fcfig, self.ax = plt.subplots(nrows=1, figsize=(figw-1, figh-1), dpi=dpi)

        # plot first image & overlay activity map  

        self.canvas = FigureCanvasTkAgg(self.fcfig, parent)

        #print(' ------------------------------------------------------------ ')
        #print('check normalization of frequency corr')
        #print(numpy.max(self.freq_acorr))
        #print(' ------------------------------------------------------------ ')

        divider = make_axes_locatable(self.ax)
        cax = divider.append_axes("right", size="7%", pad=0.08)
        bla=self.ax.imshow(self.freq_acorr, alpha=1.0, cmap='coolwarm', interpolation='none',extent=[xmin,xmax,ymin,ymax])
        #self.ax.set_title('Frequency autocorrelation')

        self.ax.set_xlabel("$\Delta$x [$\mu$m]",labelpad=0)
        self.ax.set_ylabel("$\Delta$y [$\mu$m]",labelpad=-4)

        self.fcfig.colorbar(bla,cax=cax,label="C($\Delta$x,$\Delta$y)")

        # write freq correlogram to file:
        # numpy.savetxt('frequencycorrelogram.dat', self.freq_acorr)

        # Determine the frequency correlation length 
        # as the square root of all pixels > 1/e
        threshold = math.exp(-1)
        area = numpy.sum(self.freq_acorr >= threshold)
        xi = math.sqrt(area) * self.pixsize / 1000.0

        # print('**************************************************************')
        # print('Frequency correlation length:  ',xi)
        # print('**************************************************************')

        self.freq_clength = xi

        str1 = r'$\xi_f$'
        str2 = " = $%.2f$" %xi
        str3 = " $\mu$m"
        xpos = 15
        ypos = 15
        self.ax.text(xpos,ypos,str1+str2+str3,fontsize=10)

        self.fcfig.tight_layout(pad=1.5)

        self.canvas.draw()
        self.canvas.get_tk_widget().place(anchor='c', relx=0.5, rely=0.5)
        self.canvas._tkcanvas.place(anchor='c', relx=0.5, rely=0.5)


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


    def save_plot(self, dirname):
        f = open('config/output_directory.dat', 'r')
        output_directory = f.read()
        f.close()
        # special characters are replaced by an underline:
        fname = re.sub(r'[^A-Za-z0-9 ]', "_", dirname)
        fname = os.path.join(output_directory, fname + '_ACTIVITYMAP.png')
        self.fig.savefig(fname,format='png',dpi=200)