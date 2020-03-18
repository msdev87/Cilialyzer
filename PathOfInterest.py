from PIL import ImageTk
import os
import time 
if os.sys.version_info.major > 2:
    from tkinter import *
else:
    from Tkinter import * 

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import scipy 
from scipy import ndimage 
from scipy import signal 
def poly(x, coeffs):
    a = coeffs[0]
    b = coeffs[1] 
    c = coeffs[2] 
    d = coeffs[3]
    e = coeffs[4]
    f = coeffs[5] 
    y = np.zeros(len(x)) 
    for i in range(len(x)):
        y[i] = a*x[i]**5 +b*x[i]**4+c*x[i]**3+d*x[i]**2+e*x[i]+f 
    return y 


class POI:

    # POI : Path of interest

    def __init__(self):
        self.poi = () # holds the line i.e. the coordinates (xi,yi) 
        self.item = None 
        self.anchor = None 
        self.poix = None 
        self.poiy = None 
        self.poiseq = [] # contains the intensities along the line as a func of time I(loc,t)   
        self.filtseq = None 


    def GetPOI(self, roi):

        # mouse event bindings 
        def path_on_mouse_down(event): 
            if (len(self.poi) < 4):
                self.poi = (event.widget.canvasx(event.x), event.widget.canvasy(event.y))
                  
        def path_on_mouse_drag(event): 
            self.poi = self.poi + (event.widget.canvasx(event.x), event.widget.canvasy(event.y))
            if self.item is None:
                self.item = event.widget.create_line(self.poi,width=5,smooth=True)
            else:
                event.widget.coords(self.item, *self.poi)

        def path_on_mouse_up(event):
            # mouse release event  
            time.sleep(1)
            l = len(self.poi) 
            #print "length of self.poi"
            #print l 
               
            self.poix = np.zeros(l/2)
            self.poiy = np.zeros(l/2)
            for i in range(l/2): 
                self.poix[i] = self.poi[2*i]
                self.poiy[i] = self.poi[2*i+1]
            #print self.poi

            # fit a polynomial to the selected path!  
            #coeff = np.polyfit(self.poix, self.poiy,4)  

            #print self.poix 

            #fitfunc = np.polyval(coeff, self.poix)  
            #plt.plot(self.poix, self.poiy,'.',self.poix, fitfunc)   
            #plt.show() 
            time.sleep(0.5) 
            poi_win.destroy()


        #def path_on_enter(event):
        #    # enter, after path of interest has been drawn! 
                
        #    #print poi_coords 
        #    self.item = event.widget.create_line(self.poi,smooth=True,width=5)
        #    print "ITEM"
        #    print self.item 
        #    print type(self.item) 
        #    #print poi_coords
        #    event.widget.coords(self.item, *self.poi)

        #    time.sleep(3)
        #    poi_win.destroy()

        self.item = None 
        self.anchor = None 
        self.poix = None 
        self.poiy = None 
        self.poiseq = [] # contains the intensities along the line as a func of time I(loc,t)   
        self.filtseq = None 
        self.poi = ()

        # the POI shall be drawn on the first image of the cropped ROI sequence  
        roiseq = roi.sequence # actually not the cropped roi sequence  

        # plot first image! 
        fimg = roiseq[0]
        w,h = fimg.size

        # show first image of sequence
        first_photo = ImageTk.PhotoImage(fimg)
        poi_win = Toplevel() # canvas shall be placed into poi_win
        frame = Frame(poi_win)
        frame.pack(fill=BOTH)
        poi_can = Canvas(frame,width=w,height=h)
        poi_can.pack(fill=BOTH)

        poi_can.xview_moveto(0)
        poi_can.yview_moveto(0)

        poi_can.create_image(0,0,image=first_photo,anchor='nw') # draw first_photo on canvas 
        poi_can.img = first_photo

        anchor = False

        poi_can.bind('<ButtonPress-1>', path_on_mouse_down)
        poi_can.bind('<B1-Motion>', path_on_mouse_drag)
        poi_can.bind('<ButtonRelease-1>', path_on_mouse_up)
        #poi_can.bind('<Double-Button-1>',path_on_enter)

        
    def dynfilter(self,powerspec,imgseq):

        pathx = self.poix
        pathy = self.poiy 
        pathl = len(pathx) 

        nimgs = imgseq.seqlength
        firstimg = imgseq.sequence[0]
        width, height = firstimg.size

        # convert roi-sequence (PIL images) to numpy array: 
        array = np.zeros((nimgs,height, width),dtype=int)

        for i in range(nimgs):
            array[i,:,:] = np.array(imgseq.sequence[i],dtype=int)

        # poiseq: path of interest over time    
        # poiseq: contains the intensities along the selected line over time
        poiseq = np.zeros((nimgs, pathl), dtype=float)
        for t in range(nimgs):
            for i in range(pathl): 
                poiseq[t,i] = float(array[t,int(pathy[i]),int(pathx[i])]) 
                
        self.poiseq = poiseq 
  
        # self.poiseq contains I(t,x) 
        poifft = np.fft.fftn(poiseq)

        # apply the CBF-band pass 
        top = powerspec.cbfhighind
        bot = powerspec.cbflowind 
        
        poifft[0:bot-1,:] = 0.0
        poifft[top+1:-1,:] = 0.0  

        # filtered poi sequecence: self.filtered  
        self.filtseq = np.real(np.fft.ifftn(poifft))  
        #print "test"
        #print self.filtseq[0,0] 
    
        # normalize the filtered sequence (0..1) 
        maxi = float(np.amax(self.filtseq))
        mini = np.amin(self.filtseq) 

        avg = np.mean(self.filtseq) 

        #print "maxi"
        #print maxi 
        #print "mini" 
        #print mini 

        #print self.filtseq 

        #self.filtseq = self.filtseq + 100.0 
        #for i in range(len(self.filtseq[:,0])):
            #for j in range(len(self.filtseq[0,:])):
                #hm = 1.0 * self.filtseq[i,j]
                #self.filtseq[i,j] = (hm - mini)/(maxi-mini)


    def animatePOI(self,imgseq): 


        print "type of self.poiseq" 
        print type(self.poiseq) 

        roiseq = imgseq.sequence

        pathx = self.poix
        pathy = self.poiy
         
        pathl = len(pathx) 

        nimgs = len(roiseq)
        firstimg = roiseq[0]
        width, height = firstimg.size

        # convert roi-sequence (PIL images) to numpy array: 
        array = np.zeros((nimgs,height, width),dtype=int)

        for i in range(nimgs):
            array[i,:,:] = np.array(roiseq[i],dtype=int)

        if (len(self.poiseq) == 0):
            print "TEST" 
            # poiseq: path of interest over time    
            # poiseq: contains the intensities along the selected line over time
            poiseq = np.zeros((nimgs, pathl), dtype=int)
            for t in range(nimgs):
                for i in range(pathl):
                    #print "t:", t
                    #print "pathx[i]:", pathx[i]
                    poiseq[t,i] = array[t,int(pathy[i]),int(pathx[i])] 
            
            self.poiseq = poiseq 
        else:
            # show filtered sequence 
            poiseq = self.filtseq
            print "poiseq set to filtered" 



        plt.ion()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        #ax.set_ylim(0,1)
        x = np.linspace(0, pathl-1, pathl)
        y = poiseq[0,:] 
        line, = ax.plot(x, y, 'r-')
        
        
        for t in range(nimgs):
            line.set_ydata(poiseq[t,:])
            #print poiseq[t,:]
            fig.canvas.draw() 
            fig.canvas.flush_events() 


    def ThickenPOI(self):

        # algorithm to ticken the selected path! 

        rangex = max(self.poix) - min(self.poix) 
        rangey = max(self.poiy) - min(self.poiy) 


        vx = 0  
        if (rangex > rangey):
            vx = 1 # more variability along x-direction  
        else: 
            vx = 0 # more variability along y 


        thickness = 2 
        
        thick_poix = np.zeros(len(self.poix),thickness) 
        thick_poiy = np.zeros(len(self.poiy),thickness) 
        
        thick_poix[:,0] = self.poix 
        thick_poiy[:,0] = self.poiy 


        for t in range(thickness-1):
 
            if (vx):
                startx = self.poix
                starty = self.poiy + t 
 
                # search next point :
                # 1. next point adjacent to previous 
                # 2. adjacent to previous path 
                 

    def GetSpatialAcorr(self,pixsize): 

        # calculate the mean spatial autocorrelogram 
        # (mean over all times) 
        # self.filtseq contains the dynamic filtered poi sequence (time,location)  

        nimgs = len(self.filtseq[:,0])  
        npix = len(self.filtseq[0,:])

        acorr = np.zeros(2*npix) 

        for t in range(nimgs):

            # calc autocorr for each poi at each time step
            vec = np.squeeze(self.filtseq[t,:])

            # zero-padding 'vec' 
            zs = np.zeros(len(vec),dtype=float) 
            vec = np.concatenate((vec,zs))  
                        
            fft = np.fft.fft(vec)
            # note the normalization by the length of the vector!! 
            # this normalization comes from the definition of the fourier transform in numpy!!
            # pitfall! 
            prod = np.multiply(fft,np.conjugate(fft)) / float(len(vec)) 
            ifft = np.real(np.fft.ifft(prod))
    
            #meansq = (np.mean(vec[0:npix-1]))**2  
            #stdv = np.std(vec[0:npix-1])
            meansq = (np.mean(vec))**2  
            stdv = np.std(vec)
        

            #acorr = np.add(acorr,np.absolute((np.subtract(ifft,meansq))/(stdv**2))) 
            acorr = np.add(acorr,ifft/(stdv**2)) 
            
        l = len(acorr)

      
        # mean acorr 
        acorr = acorr / float(nimgs)
        acorr = acorr[0:l/2]        
        l = len(acorr)

        # hilbert
        if (np.amin(acorr) < 0): 
            h = np.abs(signal.hilbert(acorr)) 
        else:
            h = acorr


        
        fig = plt.figure()
        fig = plt.figure(figsize=(6,4), dpi=80)
        ax = fig.add_subplot(111)
        x = np.zeros(l) 
        for i in range(l):
            x[i] = i * pixsize / 1000.0
        
      
        cutoff = int(3*l/4)
        plt.plot(x[0:cutoff],acorr[0:cutoff],color='0.2',lw=2)

        plt.ylabel('Correlation',labelpad=15,fontsize=14)
        plt.xlabel(r'Displacement [$\mu$m]',labelpad=8,fontsize=14)


        if (np.amin(acorr) < 0): 
            plt.plot(x[0:cutoff],h[0:cutoff],color='darkorange')

            for i in range(len(h)): 
                if (h[i] < 0.37):
                    corrl = x[i-1] 
                    break 
        else:
            for i in range(len(h)):
                if (acorr[i] < 0.37):
                    corrl = x[i-1]
                    break 
        
        xpos = 0.4 * x[-1]
        ypos = 0.7 

        plt.text(xpos,ypos,r'$\chi \approx %.1f$ [$\mu$m]'%corrl,fontsize=14)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        plt.tight_layout()
        plt.gca().set_ylim(top=1.0) 
        plt.savefig('spatialacorr.png', bbox_inches = 'tight')
        plt.close(fig)


 
    def GetTempAcorr(self,FPS): 

        deltat = 1.0 / FPS 

        # calculate the mean temporal autocorrelogram  
        nimgs = len(self.filtseq[:,0])  
        npix = len(self.filtseq[0,:])

        acorr = np.zeros(2*nimgs) 

        for x in range(npix):

            # calc autocorr for each poi at each time step
            vec = np.squeeze(self.filtseq[:,x])

            # zero-padding 'vec' 
            zs = np.zeros(len(vec),dtype=float) 
            vec = np.concatenate((vec,zs))  
                        
            fft = np.fft.fft(vec)
            prod = np.multiply(fft,np.conjugate(fft)) / float(len(vec)) 
            ifft = np.real(np.fft.ifft(prod))
    
            meansq = (np.mean(vec))**2  
            stdv = np.std(vec)
        
            #acorr = np.add(acorr,np.absolute((np.subtract(ifft,meansq))/(stdv**2))) 
            acorr = np.add(acorr,ifft/(stdv**2))  
        
        # mean acorr 
        acorr = acorr / float(npix)
          
        acorr = acorr[0:len(acorr)/2]
        l = len(acorr) 


        cutoff = int(3*l/4) 

        # plot acorr:  
        fig = plt.figure(figsize=(6,4), dpi=80)
        ax = fig.add_subplot(111)
        
        x = np.zeros(l)  
        
        for i in range(l):
            x[i] = i * deltat * 1000.0 
        
        plt.plot(x[0:cutoff],acorr[0:cutoff],color='0.2',lw=2)



        # add hilbert transform to the acorr (to calc. the corr. length)  
        h = np.abs(signal.hilbert(acorr))  
        h = h
        plt.plot(x[0:cutoff], h[0:cutoff], color='darkorange', lw=1)

        # decrease to 1/e = corr. length:
        for i in range(l):
            if (h[i] < 0.37):
                corrl = x[i-1]
                break 
         

        xpos = 0.4 * x[-1]
        ypos = 0.7 

        
        plt.text(xpos,ypos,r'$\tau \approx %.1f$ [ms]'%corrl,fontsize=14)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        plt.tight_layout()
       
        plt.gca().set_ylim(top=1.0)
        plt.ylabel('Correlation',labelpad=15,fontsize=14)
        plt.xlabel(r'Delay [ms]',labelpad=8,fontsize=14)

        plt.savefig('tempacorr.png', bbox_inches = 'tight')
        plt.close(fig)
















       

    def GetSpatioTempAcorr(self): 

        # calculate the mean spatio-temporal autocorrelogram  
        # self.filtseq contains the dynamic filtered poi sequence (time,location)  

        nimgs = len(self.filtseq[:,0])  
        npix = len(self.filtseq[0,:])

        acorr = np.zeros(2*npix) 


        for t in range(nimgs):

            # calc autocorr for each poi at each time step
            vec = np.squeeze(self.filtseq[t,:])

            # zero-padding 'vec' 
            zs = np.zeros(len(vec),dtype=float) 
            vec = np.concatenate((vec,zs))  
            
            
            fft = np.fft.fft(vec)
            prod = np.multiply(fft,np.conjugate(fft)) / float(len(vec)) 
            ifft = np.real(np.fft.ifft(prod))
    
            meansq = (np.mean(vec))**2  
            stdv = np.std(vec)
        
            acorr = np.add(acorr,np.absolute((np.subtract(ifft,meansq))/(stdv**2))) 
            
         
            

        # mean acorr 
        acorr = acorr / float(nimgs)
           

        # plot acorr:  
        fig = plt.figure(figsize=(6,4), dpi=80)
        ax = fig.add_subplot(111)
        l = len(acorr) 
        x = np.linspace(0, l/2-1, l)
        y = acorr[0:l/2]  
        line, = ax.plot(x[0:cutoff], y[0:cutoff], 'r-')
        fig.canvas.draw()
        plt.show()  
        


    def kspec(self, FPS, pixsize):

        nimgs = len(self.filtseq[:,0])  
        npix = len(self.filtseq[0,:])

        # 2D Fourier transform 
        ft = np.fft.fft2(self.filtseq) 
        r = len(self.filtseq[nimgs/2+1:,0])

        kspec = np.zeros(npix,dtype=float) 
        sqsum = 0.0
        for i in range(r):
            # sum over the NEGATIVE frequency domain! 
            f = i + (nimgs/2+1) 
            kspec = np.add(kspec,np.square(np.absolute(ft[f,:])))            

        kspec[0] = 0.0 
        kspec = kspec / np.sum(kspec) 



        # plot the k-spectrum! 
        fig = plt.figure(figsize=(6,4), dpi=80)
 
        ax = fig.add_subplot(111)
        l = len(kspec)
        x = np.zeros(npix)
        for i in range(npix): 
            x[i] = - ((npix/2)/(npix*pixsize)) + i* (1.0 / (npix*pixsize))     
         
    
        # until here x is in nm^-1 units -> convert to mu^-1:
        x = x * 1000.0

        y = np.roll(kspec,npix/2)  
        line, = ax.plot(x, y, 'r-')
        
        #plt.text(xpos,ypos,r'$\tau \approx %.1f$ [ms]'%corrl,fontsize=14)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        plt.tight_layout()
       
        #plt.gca().set_ylim(top=1.0)
        plt.ylabel('Relative Power Spectral Density',labelpad=15,fontsize=14)
        plt.xlabel(r'Spatial Frequency [$\mu$m$^{-1}$]',labelpad=8,fontsize=14)

        #plt.savefig('tempacorr.png', bbox_inches = 'tight')
        #plt.close(fig) 

        fig.canvas.draw()
        plt.show()  
        


         














