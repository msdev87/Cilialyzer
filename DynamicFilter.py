import numpy 
import PIL 
import scipy 
#from scipy.misc import bytescale 
from bytescl import bytescl 

import sys 

import math 

import os
if os.sys.version_info.major > 2:
    from tkinter import *
else:
    from tkinter import *

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

#from matplotlib.backends.backend_tk import FigureCanvasTk, NavigationToolbar2Tk
from matplotlib.figure import Figure

import matplotlib.pyplot as plt


from mpl_toolkits.axes_grid1 import make_axes_locatable



numpy.set_printoptions(threshold=sys.maxsize)

class DynFilter:
    
    
    def __init__(self):
        self.dyn_roiseq = []
        self.corr_roiseq = []
        self.tkframe = None

        self.profileframe = None 

        self.kxkyplotax = None  
        self.kxkyrows = None 
        self.kxkycols = None 
        self.kxky = None 
        self.splitline = None 


        
    def bandpass(self, PILseq, fps, minf, maxf,nharms):
        
        # input: roiseq 
        # output: dynamically filtered roiseq 
        
        # dynamic filtering: bandpass -> keep frequencies f : minf <= f <= maxf 
        
        firstimg = PILseq[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        nimgs = len(PILseq) # number of images  
        
        # create numpy array 'array' 
        array = numpy.zeros((int(nimgs),int(height),int(width)))  
        for i in range(nimgs):
            array[i,:,:] = numpy.array(PILseq[i])   
        (nt,ni,nj) = numpy.shape(array)
       

        # determine the frequency band to be filtered (under consideration of nrharms) 
         

        # remove frequency if not contained in any band
        
        filt = numpy.zeros(nt)
    
       
        # ---------- get indices of 'cbf band' -> keep fundamental freq --------
        # we also have to filter in the negative frequency domain!  
        minf1 = int(round((float(nimgs)*minf/float(fps))-1))
        maxf1 = int(round((float(nimgs)*maxf/float(fps))-1))
          
        filt[minf1:maxf1+1] = 1.0 
   
        # get corresponding negative frequencies:
        filt[-maxf1:-minf1+1] = 1.0  

        # ---------------------------------------------------------------------- 


        # ------------------ keep second harmonic freq band --------------------
        if (nharms > 1):

            peakw = maxf - minf 
            peakf = minf + 0.5 * peakw  
       
            sminf = 2.0 * peakf - 0.5 * peakw  
            smaxf = 2.0 * peakf + 0.5 * peakw  

            minf2 = int(round((float(nimgs)*sminf/float(fps))-1))
            maxf2 = int(round((float(nimgs)*smaxf/float(fps))-1))
  
            filt[minf2:maxf2+1] = 1.0 
            # corr. negative freqs: 
            filt[-maxf2:-minf2+1] = 1.0  


        
        # ------------------ keep third harmonic freq band --------------------
        if (nharms > 2): 
       
            tminf = 3.0 * peakf - 0.5 * peakw  
            tmaxf = 3.0 * peakf + 0.5 * peakw  

            minf3 = int(round((float(nimgs)*tminf/float(fps))-1))
            maxf3 = int(round((float(nimgs)*tmaxf/float(fps))-1))

            
           
  
            filt[minf3:maxf3+1] = 1.0 
            # corr. negative freqs: 
            filt[-maxf3:-minf3+1] = 1.0  

   
        # ----------------------------------------------------------------------



        numpy.set_printoptions(threshold=sys.maxsize)
        #print(filt)


       
      
        # dynamic filtering for each pixel separately! (in time domain)   
       
        # loop over pixels (spatial domain)  
        # apply bandpass for pixel after pixel 

        for i in range(ni):
            for j in range(nj):

                array[:,i,j] = numpy.real(numpy.fft.ifft(numpy.multiply(numpy.fft.fft(array[:,i,j],axis=0),filt),axis=0))



        array = bytescl(array)

        # inverse transform 
        #array = bytescl(numpy.real(numpy.fft.ifftn(array)))
         
        #print "inverse fft:"
        #print array 
        
        # create PIL sequence from numpy array!
        
        print(numpy.shape(array)) 

        for i in range(nimgs):
            self.dyn_roiseq.append(PIL.Image.fromarray(numpy.uint8(array[i,:,:])))
        
        
        
        
     
    def spatiotempcorr(self,fps,minf,maxf):

        # calc spatio-temporal correlation 
        nimgs = len(self.dyn_roiseq)
        firstimg = self.dyn_roiseq[0]
        width, height = firstimg.size
        
        # corr: spatial correlogram 
        corr = numpy.zeros((height,width)) # 2x w,h -> zero-padding 
        scorr = numpy.zeros((height,width))        

        img1 = numpy.zeros((height,width))
        img2 = numpy.zeros((height,width))
        
        # calc the cross-corr for pairs of images (img1 and img2) 
	
        maxtimeshift = 10

        #self.corr_roiseq = numpy.zeros((maxtimeshift,2*height,2*width))

        nrcorr = nimgs 

        # loop over time and timeshifts 
        for deltat in range(maxtimeshift): 
            scorr[:,:] = 0.0 
            for t in range(nrcorr-maxtimeshift):
   
                # get image pair 
                img1[0:height,0:width] = numpy.array(self.dyn_roiseq[t]) 
                img2[0:height,0:width] = numpy.array(self.dyn_roiseq[t+deltat])

                img1 = img1 - numpy.mean(img1[0:height,0:width])
                img2 = img2 - numpy.mean(img2[0:height,0:width]) 

                # calc corr of img1 and img2 
                fft1 = numpy.fft.fftn(img1) 
                fft2 = numpy.fft.fftn(img2)

                prod = numpy.multiply(fft1,numpy.conjugate(fft2)) / float(width*height)
                #ifft = numpy.real(numpy.fft.ifftn(prod))
                ifft = numpy.real(numpy.fft.ifftn(prod))

                stdv1 = numpy.std(img1)
                stdv2 = numpy.std(img2)
        
                #corr = numpy.absolute(numpy.subtract(ifft,(numpy.mean(img1) * numpy.mean(img2))))
                corr = numpy.subtract(ifft,(numpy.mean(img1) * numpy.mean(img2)))
                corr = corr / (stdv1 * stdv2)
                #corr = corr + 1 
                scorr = numpy.add(scorr,corr)#,numpy.absolute(corr)) 

               	
            scorr = scorr / float(nrcorr)
            scorr = numpy.fft.fftshift(scorr)
            print("max scorr ", numpy.amax(scorr), " min scorr ", numpy.amin(scorr)) 

            scorr = scorr + 1 
            #scorr = (scorr - numpy.amin(scorr)) / (numpy.amax(scorr) - numpy.amin(scorr)) * 255.0 
            scorr = scorr * 127

            li = len(scorr[:,0])
            lj = len(scorr[0,:]) 
            self.corr_roiseq.append(PIL.Image.fromarray(numpy.uint8(scorr[(round(li/2)-round(li/4)):(round(li/2)+round(li/4)),(round(lj/2)-round(lj/4)):(round(lj/2)+round(lj/4))])))
        


	
    def kspec(self,fps,minf,maxf,tkparent):
        
        #print("start calc kxky")  
        nimgs = len(self.dyn_roiseq)
        firstimg = self.dyn_roiseq[0]
        width, height = firstimg.size

        #print("nr of images: ", nimgs) 


        array = numpy.zeros((int(nimgs),int(height),int(width)))
        for i in range(nimgs):
            array[i,:,:] = numpy.array(self.dyn_roiseq[i])


        # 3D fft         
        fftarray = numpy.fft.fftn(array)   
        
        # sum over positive frequencies, which actually are the NEGATIVE frequencies 
        # (technical vs.physical FFT definition) 
	
        r = round(nimgs/2) - 1 # number of freqs to sum over   

        kxky = numpy.zeros((height,width),dtype=float)
        
        for i in range(round(nimgs/2)-1):
            # sum over the NEGATIVE frequency domain! 
            f = i + round(nimgs/2+1)
            kxky = numpy.add(kxky,numpy.square(numpy.absolute(fftarray[f,:,:])))

        kxky[0,0] = 0.0
        kxky = kxky / numpy.sum(kxky)
        kxky = numpy.fft.fftshift(kxky)

        # plot kxky 
        # print("kxky calculated")

        plt.ion() 
        fig = Figure(figsize=(6,5), dpi=100)
        self.kxkyplotax = fig.add_subplot(111) 
        self.tkframe = Frame(tkparent)
        self.tkframe.pack(expand=1,fill=BOTH)

        can = FigureCanvasTkAgg(fig, self.tkframe)

        ys = round(len(kxky[:,0])/2) - round(len(kxky[:,0])/8) 
        ye = round(len(kxky[:,0])/2) + round(len(kxky[:,0])/8) + 1  
        xs = round(len(kxky[0,:])/2) - round(len(kxky[0,:])/8) 
        xe = round(len(kxky[0,:])/2) + round(len(kxky[0,:])/8) + 1  
       
        self.kxkyrows = ye - ys   
        self.kxkycols = xe - xs  

        self.kxky = kxky 


        la1 = self.kxkyplotax.imshow(kxky[ys:ye,xs:xe], alpha=1.0,cmap='bwr',interpolation='none')
        #self.splitline, = self.kxkyplotax.plot([3,3],[10,10], color='green',linewidth=5)
       
        
        #if ((len(kxky[ys:ye,0]) % 2) == 0):
        #    self.kxkyplotax.axes.axhline(y=round(len(kxky[ys:ye,0]))-round(len(kxky[ys:ye,0])/2),color='w',linewidth=1)
        #else: 
        #    self.kxkyplotax.axes.axhline(y=round(len(kxky[ys:ye,0]))-round(len(kxky[ys:ye,0])/2),color='w',linewidth=1)
  
        #if ((len(kxky[0,xs:xe]) % 2) == 0): 
        #    self.kxkyplotax.axes.axvline(x=round(len(kxky[0,xs:xe]))-round(len(kxky[0,xs:xe])/2),color='w',linewidth=1)
        #else: 
        #    self.kxkyplotax.axes.axvline(x=round(len(kxky[0,xs:xe]))-round(len(kxky[0,xs:xe])/2),color='w',linewidth=1)
 









        #####################################################################
        # filtering in the wave vector domain # 

   

        #fftarray[:,:,:] = 0.0         

        fftarray[0:round(nimgs/2),:,:] = 0.0 
        fftarray[:,round(width/2+1):,:] = 0.0 




        # rücktransformation 

        array = numpy.real(numpy.fft.ifftn(fftarray))
        array = bytescl(array)

        print(array) 

        
        self.dyn_roiseq = [] 

        for i in range(nimgs):
            self.dyn_roiseq.append(PIL.Image.fromarray(numpy.uint8(array[i,:,:])))
        ###################################################################### 
        print('------------- test -----------------')  
    

     
        self.kxkyplotax.set_title('Spatial Power Spectral Density')
        divider = make_axes_locatable(self.kxkyplotax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar=fig.colorbar(la1,cax=cax)  
        
        
        self.kxkyplotax.axes.get_xaxis().set_ticks([])
        self.kxkyplotax.axes.get_yaxis().set_ticks([])   


        can.draw()
        can.get_tk_widget().pack() 
        can._tkcanvas.pack()















          

    def mscorr(self,fps,minf,maxf,tkparent,tkparent2,pixsize):

        # calc mean spatial autocorrelation 

        nimgs = len(self.dyn_roiseq)
        firstimg = self.dyn_roiseq[0]
        width, height = firstimg.size
       
        #print('width', width) 
        #print('height', height) 

        # corr: spatial correlogram 
        corr = numpy.zeros((height,width)) # 2x w,h -> zero-padding 
        scorr = numpy.zeros((height,width))        

        img1 = numpy.zeros((height,width),dtype=float)
        img2 = numpy.zeros((height,width),dtype=float)

        
        # loop over time 
        
        scorr[:,:] = 0.0 


        for t in range(nimgs):

            # get image pair  
            img1[:,:] = numpy.array(self.dyn_roiseq[t]) 
            img2[:,:] = numpy.array(self.dyn_roiseq[t])

            #print('img1')
            #print(img1) 
            #print(img1.dtype)
            #print(img1.shape) 


            #img1 = img1 - numpy.mean(img1[:,:])
            #img2 = img2 - numpy.mean(img2[:,:]) 

            #print(img1) 

            # calc corr of img1 and img2 
            fft1 = numpy.fft.fft2(img1)
            fft2 = numpy.fft.fft2(img2)

            prod = numpy.multiply(fft1,numpy.conjugate(fft2)) / float(width*height)
            ifft = numpy.real(numpy.fft.ifft2(prod))

            stdv1 = numpy.std(img1)
            stdv2 = numpy.std(img2)
        
            corr = numpy.subtract(ifft,(numpy.mean(img1) * numpy.mean(img2)))
            corr = corr / (stdv1 * stdv2)
                
            scorr = numpy.add(scorr,corr)#,numpy.absolute(corr)) 
               	
        scorr = scorr / float(nimgs)
        scorr = numpy.fft.fftshift(scorr)
         

        # plot the mean spatial autocorrelation:  

        li = len(scorr[:,0])
        lj = len(scorr[0,:]) 

        # nicht als sequenz abspeichern -> einfach plotten!

        fig = Figure(figsize=(6,5), dpi=100)
        ax = fig.add_subplot(111)

        self.tkframe = Frame(tkparent)
        self.tkframe.pack(expand=1,fill=BOTH)

        can = FigureCanvasTkAgg(fig, self.tkframe)

        xs = round(li/2)-round(li/4)
        xe = round(li/2)+round(li/4)
        ys = round(lj/2)-round(lj/4) 
        ye = round(lj/2)+round(lj/4) 
         

        # axis tick labels for correlogram plot
        

        
        #la1= ax.imshow(scorr[xs:xe,ys:ye], alpha=1.0,cmap='bwr',interpolation='none')
        xmin, xmax, ymin, ymax = -0.5*lj*pixsize,0.5*lj*pixsize,-0.5*li*pixsize,0.5*li*pixsize   
        la1= ax.imshow(scorr, alpha=1.0,cmap='bwr',interpolation='none',extent=[xmin,xmax,ymin,ymax])
        
        ax.set_title('Mean Spatial Autocorrelation') 
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar=fig.colorbar(la1,cax=cax)  
 
        cbar.ax.tick_params(labelsize=17) 
 


        ax.axes.tick_params(labelsize=17) 


        #ax.axes.get_xaxis().set_ticks([])
        #ax.axes.get_yaxis().set_ticks([])       

        #ax.axes.axhline(y=round(len(scorr[xs:xe,0])-1)-round(len(scorr[xs:xe,0])/2),color='w',linewidth=2)
        #ax.axes.axvline(x=round(len(scorr[0,ys:ye])-1)-round(len(scorr[0,ys:ye])/2),color='w',linewidth=2)

        can.draw()
        can.get_tk_widget().pack() 
        can._tkcanvas.pack()

        ########################################################################
        # plot the profile along the horizontal 
        
        x0, y0 = 0, li//2   # in pixel coords 
        x1, y1 = lj, li//2 


        #n = lj 
        #x, y = numpy.linspace(x0, x1, n), numpy.linspace(y0, y1, n)

        #print(x) 

        # extract the values along the line defined by xi,yi and 
        # make use of a cubic interpolation 
        #zi = scipy.ndimage.map_coordinates(scorr, numpy.vstack((x,y)),order=1, mode='nearest' )
      

        #x = numpy.array(range(lj)) 
        #y = numpy.zeros(lj) + li//2 

        zi = numpy.zeros(lj) 
        for i in range(lj):
            zi[i] = scorr[li//2, i]  

        print(zi)
        fig = Figure(figsize=(6,5), dpi=100)
        ax = fig.add_subplot(111)

        self.profileframe = Frame(tkparent2)
        self.profileframe.pack(expand=1,fill=BOTH)

        can = FigureCanvasTkAgg(fig, self.profileframe)
       


        ax.axes.tick_params(labelsize=17)

        xax = pixsize * (numpy.array(range(lj)) - lj/2)  

        ax.plot(xax,zi,linewidth=2,color='0.3')  
        
        #ax.set_title('Mean Spatial Autocorrelation') 
        #divider = make_axes_locatable(ax)
        #cax = divider.append_axes("right", size="5%", pad=0.05)
        #fig.colorbar(la1,cax=cax)  
 

        can.draw()
        can.get_tk_widget().pack() 
        can._tkcanvas.pack()










       

        #######################################################################
        #######################################################################

        # determine the direction of maximum correlation
        # and plot the cross-section of the 2D mean spatial autocorrelation 
        
        # first, get the location of the maximum in scorr:
        """
        ind = np.unravel_index(np.argmax(scorr, axis=None), scorr.shape)
        maxi = ind[0]
        maxj = ind[1] 

        steps = 360 

        diri = numpy.zeros(li) 
        dirj = numpy.zeros(lj) 

        summe = numpy.zeros(steps)  
        summ = 0.
        maxdirection = 0. 

        cas = 0 # determines if change along i, or change along j dominates 
 
        for i in range(steps):
	    
            alpha = i * (360. / float(steps))
	    rad = alpha * 2. * math.pi / 360.   
	
	    m = sin(rad) / cos(rad) # slope m  
	    q = maxi - fix(m * maxj) # abszisse q  

            if ((alpha < 45.0) or (alpha > 315.0)): 
	        # change along j dominates
		diri = m * dirj + q 
		cas = 0				
	    
            if ((alpha < 135.0) and (alpha > 45.0)):
	        # change along i dominates		
		dirj = (diri - q) / m
		cas = 1  	
	
            if ((alpha > 135.0) and (alpha < 225.0)):  
	        # change along j dominates			
		diri = m * dirj + q 				
		cas = 0
	
            if ((alpha > 225.0) and (alpha < 315.0)):
	        # change along i dominates			
		dirj = (diri - q) / m 
		cas = 1

				
	    indices_i = numpy.around(diri) 				
	    indices_j = numpy.around(dirj) 			
		
        """   	



      







