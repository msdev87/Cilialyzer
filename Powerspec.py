import numpy
import matplotlib.pyplot as plt
import time
import math

import TkPowerspecPlot
import os
if os.sys.version_info.major > 2:
    from tkinter import *
else:
    from tkinter import *

import tkinter.ttk


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
        
        #self.tkframe.pack(expand=1,fill=BOTH)
        self.tkframe.pack()
        self.tkframe.update() 
        self.pwspecplot = TkPowerspecPlot.TkPowerspecPlot(self.tkframe)
        self.pixelspectra = None
        self.pixelffts = None



    def calc_powerspec(self,roiseq,FPS,parent):

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

            #print "type"
            #print type(roiseq) 
            firstimg = roiseq[0] # first image of roi sequence  
            width, height = firstimg.size # dimension of images 
            nimgs = len(roiseq) # number of images   

            # initialize numpy float array, which will hold the image sequence  
            array = numpy.zeros((int(nimgs),int(height),int(width)))  

            #array = numpy.array(array,dtype=float) 

            for i in range(nimgs):
                array[i,:,:] = numpy.array(roiseq[i])   

            (nt,ni,nj) = numpy.shape(array)

            print('shape of array: ',nt,ni,nj)

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
            # ********************************************************************#

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
            fontsize=14

            #powerspecplot.plot(self.freqs,self.spec,xlabel,ylabel,labelpad,fontsize) 

            self.pwspecplot.plot(self.freqs, self.spec, xlabel, ylabel, labelpad, fontsize)



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
        plt.ylabel('Relative Power Spectral Density',labelpad=15,fontsize=14)
        plt.xlabel('Frequency [Hz]',labelpad=8,fontsize=14)
        plt.xlim(0,50) 
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        #plt.grid()
        #plt.tight_layout()
        plt.show()

        
        plt.waitforbuttonpress()  
        plt.waitforbuttonpress()  
      




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


