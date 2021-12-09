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

import smooth

numpy.set_printoptions(threshold=sys.maxsize)

#from scipy import signal

from scipy.optimize import curve_fit


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

        #print(array) 

        self.dyn_roiseq = []

        for i in range(nimgs):
            self.dyn_roiseq.append(PIL.Image.fromarray(numpy.uint8(array[i,:,:])))
        ###################################################################### 
        print('------------------------- test -----------------')

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

        # mscorr calculates the mean spatial autocorrelation
        # over several images of the image sequence 

        # def gaussian(x, a, b, c):
        # return a*numpy.exp(-numpy.power(x - b, 2)/(2*numpy.power(c, 2)))

        def exponential(x,a,b):
            return a*numpy.exp(-abs(x/b))

        nimgs = len(self.dyn_roiseq)
        print('nimgs', nimgs)
        firstimg = self.dyn_roiseq[0]
        width, height = firstimg.size

        # corr: spatial correlogram 
        corr = numpy.zeros((height,width))
        scorr = numpy.zeros((height,width)) # sum (over time) of spatial acorrs 

        # 2D arrays, which will be correlated
        img1 = numpy.zeros((height,width),dtype=float)
        img2 = numpy.zeros((height,width),dtype=float)

        # as the spatial autocorrelation hardly varies over time
        # we do not have to average over the whole image stack
        # consequently, the average over 50 images is a good approximation 
        # for the overall average 

        nimgs = 50

        for t in range(nimgs): # loop over time

            # pair of images, which we correlate 
            img1[:,:] = numpy.array(self.dyn_roiseq[t])
            img2[:,:] = numpy.array(self.dyn_roiseq[t])

            # calculate the correlation between img1 and img2
			# given by the inverse FFT of the product: FFT(img1)*FFT(img2)

            fft1 = numpy.fft.fft2(img1)
            fft2 = numpy.fft.fft2(img2)

            prod = numpy.multiply(fft1,numpy.conjugate(fft2)) / float(width*height)
            ifft = numpy.real(numpy.fft.ifft2(prod))

            stdv1 = numpy.std(img1)
            stdv2 = numpy.std(img2)

            corr = numpy.subtract(ifft,(numpy.mean(img1) * numpy.mean(img2)))
            corr = corr / (stdv1 * stdv2)

            scorr = numpy.add(scorr,corr)

        scorr = scorr / float(nimgs)
        scorr = numpy.fft.fftshift(scorr)

        scorr = numpy.squeeze(scorr) # get rid of extra dimensions


        # FOR TEST write scorr out for tests 
        #numpy.savetxt('scorr.dat',scorr)



        # 'scorr' holds now the two-dimensional mean spatial autocorrelation
		# based on which we determine the metachronal wavelength 
		# according to Ryser et al. 2007 

        # the metachronal wavelength is characterized by the distance between 
        # the two minima in the mean spatial autocorrelation

        # plot the mean spatial autocorrelation 
        # together with the line connecting the two correlation minima   

        nrows = len(scorr[:,0]) # number of rows
        ncols = len(scorr[0,:]) # number of columns

        fig = Figure(figsize=(6,5), dpi=100)
        ax = fig.add_subplot(111)

        self.tkframe = Frame(tkparent)
        self.tkframe.pack(expand=1,fill=BOTH)

        can = FigureCanvasTkAgg(fig, self.tkframe)

		# only the center of scorr is interesting
        # xs = round(nrows/2)-round(nrows/8)
        # xe = round(nrows/2)+round(nrows/8)
        # ys = round(ncols/2)-round(ncols/8)
        # ye = round(ncols/2)+round(ncols/8)
        # axis tick labels for correlogram plot
        # la1= ax.imshow(scorr[xs:xe,ys:ye], alpha=1.0,cmap='bwr',interpolation='none')
        # xmin, xmax = -0.125*ncols*pixsize*0.001,0.125*ncols*pixsize*0.001
        # ymin, ymax = -0.125*nrows*pixsize*0.001,0.125*nrows*pixsize*0.001
        # la1= ax.imshow(scorr[xs:xe,ys:ye],alpha=1.0,cmap='bwr',interpolation='none',
        # extent=[xmin,xmax,ymin,ymax])








        # 2D colormap of scorr
        xmin=-ncols/2.0*pixsize*0.001
        xmax=-xmin
        ymin=nrows/2.0*pixsize*0.001
        ymax=-ymin

        print('ncols',ncols)
        print('nrows',nrows)
        print('xmin,xmax,ymin,ymax ',xmin, xmax, ymin, ymax)


        la1 = ax.imshow(scorr,alpha=1.0,cmap='bwr',interpolation='none',extent=[xmin,xmax,ymin,ymax])

        #ax.set_title('Mean Spatial Autocorrelation',fontsize=16)
        ax.set_xlabel("$\Delta$x [$\mu$m]",fontsize=16)
        ax.set_ylabel("$\Delta$y [$\mu$m]",fontsize=16)



        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar=fig.colorbar(la1,cax=cax)
        cbar.ax.tick_params(labelsize=15)
        ax.axes.tick_params(labelsize=15)

        ########################################################################
        # plot the profile of the correlogram along the line 
        # connecting the two minima (and the global maximum)

        # get the location of the extrema in scorr (in pixel coordinates) 
        maxy, maxx = numpy.unravel_index(numpy.argmax(scorr,axis=None),scorr.shape)
        miny, minx = numpy.unravel_index(numpy.argmin(scorr,axis=None),scorr.shape)

        # get the profile along the line, which is given by the connection 
        # of the maximum and minimum coordinates

		# calculate the 2D distance matrix 'distmat' (in pixels)        
        distmat = numpy.zeros(scorr.shape)

        for y in range(scorr.shape[0]):
            for x in range(scorr.shape[1]):
                dx = x-maxx
                dy = y-maxy
                distmat[y,x] = math.sqrt(dx**2+dy**2)

        # the wavelength is defined as twice the distance between the
        # maximum and the minimum!                                   

        # wavelength in pixels:                   
        dx = maxx-minx
        dy = maxy-miny
        wavelength_pix=2*math.sqrt(dx**2+dy**2)

        # plot the correlation profile along the line (x0,y0) -- (x1,y1) 
        x0,y0 = maxx-(4*dx),maxy-(4*dy)
        x1,y1 = maxx+(4*dx),maxy+(4*dy)

        # note that:
        # sqrt( (x1-x0)^2 + (y1-y0)^2 ) = 4 * wavelength

        # the line needs to be restricted by the size of scorr (nrows, ncols) 
        # (in the case of long wavelengths or small images)  
        if (x0 > x1):
            if (x0 > ncols-1):
                x0 = ncols-1
            if (x1 < 0):
                x1 = 0
        else:
            if (x0 < 0):
                x0 = 0
            if (x1 > ncols-1):
                x1 = ncols-1

        if (y0 > y1):
            if (y0 > nrows-1):
                y0 = nrows-1
            if (y1 < 0):
                y1 = 0
        else:
            if (y0 < 0):
                y0 = 0
            if (y1 > nrows-1):
                y1 = nrows-1

        # ----------------- plot scorr with profile line --------------------

        fac = 0.001*pixsize
        ax.plot([x0*fac-xmax, x1*fac-xmax], [y0*fac+ymax, y1*fac+ymax], color="orange", linewidth=1)
        
        fig.tight_layout()
        can.draw()
        can.get_tk_widget().pack()
        can._tkcanvas.pack()

        # --------------------------------------------------------------------
        print('wavelength in pixels: ',wavelength_pix)

        # get profile
        num = 1000
        print('x0,x1,y0,y1',x0,x1,y0,y1)
        x, y = numpy.linspace(x0, x1, num), numpy.linspace(y0, y1, num)
        scorr_profile = scorr[y.astype(numpy.int), x.astype(numpy.int)]
        distmat_profile= distmat[y.astype(numpy.int), x.astype(numpy.int)]

        # note that the spacing corresponds now to 4*wavelength/num

        # distmat_profile determines the x-axis in the profile plot 
        # half of all values need to be negative
        dm = numpy.argmin(distmat_profile) # dm = location of correlation max.  

        distmat_profile[0:dm+1] = -distmat_profile[0:dm+1]

        # smooth profile
        # scorr_profile = smooth.running_average(scorr_profile,70)
        # distmat_profile = smooth.running_average(distmat_profile,70)

        fig = Figure(figsize=(6,5), dpi=100)
        fig.subplots_adjust(left=0.15,bottom=0.15)
        ax = fig.add_subplot(111)

        self.profileframe = Frame(tkparent2)
        self.profileframe.pack(expand=1,fill=BOTH)

        can = FigureCanvasTkAgg(fig, self.profileframe)

        ax.axes.tick_params(labelsize=14)

        # convert to microns: 
        distmat_profile = distmat_profile * pixsize * 0.001
        wavelength = wavelength_pix * pixsize * 0.001

        ax.plot([distmat_profile[0],distmat_profile[-1]],[0,0], color='black',linewidth=2.0)
 

        ax.plot(distmat_profile,scorr_profile,linewidth=3,color='darkorange')
        ax.set_ylim([-0.6,1.05])
        ax.axvline(x=0.5*wavelength,ymin=-0.55,ymax=0.95,linestyle='dashed',color='0.5')
        ax.axvline(x=-0.5*wavelength,ymin=-0.55,ymax=0.95,linestyle='dashed',color='0.5')

        # print the wavelength 'lambda' 
        str1 = "$\lambda$ = "
        str2 = "$%.1f$" %wavelength
        str3 = " $\mu$m"
        xpos = 0.7*wavelength
        ypos = 0.9
        ax.text(xpos,ypos,str1+str2+str3,fontsize=14)

        #ax.set_title('Mean Spatial Autocorrelation') 
        #divider = make_axes_locatable(ax)
        #cax = divider.append_axes("right", size="5%", pad=0.05)
        #fig.colorbar(la1,cax=cax)  

        ax.set_xlabel("Displacement [$\mu$m]",fontsize=16)
        ax.set_ylabel("Correlation",fontsize=16)

        # draw also the absolute value of the correlation profile
        # as well as its envelope, which we use to determine 
        # the spatial correlation length 
        scorr_profile = numpy.absolute(scorr_profile)
        #ax.plot(distmat_profile,scorr_profile,linewidth=1,color='orange',linestyle='dashed')

        # the autocorrelation length (\xi) is determined as the de-correlation
        # of the exponential fit to the 'envelope' exp(-2)
        # the exponential is fitted to 3 points (the two minima & the maximum)
        # seems oversimplified, but represents a robust measure for the 
        # de-correlation length  

        # fx and fy determine the x and y values to determine the exponential fit
        # note that distmat_profile has been interpolated 
        # (with 'num' points - see above). Therefore, the assignment of the 
        # indices in the interpolated profile is tricky 

        # the whole distmat_profile len(distmat_profile)=num represents 
        # four wavelengths!
        wavelength_interp = num / 4.0

        inds = list(range(7))
        for i in range(7):
            inds[i] = int(dm-(1.5*wavelength_interp+(i*0.5*wavelength_interp)))

        fx = distmat_profile[inds]
        fy = scorr_profile[inds]
        pars,cov = curve_fit(f=exponential,xdata=fx, ydata=fy,p0=[1.0,0.5*wavelength_interp],bounds=(-numpy.inf, numpy.inf),sigma=[1.0,1.0,1.0,1.0,1.0,1.0,1.0])

        # print('pars ',pars)
        a,b = pars[0], pars[1]
        # print(distmat_profile.size)
        gf = numpy.zeros(1000)
        for i in range(1000):
            gf[i] = exponential(distmat_profile[i],a,b)

        #ax.plot(distmat_profile,gf,color='darkorange')
        # acorrlength measures distance after which correlation amounts to exp(-4)
        acorrlength=3*abs(b)

        #str1=r'$\xi_{exp}$'
        #str2=" = $%.1f$" %acorrlength
        #str3=" $\mu$m"
        #ax.text(0.7*wavelength,0.8,str1+str2+str3,fontsize=14,color='darkorange')

        # some correlation profiles are not well approximated by 
        # an exponential fit -> therefore, a second spatial correlation length
        # 'xi' is determined as follows:
        # search the greatest index k, for which: abs(scorr_profile[k]) <= exp(-4)
        # and determine the distance to the correlation maximum 
        # this represents a more robust alternative for the spatial corr length  

        # search index k: 
        k=0
        while ( scorr_profile[k] <= math.exp(-3) ):
            k=k+1
        # determine distance to correlation maximum (in real units) 
        xi = abs(dm - k) * 4 * wavelength / num
        # print xi on plot:
        str1=r'$\xi$'
        str2=" = $%.1f$" %xi
        str3=" $\mu$m"
        ax.text(0.7*wavelength,0.75,str1+str2+str3,fontsize=14,color='darkorange')


        ax.margins(0.01)
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











