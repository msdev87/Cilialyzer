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



def decay_func(x, a, b):
    # f(x) = a * x^(-b)
    return a * (x**(-b))

def gauss_func(x,a,b,c):
    # f(x) = a * exp( - (x-b)**2 / 2c**2)
    return a * numpy.exp(-(x-b)**2 / (2*c**2))

def fit_func(x, d1, d2, g1a, g1b, g1c, g2a, g2b, g2c):
    return decay_func(x, d1, d2) + gauss_func(x, g1a, g1b, g1c) + gauss_func(x, g2a, g2b, g2c)

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


        #self.tkframe.pack(expand=1,fill=BOTH)
        self.tkframe.pack()
        self.tkframe.update()
        self.pwspecplot = TkPowerspecPlot.TkPowerspecPlot(self.tkframe)
        self.pixelspectra = None
        self.pixelffts = None

    def calc_powerspec(self,roiseq,FPS,parent,minscale,maxscale):

        # check whether the input data is adequately set:
        if (len(roiseq)) < 10:
            messagebox.showerror(title = "Error", message = "Please select a directory")

        else:

            # rebuild the frame (deletes its content)  
            self.tkframe.destroy()
            self.tkframe = Frame(parent,width=self.parentw,height=self.parenth)
            #self.tkframe.pack(expand=1,fill=BOTH)
            self.tkframe.pack()
            self.tkframe.update()
            #print('newtest', self.tkframe.winfo_width())
            self.pwspecplot = TkPowerspecPlot.TkPowerspecPlot(self.tkframe)


            firstimg = roiseq[0] # first image of roi sequence  
            width, height = firstimg.size # dimension of images 
            nimgs = len(roiseq) # number of images   

            # initialize numpy float array, which will hold the image sequence  
            array = numpy.zeros((int(nimgs),int(height),int(width)))

            for i in range(nimgs):
                array[i,:,:] = gaussian_filter(numpy.array(roiseq[i]),sigma=0.75)


            # slight gaussian smoothing along time axis:
            for i in range(height):
                for j in range(width):
                    array[:,i,j] = gaussian_filter(array[:,i,j], sigma=0.75)


            (nt,ni,nj) = numpy.shape(array)

            # print('shape of array: ',nt,ni,nj)

            # create a toplevel window to display the progress indicator
            # caution: the feedback to the frontend slows down the cbf calculation!
            # ******************************************************************* #
            progresswin = Toplevel()
            progresswin.minsize(width=500,height=30)
            progresswin.title("Powerspectrum in Progress, Please Wait...")

            # get the monitor dimensions:
            screenw = progresswin.winfo_screenwidth()
            screenh = progresswin.winfo_screenheight()

            # place the progress indicator in the center of the screen 
            placement = "+%d+%d" % (screenw/2-300,screenh/2-15)
            progresswin.geometry(placement)

            s = tkinter.ttk.Style()
            s.theme_use("default")
            s.configure("TProgressbar", thickness=30)

            pbvar = IntVar() # progress bar variable (counting the number of loaded images)   
            pb=tkinter.ttk.Progressbar(progresswin,mode="determinate",variable=pbvar,\
                maximum=ni*nj,length=600,style="TProgressbar")
            pb.grid(row=1,column=0,pady=5)
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
                pbvar.set(progress)
                progresswin.update()

            # note that we (conciously) throw away the zero-frequency part
            self.spec = self.spec[1:round(nt/2)]
            self.spec = self.spec / numpy.sum(self.spec)

            #print('--------------------------------------------------')
            #print('test if self.spec is properly normalized to 1:')
            #print(numpy.sum(self.spec))
            #print('--------------------------------------------------')

            # calculate the corresponding frequencies: 
            self.freqs = numpy.zeros(self.spec.size)
            for i in range(self.spec.size):
                self.freqs[i] = (i+1) * float(FPS) / float(nimgs)

            progresswin.destroy()
            s.configure("TProgressbar", thickness=5)

            ylabel = 'Power Spectral Density'
            xlabel = 'Frequency [Hz]'
            labelpad=10
            fontsize=15

            # self.pwspecplot.plot(self.freqs, self.spec, xlabel, ylabel, labelpad, fontsize)

            # slightly smooth the powerspectrum
            self.spec = gaussian_filter(self.spec, sigma=1)
            self.pwspecplot.plot(self.freqs, self.spec, xlabel, ylabel, labelpad, fontsize)

            # write powerspectrum and frequencies to file: 
            numpy.savetxt('powerspectrum.dat', self.spec)
            numpy.savetxt('frequencies.dat', self.freqs)

            # fit the powerspectrum  
            y = self.spec
            x = self.freqs

            # ----- initial values for the fit parameters of the fit_func -----
            # the location of the maximum peak 
            # serves as a first guess for the first gaussian CBF-peak

            # serach location of max:
            maxloc = numpy.argmax(y)

            a = 0.5
            b = 0.5
            h1 = 0.1
            mu1 = x[maxloc]
            s1 =  mu1/3.0
            h2 = 0.7 * h1
            mu2 = 1.8 * mu1
            s2 = s1

            pars0 = [a, b, h1, mu1, s1, h2, mu2, s2]

            # -----------------------------------------------------------------

            pars, cov = scipy.optimize.curve_fit(f=fit_func, xdata=x, ydata=y, p0=pars0, bounds=(0,50))

            """
            pars holds the following fit parameters:
            we fitted the function:
            f(x) = a*x^(-b) + gauss1(h1,mu1,s1) + gauss2(h2,mu2,s2)
            to the (gaussian-smoothed) power spectral density
            """

            # generate an automated suggestion for minscale and maxscale 
            # 1. order the fitted gaussian according to their peak heights

            peakheights = sorted([pars[2],pars[5]])
            # get index of highest peak in pars:
            pars = pars.tolist() # convert numpy array to list
            h1_ind = pars.index(peakheights[-1]) # higher peak
            h2_ind = pars.index(peakheights[0]) # lower peak

            a = pars[0]
            b = pars[1]

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

            print('-----------------------------------------------------------')
            print('a: ',a)
            print('b: ',b)
            print('mu1: ', mu1)
            print('mu2: ', mu2)
            print('s1: ',s1)
            print('s2: ',s2)
            print('-----------------------------------------------------------')

            # check whether the second Gaussian is different from the first one
            # if yes --> take second Gaussian into account
            # if second_gaussian = True -> second Gaussian has to be taken into account
            second_gaussian = False

            if ( (mu2 < mu1-s1) or (mu2 > mu1+s1) ):
                # check whether the Gaussians are different (True means different)

                # check whether the second Gaussian is a higher harmonic of the
                # first one, or vice versa

                if ( mu1 < mu2 ):
                    # check whether second Gaussian is a higher harm. of the first one
                    if ( mu2 + s2 < 2 * (mu1-0.5*s1)):
                        second_gaussian = True

                if ( mu1 > mu2 ):
                    # check whether first Gaussian is a higher harm. of the second one
                    if ( mu1 + s1 < 2 * (mu2-0.5*s2) ):
                        second_gaussian = True

            if (second_gaussian):
                # take both Gaussians into account
                if (mu1 > mu2):
                    # set minscale as local min in interval [mu2-4s2,mu2-2s2]
                    ind1 = int( round(((mu2-4*s2)*float(nimgs)/float(FPS))-1))
                    ind2 = int( round(((mu2-2*s2)*float(nimgs)/float(FPS))-1))
                    ind1 = max(ind1,0) # prevent negative indices
                    ind2 = max(ind2,1)

                    minscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    #minscale.set(self.freqs[int(numpy.where(self.spec == numpy.amin(self.spec[ind1:ind2]))[0][0])])

                    # set maxscale as local min in interval [m1+2*s1,mu1+4*s1]
                    ind1 = int(round(((mu1+2*s1)*float(nimgs)/float(FPS))-1))
                    ind2 = int(round(((mu1+4*s1)*float(nimgs)/float(FPS))-1))

                    maxscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    #maxscale.set(self.freqs[int(numpy.where(self.spec == numpy.amin(self.spec[ind1:ind2]))[0][0])])

                if (mu1 < mu2):
                    # set minscale as local min in interval [mu1-4s1,mu1-2s1]
                    ind1 = int(round(((mu1-4*s1)*float(nimgs)/float(FPS))-1))
                    ind2 = int(round(((mu1-2*s1)*float(nimgs)/float(FPS))-1))
                    ind1 = max(ind1, 0)
                    ind2 = max(ind2, 1)
                    print('test')
                    print('ind1: ',ind1)
                    print('ind2: ',ind2)

                    minscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    #minscale.set(self.freqs[int(numpy.where(self.spec == numpy.amin(self.spec[ind1:ind2]))[0][0])])

                    # set maxscale as local min in interval [m2+2*s2,mu2+4*s2]
                    ind1 = int(round(((mu2+2*s2)*float(nimgs)/float(FPS))-1))
                    ind2 = int(round(((mu2+4*s2)*float(nimgs)/float(FPS))-1))

                    maxscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                    #maxscale.set(self.freqs[int(numpy.where(self.spec == numpy.amin(self.spec[ind1:ind2]))[0][0])])
            else:

                # only first gaussian (dominant peak height) is taken into account

                # set minscale as local min in interval [mu1-4s1,mu1-2s1]
                ind1 = int(round(((mu1 - 4 * s1) * float(nimgs) / float(FPS)) - 1))
                ind2 = int(round(((mu1 - 2 * s1) * float(nimgs) / float(FPS)) - 1))

                # the following lines ensure that the indices are not negative 
                # and that the interval can not be empty  
                ind1 = max(ind1, 0)
                ind2 = max(ind2, 1)

                print('-----------------------------------------------------------')
                print('minscale')
                print('ind1 ',ind1,' ind2 ',ind2)
                print('freq[ind1] ', self.freqs[ind1],' freq[ind2] ',self.freqs[ind2])
                print('-----------------------------------------------------------')

                minscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                #minscale.set(self.freqs[int(numpy.where(self.spec == numpy.amin(self.spec[ind1:ind2]))[0][0])])

                # set maxscale as local min in interval [m1+2*s1,mu1+4*s1]
                ind1 = int(round(((mu1 + 2 * s1) * float(nimgs) / float(FPS)) - 1))
                ind2 = int(round(((mu1 + 4 * s1) * float(nimgs) / float(FPS)) - 1))
                print('-----------------------------------------------------------')
                print('maxscale')
                print('ind1 ',ind1,' ind2 ',ind2)
                print('freq[ind1] ',self.freqs[ind1],' freq[ind2] ',self.freqs[ind2])
                print('-----------------------------------------------------------')

                maxscale.set(self.freqs[ind1+numpy.argmin(self.spec[ind1:ind2])])
                #maxscale.set(self.freqs[int(numpy.where(self.spec == numpy.amin(self.spec[ind1:ind2]))[0][0])])

            # freqs[i] = (i+1) * FPS / nimgs

            # as soon as minscale and maxscale have been set correctly 
            # --> determine CBF 
            self.pwspecplot.get_cbf(float(minscale.get()), float(maxscale.get()), FPS)

            # plot the fit
            #x = numpy.array(range(1000))
            #x = numpy.divide(x,10)
            #y = fit_func(x, pars[0], pars[1], pars[2], pars[3], pars[4], pars[5], pars[6], pars[7])

            #self.pwspecplot.axes.plot(x,y)


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

        self.tkframe.pack()
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

