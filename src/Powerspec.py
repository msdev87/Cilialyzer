import numpy
import matplotlib.pyplot as plt
import time
import math
from scipy.ndimage import gaussian_filter

import TkPowerspecPlot
import os
if os.sys.version_info.major > 2:
    from tkinter import *
else:
    from tkinter import *

import tkinter.ttk
import scipy.optimize

def decay_func(x, a, b, c):
    # f(x) = a * (x+b)^(-c)
    return a * ((x+b)**(-c))

def gauss_func(x,a,b,c):
    # f(x) = a * exp( - (x-b)**2 / 2c**2)
    return a * numpy.exp(-(x-b)**2 / (2*c**2))

def fit_func(x, d1, d2, d3, g1a, g1b, g1c, g2a, g2b, g2c):
    return decay_func(x, d1, d2, d3) + gauss_func(x, g1a, g1b, g1c) + gauss_func(x, g2a, g2b, g2c)

class powerspec:

    def __init__(self,parent,parentw,parenth):

        self.spec = None
        self.freqs = None
        self.cbf_low = None # for peak selection (left limit)  
        self.cbf_high = None # right limit in peak selection 
        self.cbflowind = None
        self.cbfhighind = None
        self.pwspecplot = None
        self.parentw = parentw
        self.parenth = parenth
        self.tkframe = Frame(parent,width=self.parentw,height=self.parenth)
        self.parent = parent

        self.tkframe.place(in_=parent, width=self.parentw, height=self.parenth)
        self.tkframe.update()
        self.pwspecplot = TkPowerspecPlot.TkPowerspecPlot(self.tkframe)
        self.pixelspectra = None
        self.pixelffts = None

    def calc_powerspec(self, roiseq, FPS, parent, minscale, maxscale, automated=0):

        # check whether the input data is adequately set:
        if (len(roiseq)) < 10:
            messagebox.showerror(title = "Error", message = "Please select a directory")

        else:
            # if not automated:
            # rebuild the frame (deletes its content)
            self.tkframe.destroy()
            self.tkframe = Frame(parent,width=self.parentw,height=self.parenth)

            self.tkframe.place(in_=parent, anchor='c', relx=0.5, rely=0.5)
            self.tkframe.update()

            self.pwspecplot = TkPowerspecPlot.TkPowerspecPlot(self.tkframe)

            firstimg = roiseq[0] # first image of roi sequence  
            width, height = firstimg.size # dimension of images 
            nimgs = len(roiseq) # number of images   

            # initialize numpy float array, which will hold the image sequence  
            array = numpy.zeros((int(nimgs),int(height),int(width)))

            # ---- Noise-removal by Gaussian filtering (in space and time) ---- 
            # Gaussian filtering of the img seq in space and time 
            # (sigma=1,kernel size=1)
            for i in range(nimgs):
                array[i,:,:] = numpy.array(roiseq[i])
            array = gaussian_filter(array, 1.0, truncate=1.0)
            # --------------------------------------------------------------- #

            (nt,ni,nj) = numpy.shape(array)

            # -- create a toplevel window to display the progress indicator --
            # caution: the feedback to the frontend slows down the cbf calc.!
            # *************************************************************** #
            if not automated:
                progresswin = Toplevel()
                progresswin.minsize(width=500,height=30)
                progresswin.title("Powerspectrum in Progress, Please Wait...")
                # get the monitor dimensions:
                screenw = progresswin.winfo_screenwidth()
                screenh = progresswin.winfo_screenheight()
                # place the progress indicator in the center of the screen
                placement = "+%d+%d" % (screenw/2-300,screenh/2-15)
                progresswin.geometry(placement)
                progresswin.geometry('600x30')

                s = tkinter.ttk.Style()
                s.theme_use("default")
                s.configure("TProgressbar", thickness=30)

                pbvar = IntVar() # progress bar variable (counts number of loaded imgs)
                pb=tkinter.ttk.Progressbar(progresswin,mode="determinate",variable=pbvar,\
                    maximum=ni*nj,length=600,style="TProgressbar")
                s.configure("TProgressbar", thickness=30)
                pb.place(in_=progresswin)
                progresswin.update()
            progress = 0
            # **************************************************************** #
            # fast-fourier-transform along time axis (pixel-wise) 

            # powerspectrum.pixelspectra : 3D array, which holds the 
            # power spectra along the time-axis for each pixel
            self.pixelspectra = numpy.zeros((nt, ni, nj))

            # powerspectrum.pixelffts: 3D array holding the pixel-wise temp.fft
            self.pixelffts = numpy.zeros((nt, ni, nj), dtype=numpy.complex_)

            self.spec = numpy.zeros(nt)

            for i in range(ni):
                for j in range(nj):
                    self.pixelffts[:,i,j] = numpy.fft.fft(array[:,i,j], axis=0)
                    spec = numpy.square(numpy.absolute(self.pixelffts[:,i,j]))
                    self.pixelspectra[:,i,j] = spec
                    self.spec = numpy.add(self.spec, spec)
                    progress += 1
                if not automated:
                    pbvar.set(progress)
                    progresswin.update()

            # note that we (consciously) throw away the zero-frequency part
            # AND the first (lowest frequency > 0), as this frequency 
            # is falsified by the periodic repetition of the function 
            # by the FFT
            self.spec = self.spec[2:round(nt/2)-2]
            # normalize the temporal power spectrum to 1:
            self.spec = self.spec / numpy.sum(self.spec)

            # calculate the corresponding frequencies: 
            self.freqs = numpy.zeros(self.spec.size)
            for i in range(self.spec.size):
                        self.freqs[i] = (i+2) * float(FPS) / float(nimgs)

            if not automated:
                progresswin.destroy()
                s.configure("TProgressbar", thickness=5)

            ylabel = 'Power Spectral Density'
            xlabel = 'Frequency [Hz]'
            labelpad=10
            fontsize=15

            # self.pwspecplot.plot(self.freqs, self.spec, xlabel, ylabel, labelpad, fontsize)

            # slightly smooth the powerspectrum
            self.spec = gaussian_filter(self.spec, sigma=1.0,truncate=1.25)
            # Please note: 
            # the cropped self.freqs (frequency array) and the cropped
            # self.spec array is overgiven!
            self.pwspecplot.plot(self.freqs, self.spec, xlabel, ylabel, labelpad, fontsize)

            # write powerspectrum and frequencies to file: 
            # numpy.savetxt('powerspectrum.dat', self.spec)
            # numpy.savetxt('frequencies.dat', self.freqs)

            # fit the powerspectrum  
            y = self.spec
            x = self.freqs

            # ----- initial values for the fit parameters of the fit_func -----
            # the location of the maximum peak 
            # serves as a first guess for the first gaussian CBF-peak

            # serach location of max:
            maxloc = numpy.argmax(y[numpy.where(self.freqs > 2)])

            a, b, h1 = 0.05, 0.5 ,0.07
            c = 1.0
            mu1 = 7.0
            s1 = 2.3
            h2 = 0.03
            mu2 = 14.0
            s2 = 2.5

            pars0 = [a, b, c, h1, mu1, s1, h2, mu2, s2]

            # -----------------------------------------------------------------
            lower =[0, 0, 0.01,0, 1, 0.01,0, 1, 0.01]
            upper =[1, 1,  5,  1, 25, 5,  1, 50, 5]
            pars, cov = scipy.optimize.curve_fit(f=fit_func, xdata=x, ydata=y,
                p0=pars0, bounds=(lower, upper))

            #print(pars)


            """
            pars holds the following fit parameters:
            we fitted the function:
            f(x) = a*x^(-b) + gauss1(h1,mu1,s1) + gauss2(h2,mu2,s2)
            to the (gaussian-smoothed) power spectral density
            """

            # We need a measure of how well the automated CBF estimate is
            # Instead of the usually used RMSD we need smth like a relative RMSD
            # i.e. for each frequency we measure the RMSD weighted by the
            # amplitude of the powerspectrum
            # This allows to compare between different videos

            # The measure could be termed 'average relative absolute deviation'
            # (between the power spectral density and the fit)

            # We are only interested in the frequency range from 1 to 30 Hz

            average_relative_deviation = 0.
            counter = 0
            for i in range(len(self.spec)):

                if (self.freqs[i] > 1.0) and (self.freqs[i] < 30.0):
                    average_relative_deviation = average_relative_deviation +\
                        math.sqrt((fit_func(self.freqs[i], pars0[0], pars[1],pars[2],pars[3],pars[4],pars[5],pars[6],pars[7],pars[8]) - self.spec[i])**2)
                    counter += 1

            average_relative_deviation = average_relative_deviation / counter

            #print('average relative deviation: ', average_relative_deviation)

            # generate an automated suggestion for minscale and maxscale 
            # 1. order the fitted gaussian according to their peak heights

            peakheights = sorted([pars[3],pars[6]])
            # get index of highest peak in pars:
            pars = pars.tolist() # convert numpy array to list
            h1_ind = pars.index(peakheights[-1]) # higher peak
            h2_ind = pars.index(peakheights[0]) # lower peak

            a = pars[0]
            b = pars[1]
            c = pars[2]

            h1  = pars[h1_ind]
            mu1 = pars[h1_ind+1]
            s1  = pars[h1_ind+2]

            h2 = pars[h2_ind]
            mu2 = pars[h2_ind+1]
            s2 = pars[h2_ind+2]

            if (s1 < 0.2):
                s1 = 0.2
            if (s2 < 0.2):
                s2 = 0.2

            #print('-----------------------------------------------------------')
            #print('a: ',a)
            #print('b: ',b)
            #print('mu1: ', mu1)
            #print('mu2: ', mu2)
            #print('s1: ',s1)
            #print('s2: ',s2)
            #print('-----------------------------------------------------------')

            # check whether the second Gaussian is different from the first one
            # if yes --> take second Gaussian into account
            # if second_gaussian = True -> second Gaussian has to be taken into account
            # Please note that this might be confusing here
            # second_gaussian = True means that the second Gaussian should be
            # considered as to contribute to the CBF bandwidth
            # Please also note: if there are two different peaks within the
            # the CBF-bandwidth, the upper limit can not exceed frequencies
            # above twice the first peak (in order to not take 2nd harmonics into account)

            second_gaussian = False

            if (( (mu2 < mu1-s1) or (mu2 > mu1+s1) ) and (h1/h2 < 5)):
                # check whether the Gaussians are different (True means different)

                # check whether the second Gaussian is a higher harmonic of the
                # first one, or vice versa

                if ( mu1 < mu2 ):
                    # check whether second Gaussian is a higher harm. of the first one
                    # if ( mu2 + s2 < 2 * (mu1-0.5*s1)):
                    if ( mu2 + 0.5*s2 < 2 * mu1):
                        second_gaussian = True

                if ( mu1 > mu2 ):
                    # check whether first Gaussian is a higher harm. of the second one

                    # note: if mu1 > mu2 -> higher peak (at mu1)
                    # corresponds to higher frequency, in this case we relax the
                    # condition below and make it lest strict than if mu1 < mu2

                    if ( mu1 < 2 * mu2 ):
                        second_gaussian = True

            if (second_gaussian):
                # take both Gaussians into account
                if (mu1 >= mu2):
                    # set minscale as local min in interval [mu2-4s2,mu2-1s2]
                    # -> local min closest to mu2! 
                    ind1 = int( round(((mu2-4*s2)*float(nimgs)/float(FPS)))-2)
                    ind2 = int( round(((mu2-1*s2)*float(nimgs)/float(FPS)))-2)
                    ind1 = max(ind1,0) # prevent negative indices
                    ind2 = max(ind2,1)
                    minind=ind2
                    while(self.spec[minind-1] < self.spec[minind]): minind = minind-1
                    #minscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    minscale.set(self.freqs[minind])
                    if (minscale.get() < 1): minscale.set(1)
                    #print('minscale set')

                    # set maxscale as local min in interval [m1+1*s1,mu1+4*s1]
                    ind1 = int(round(((mu1+1*s1)*float(nimgs)/float(FPS)))-2)
                    ind2 = int(round(((mu1+4*s1)*float(nimgs)/float(FPS)))-2)
                    maxind=ind1
                    while(self.spec[maxind+1] < self.spec[maxind]): maxind = maxind+1
                    maxscale.set(self.freqs[maxind])
                    #maxscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    if (maxscale.get() > 2*mu2+1.5*s2): maxscale.set(2*mu2+1.5*s2)
                    #print('maxscale set')

                if (mu1 < mu2):
                    # set minscale as local min in interval [mu1-4s1,mu1-2s1]
                    ind1 = int(round(((mu1-4*s1)*float(nimgs)/float(FPS)))-2)
                    ind2 = int(round(((mu1-1*s1)*float(nimgs)/float(FPS)))-2)
                    ind1 = max(ind1, 0)
                    ind2 = max(ind2, 1)
                    minind=ind2
                    while(self.spec[minind-1] < self.spec[minind]): minind = minind-1
                    minscale.set(self.freqs[minind])
                    if (minscale.get() < 1): minscale.set(1)
                    #minscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    #print('minscale set')

                    # set maxscale as local min in interval [m2+2*s2,mu2+4*s2]
                    ind1 = int(round(((mu2+1*s2)*float(nimgs)/float(FPS)))-2)
                    ind2 = int(round(((mu2+4*s2)*float(nimgs)/float(FPS)))-2)
                    #maxscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    maxind=ind1
                    while(self.spec[maxind+1] < self.spec[maxind]): maxind = maxind+1
                    maxscale.set(self.freqs[maxind])
                    if (maxscale.get() > 2*mu1+1.5*s1): maxscale.set(2*mu1+1.5*s1)
                    #print('maxscale set')
            else:
                # Only first gaussian (dominant peak height) is considered 

                # set minscale as local min in interval [mu1-4s1,mu1-2s1]
                ind1 = int(round(((mu1-4*s1) * float(nimgs) / float(FPS)))-2)
                ind2 = int(round(((mu1-1*s1) * float(nimgs) / float(FPS)))-2)
                # the following lines ensure that the indices are not negative 
                # and that the interval can not be empty

                if (ind2 > 0):
                    ind1 = max(ind1, 0)
                    #ind2 = max(ind2, 1)
                    minind=ind2
                    gfspec = gaussian_filter(self.spec, 1.5, truncate=2.0)
                    while(gfspec[minind-1] < gfspec[minind]): minind = minind-1
                    minscale.set(self.freqs[minind])
                    if (minscale.get() < 1): minscale.set(1)
                    if (minscale.get() > 50): minscale.set(1)
                else:
                    minscale.set(1)
                #minscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                #print('minscale set')

                # set maxscale as local min in interval [m1+2*s1,mu1+4*s1]
                ind1 = int(round(((mu1 + 1 * s1) * float(nimgs) / float(FPS)))-2)
                ind2 = int(round(((mu1 + 4 * s1) * float(nimgs) / float(FPS)))-2)
                maxind=ind1
                while(self.spec[maxind+1] < self.spec[maxind]): maxind = maxind+1
                maxscale.set(self.freqs[maxind])
                #maxscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                if (maxscale.get() > minscale.get()+12): maxscale.set(minscale.get()+12)
                #print('maxscale set')

            # freqs[i] = (i+2) * FPS / nimgs

            #print('2nd gaussian', second_gaussian)

            # add a further condition to maxscale:
            # maxscale can get too large with the above conditions
            # therefore we add that self.spec[minscale] should roughly be the
            # same as self.spec[maxscale]
            minimum_index = int(round(((minscale.get()) * float(nimgs) / float(FPS)))-2)
            maximum_index = int(round(((maxscale.get()) * float(nimgs) / float(FPS)))-2)

            if (self.spec[maximum_index] < self.spec[minimum_index]):
                while (self.spec[maximum_index-2] < self.spec[minimum_index]):
                    maximum_index -= 1
                maxscale.set(float(maximum_index) * (float(FPS)-2) / float(nimgs))

            if (minscale.get() < 1.5): minscale.set(1.5)

            # ------------------------- update plot ---------------------------
            minf = float(minscale.get())
            maxf = float(maxscale.get())
            # fill whole area white (to delete prior selections!)
            self.pwspecplot.axes.fill_between(self.freqs, self.spec,facecolor='white', alpha=1.0)
            # shade first harmonic (selection)
            maxind = numpy.sum(
                (numpy.array(self.freqs) <= maxf).astype(int))
            minind = numpy.sum(
                (numpy.array(self.freqs) <= minf).astype(int))
            self.pwspecplot.axes.fill_between(
                self.freqs[minind:maxind + 1],
                self.spec[minind:maxind + 1], facecolor='gray',
                alpha=0.8)
            self.pwspecplot.canvas.draw()
            # ------------------------------------------------------------------

            # as soon as minscale and maxscale have been set correctly 
            # --> determine CBF 
            self.pwspecplot.get_cbf(float(minscale.get()), float(maxscale.get()), FPS)

            # plot the fit
            x = numpy.array(range(1000))
            x = numpy.divide(x,10)
            y = fit_func(x, pars[0], pars[1], pars[2], pars[3], pars[4], pars[5], pars[6], pars[7], pars[8])
            # self.pwspecplot.axes.plot(x,y, color='orange', linestyle='--')

            return average_relative_deviation

    def peakselection(self,powerspecplot):

        # plot the powerspectrum 
        fig = plt.figure()
        ax = fig.add_subplot(111)

        plt.title("Select Left Limit of Peak")

        # note that line is a Line2D object (matplotlib) 
        line, = ax.plot([], [])
        lx = []

        def onclick(event):
            if event.inaxes!=line.axes: return

            if (len(lx) ==1):
                lx.append(event.xdata)
                plt.axvline(float(lx[0]),color='r')
                plt.axvline(float(lx[1]),color='r')
                line.figure.canvas.draw()
                self.cbf_low = lx[0]
                self.cbf_high = lx[1]
                time.sleep(1)
                plt.close(fig)

            if (len(lx) == 0):
                lx.append(event.xdata)
                line.set_data([lx[0],lx[0]], [numpy.float(0),numpy.float(1)])
                line.set_color('r')
                plt.axvline(float(lx[0]),color='r')
                plt.title("Select Right Limit of Peak")
                line.figure.canvas.draw()

        cid = line.figure.canvas.mpl_connect('button_press_event', onclick)

        plt.ion()
        plt.plot(self.freqs,self.spec, color='0.2',lw=2)
        plt.ylabel('Relative Power Spectral Density',labelpad=15,fontsize=15)
        plt.xlabel('Frequency [Hz]',labelpad=8,fontsize=15)
        plt.xlim(0,150)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        #plt.grid()
        #plt.tight_layout()
        plt.show()

        plt.waitforbuttonpress()
        plt.waitforbuttonpress()


    def delete_content(self):
        """
        Method to remove the content getting displayed in the CBF-tab
        """
        # rebuild the frame (delete its content)  
        self.tkframe.destroy()
        self.tkframe = Frame(self.parent,width=self.parentw,height=self.parenth)
        self.tkframe.place(in_=self.parent, width=self.parentw,height=self.parenth)
        self.tkframe.update()

#    def get_cbf(self,nimgs,FPS): 
#        
#        peakheight = max(self.spec) 
#        low = self.cbf_low 
#        high = self.cbf_high
#
#        #print "low"
#        #print low 
#        #print "high" 
#        #print high 
#
#
#        bot=int(round((float(low)*nimgs/float(FPS))-1)) # transform [Hz] into index
#        top=int(round((float(high)*nimgs/float(FPS))-1))
#
#        self.cbflowind = bot 
#        self.cbfhighind = top 
#
#        # note the ugly "*1.0", which comes from how python deals with references:    
#        weights = self.spec[bot:top] *  1.0 
#
#        peakheight = max(self.spec) 
#        print "peakheight2"
#        print peakheight 
#
#
#
#        normfac = numpy.sum(weights)
#        for i in range(bot,top):
#                weights[i-bot] = weights[i-bot] / normfac
#
#        peakheight = max(self.spec) 
#        print "peakheight3"
#        print peakheight 
#
#
#        freqs = self.freqs[bot:top]
#        mean = 0
#        mean_square = 0
#
#        for c in range(bot,top):
#                mean = mean + weights[c-bot] * freqs[c-bot]
#                mean_square = mean_square + (weights[c-bot] * (freqs[c-bot] * freqs[c-bot]))
#
#        stddev = math.sqrt(mean_square - (mean*mean))
#
#        plt.ioff()
#
#        fig = plt.figure(figsize=(6,4), dpi=80)
#        ax = fig.add_subplot(111)
# 
#        #print "self.spec2"
#        #print self.spec 
#
#        peakheight = max(self.spec) 
#        print "peakheight4"
#        print peakheight 
#
#
#        plt.plot(self.freqs,self.spec, color='0.2',lw=2)
#        plt.ylabel('Relative Power Spectral Density',labelpad=15,fontsize=14)
#        plt.xlabel('Frequency [Hz]',labelpad=8,fontsize=14)
#        plt.xlim(0,35)
#        plt.xticks(fontsize=14)
#        plt.yticks(fontsize=14)
#        
#        #xpos = 0.55*float(35)
#        #ypos = float(peakheight)*0.75
#        
#        xpos = 0.55
#        ypos = 0.9 
#        str1 = "$CBF = $"
#        str2 = "$%.1f$" %mean
#        str3 = "$\pm$"
#        str4 = "$%.1f$" %stddev
#        str5 = " [Hz]"
#        plt.text(xpos,ypos,str1+str2+str3+str4+str5,transform=ax.transAxes,fontsize=14)
#        plt.grid()
#        plt.tight_layout()
#        #plt.show()
#        plt.savefig('powerspec.png', bbox_inches = 'tight') 
#        plt.close(fig) 

