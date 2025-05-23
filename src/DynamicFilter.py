import numpy
import PIL
from math_utils.bytescl import bytescl
import sys
import math
import os
from math_utils import autocorrelation_zeropadding
import temporal_autocorrelation2D
from scipy.ndimage import gaussian_filter
import re
if os.sys.version_info.major > 2:
    from tkinter import *
else:
    from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
#numpy.set_printoptions(threshold=sys.maxsize)
from scipy.optimize import curve_fit
import cv2
class DynFilter:

    def __init__(self):

        self.dyn_roiseq = []
        self.corr_roiseq = []
        self.tkframe = None
        self.profileframe = None
        self.corrplotframe = None
        self.kxkyplotax = None
        self.kxkyrows = None
        self.kxkycols = None
        self.kxky = None
        self.splitline = None
        self.pixelffts = []
        self.fps = None
        self.wavelength = None
        self.sclength = None # spatial correlation length
        self.cbp_elongation = None
        self.bidirectional_corrlength = None



        """
        # multiprocessing 
        multiprocessing.freeze_support()
        self.ncpus = multiprocessing.cpu_count()
        if (self.ncpus > 1):
            self.pool = multiprocessing.Pool(self.ncpus-1)
        else:
            self.pool = multiprocessing.Pool(self.ncpus)
        """

    def bandpass(self, PILseq, fps, minf, maxf):

        # input: roiseq 
        # output: dynamically filtered roiseq
        # dynamic filtering: bandpass -> keep frequencies f : minf <= f <= maxf 

        self.fps = fps

        firstimg = PILseq[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        nimgs = len(PILseq) # number of images  

        # create numpy array 'array' 
        array = numpy.zeros((int(nimgs), int(height), int(width)),
                            dtype=numpy.float32)
        for i in range(nimgs):
            array[i,:,:] = numpy.array(PILseq[i])
        (nt,ni,nj) = numpy.shape(array)

        # determine the frequency band(s) to be filtered (consdier nrharms)
        # remove frequency if not contained in any band

        filt = numpy.zeros(nt)

        # ---------- get indices of 'cbf band' -> keep fundamental freq --------
        # we also have to filter in the negative frequency domain!
        # Note that minf1 and maxf1 are frequency indices (not in real units)
        minf1 = int(round((float(nimgs)*minf/float(fps))-1))
        maxf1 = int(round((float(nimgs)*maxf/float(fps))-1))

        # Note that we bandpass filter in the following
        # The frequency band we keep is given by the min. frequency,
        # (i.e. the left slider), the max. frequency is given by 7 x max. freq.
        # OR the highest frequency possible
        if (7*maxf1 < int(len(filt)/2)-1):
            # keep positive frequencies
            filt[minf1:7*maxf1] = 1.0
            # get corresponding negative frequencies:
            filt[-7*maxf1:-minf1+1] = 1.0
        else:
            # keep positive freqs from minf1
            filt[minf1:int(len(filt)/2)] = 1.0
            #keep negative freqs from -minf1
            filt[-int(len(filt)/2)-1:-minf1+1] = 1.0

        # ------------------ keep second harmonic freq band --------------------
        """
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
        """
        #numpy.set_printoptions(threshold=sys.maxsize)
        #print(filt)

        # dynamic filtering for each pixel separately! (in time domain)   

        # loop over pixels (spatial domain)
        # apply bandpass (along time axis!) for pixel after pixel
        for i in range(ni):
            for j in range(nj):
                array[:,i,j] = numpy.real(numpy.fft.ifft(numpy.multiply(
                    numpy.fft.fft(array[:, i, j], axis=0), filt), axis=0))
        array = bytescl(array)

        self.dyn_roiseq.clear()
        self.dyn_roiseq = []

        # create PIL sequence from numpy array!
        for i in range(nimgs):
            self.dyn_roiseq.append(PIL.Image.fromarray(numpy.uint8(array[i,:,:])))

    """
    def temporal_autocorrelation(self, tkplotframe, frequencymap):

            #computes the mean temporal autocorrelation function
            #from which we determine the autocorrelation time

            firstimg = self.dyn_roiseq[0]  # first image of dyn roi sequence
            width, height = firstimg.size  # dimension of images
            nimgs = len(self.dyn_roiseq)   # number of images

            # create numpy array from self.dyn_roiseq,
            # which holds the list of dynamically filtered PIL images
            array = numpy.zeros((int(nimgs), int(height), int(width)))

            (nt, ni, nj) = numpy.shape(array)
            for t in range(nt):
                array[t, :, :] = numpy.array(self.dyn_roiseq[t])

            # determine the temporal autocorrelation function for each pixel,
            # calculate the average and plot the average temp. autocorrelation
            self.meantacorr = numpy.zeros(int(nt/2))

            # 'time' holds the elapsed time in real units
            time = numpy.zeros(int(nt/2))
            time = numpy.divide(numpy.array(range(int(nt/2))),float(self.fps))

            # array[t,i,j] needs to be split up for the multiprocessing
            # splitting is done along dimension j:
            subarrays = []

            jend = len(array[0,0,:]) # number of elements along j
            jsub = int(jend / (self.ncpus-1)) # we will start self.ncpus-1 processes

            mask = ~numpy.isnan(frequencymap)
            # print(mask)

            # create list of subarrays
            for i in range(self.ncpus-1):

                if (i < self.ncpus-2):
                    array_slice = array[:,:,i*jsub:(i+1)*jsub]
                else:
                        array_slice = array[:,:,i*jsub:]

                # append tuple: slice & mask 
                subarrays.append((array_slice, mask))

            # get the average autocorrelation for each array-slice   
            meanacorrs = self.pool.map(temporal_autocorrelation2D.avg_tacorr,
                          [subarrays[i] for i in range(len(subarrays))])

            # get average:
            for i in range(len(subarrays)):
                self.meantacorr = self.meantacorr + meanacorrs[i]

            self.meantacorr = (1.0 / float(self.ncpus-1)) * self.meantacorr

            # plot the average temporal autocorrelation function
            fig = plt.figure(figsize=(7, 5), dpi=100)
            ax = fig.add_subplot(111)

            can = FigureCanvasTkAgg(fig, tkplotframe)

            ax.axes.tick_params(labelsize=14)
            ax.plot(time, self.meantacorr, color='orange', linewidth=2.0)

            ax.margins(0.05)
            can.draw()
            can.get_tk_widget().pack()
            can._tkcanvas.pack()

            ax.set_ylim([-0.6, 1.05])
            ax.set_xlim([0, 1.4])

            # print(numpy.absolute(self.meantacorr))

            # determine the correation time tau: 
            tau = 1
            while (numpy.absolute(self.meantacorr[-tau]) < math.exp(-2)):
                tau = tau + 1

            tau = nt/2 - tau

            #print('***********************')
            # print('tau: ', tau)

            # tau in real units: 
            tau = tau / float(self.fps) * 1000.0

            ax.axvline(x=tau/1000.0, ymin=-0.3, ymax=0.8, linestyle='dashed', color='0.5')

            str1 = r'$\tau$ = '
            str2 = "$%.0f$" % tau
            str3 = " ms"
            xpos = 0.5
            ypos = 0.9
            ax.text(xpos, ypos, str1 + str2 + str3, fontsize=14)

            ax.set_xlabel(r"Time delay $\Delta$t [ms]", fontsize=16)
            ax.set_ylabel("Temporal autocorrelation", fontsize=16)

    """

    def spatiotempcorr(self, fps, minf, maxf):

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
            #print("max scorr ", numpy.amax(scorr), " min scorr ", numpy.amin(scorr)) 

            scorr = scorr + 1 # no negative values
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

    def mscorr(self, fps, minf, maxf, colormapframe, profileframe, pixsize, validity_mask, automated=0, output_fname=''):
        """
        This function calculates the wavelength based on the average spatial
        autocorrelation
        """
        print(' ----- starting mscorr ----- ')

        def exponential(x,a,b):
            return a*numpy.exp(-abs(x/b))

        nimgs = len(self.dyn_roiseq)
        firstimg = self.dyn_roiseq[0]
        width, height = firstimg.size

        # corr: spatial correlogram 
        corr = numpy.zeros((height,width))
        scorr = numpy.zeros((height,width)) # sum (over time) of spatial acorrs 

        # as the spatial autocorrelation hardly varies over time
        # -> the average over 300 images is a good approximation
        if (nimgs > 300): nimgs = 300

        print('next: loop over frames to calculate autocorrelation of each frame')

        for t in range(nimgs): # loop over time
            # images are slightly smoothed
            img = gaussian_filter( numpy.array(self.dyn_roiseq[t], dtype=numpy.float32),
                sigma=1.0, truncate=2.0)
            # autocorrelate
            corr = autocorrelation_zeropadding.acorr2D_zp(img, mask=validity_mask)
            scorr = numpy.add(scorr,corr)

        scorr = scorr / float(nimgs)
        # get rid of extra dimensions
        scorr = numpy.squeeze(scorr)

        print('mean spatial autocorrelation done')
        # 'scorr' holds now the two-dimensional mean spatial autocorrelation   
        # based on which we determine the metachronal wavelength 
        # according to Ryser et al. 2007 

        # the metachronal wavelength is characterized by the distance between 
        # the two minima in the mean spatial autocorrelation

        # plot the mean spatial autocorrelation 
        # together with the line connecting the two correlation minima   

        nrows = len(scorr[:,0]) # number of rows
        ncols = len(scorr[0,:]) # number of columns

        fig = Figure(figsize=(5,5))
        ax = fig.add_subplot(111)

        can = FigureCanvasTkAgg(fig, colormapframe)

        ny = len(scorr[:,0])
        nx = len(scorr[0,:])

        corrplot = numpy.zeros((ny,nx))
        corrplot[:,:] = numpy.nan

        corrplot = scorr

        vmax = numpy.max(corrplot)
        xend = 0.5*nx*pixsize/1000.0
        yend = 0.5*ny*pixsize/1000.0

        # Plot the two-dim average spatial autocorrelation
        la1 = ax.imshow(corrplot,alpha=1.0, cmap='bwr', interpolation='none',\
            extent=[-xend,xend,-yend,yend], vmin=-0.8*vmax, vmax=0.8*vmax)

        ax.set_xlabel(r"$\Delta$x [$\mu$m]",fontsize=17)
        ax.set_ylabel(r"$\Delta$y [$\mu$m]",fontsize=17)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar=fig.colorbar(la1,cax=cax)
        cbar.ax.tick_params(labelsize=15)
        ax.axes.tick_params(labelsize=15)

        ######################################################################
        # plot the profile of the correlogram along the line 
        # connecting the two minima (and the global maximum)

        # get the location of the extrema in scorr (in pixel coordinates)
        # (if multiple extrema argmax/argmin provides index of first occurence) 
        maxy, maxx = numpy.unravel_index(numpy.argmax(scorr,axis=None),scorr.shape)
        miny, minx = numpy.unravel_index(numpy.argmin(scorr,axis=None),scorr.shape)

        # slightly smooth scorr:
        scorr = gaussian_filter(scorr, sigma=1.0, truncate=2.0)

        # calculate the 'bidirectional spatial correlation length'
        # this will provide a measure which is similar to the frequency correlation length

        threshold = 1.0 / math.e
        # the center indices are given by the maximum correlation value
        max_row, max_col = numpy.unravel_index(numpy.argmax(scorr, axis=None), scorr.shape)
        center_indices = [[max_row, max_col]]
        new_neighbors = [[max_row, max_col]]
        relative_neighbors = [[-1,0], [0,-1], [1,0], [0,1]]
        visited = set()
        while new_neighbors:
            current_neighbors = new_neighbors.copy()
            new_neighbors = []  # Reset for next iteration
            for r, c in current_neighbors:
                for dr, dc in relative_neighbors:
                    row_ind, col_ind = r + dr, c + dc
                    # Check bounds and if already visited
                    if (0 <= row_ind < scorr.shape[0] and 0 <= col_ind < scorr.shape[1] and
                        (row_ind, col_ind) not in visited and scorr[row_ind, col_ind] > threshold):
                        # Add new neighbor to lists
                        center_indices.append([row_ind, col_ind])
                        new_neighbors.append([row_ind, col_ind])
                        visited.add((row_ind, col_ind))  # Mark as visited
        area = len(center_indices)
        self.bidirectional_corrlength = math.sqrt(area) * pixsize / 1000.0

        print('self.bicorr', self.bidirectional_corrlength)

        #print(' ellipse gets fitted next')
        # ---------------------------------------------------------------------
        # fit ellipse to all values > 1/e
        ellipse_array = numpy.zeros_like(scorr)
        inds = numpy.argwhere(scorr > 1/math.e)
        if len(inds) > 7:
            rows = inds[:,0]
            cols = inds[:,1]
            ellipse_array[rows, cols] = 1
            ellipse_indices = numpy.column_stack(numpy.where(ellipse_array > 0))
            ellipse = cv2.fitEllipse(ellipse_indices)
            (center_x, center_y), (semi_axis1, semi_axis2), rotation_angle = ellipse

            major_axis = max(semi_axis1, semi_axis2)
            minor_axis = min(semi_axis1, semi_axis2)

            self.cbp_elongation = major_axis / minor_axis
        else:
            self.cbp_elongation = numpy.nan

        print('ellipse-fitting done')

        #print('---------------------------------------------------------------')
        #print('major axis/mino axis: ', major_axis/minor_axis)
        #print('---------------------------------------------------------------')

        #----------------------------------------------------------------------

        """
        # ----------------------------------------------------------------------
        # to characterize the collective beat pattern:
        # fit the elliptic peak around the maximum
        # search all correlation values > 0 and fit an ellipse

        relative_neighbors = numpy.array([[0,-1], [-1,0],[0,0], [1,0], [0,1]])
        #neighbors = numpy.add(relative_neighbors, numpy.array([maxy, maxx]))
        neighbors = numpy.array([[maxy, maxx]]).reshape((1,2))
        ellipse_array = numpy.zeros_like(scorr)
        corr_threshold = 0.1 #1 / math_utils.e
        neighbors_rows = neighbors[:, 0]
        neighbors_cols = neighbors[:, 1]

        while (numpy.sum(scorr[neighbors_rows, neighbors_cols] > corr_threshold) > 0):
            cnt_max = neighbors.shape[0]
            # loop over all elements in neighbors
            for cnt in range(cnt_max):
                # loop over local neighborhood for all elements in neighbors
                for n in range(5):
                    print('neighbors: ', neighbors)
                    neighbor = neighbors[cnt,:] + relative_neighbors[n,:]
                    if ((scorr[neighbor[0],neighbor[1]] > corr_threshold) and (not ellipse_array[neighbor[0],neighbor[1]])):
                        ellipse_array[neighbor[0],neighbor[1]] = 1
                        neighbors_rows = numpy.array(
                            neighbors_rows.tolist().append(neighbor[0]))
                        neighbors_cols = numpy.array(
                            neighbors_cols.tolist().append(neighbor[1]))
                        neighbors = numpy.array(neighbors.tolist().append(neighbor))
                    else:
                        neighbors_rows = numpy.array(
                            neighbors_rows.tolist().remove(neighbor[0]))
                        neighbors_cols = numpy.array(
                            neighbors_cols.tolist().remove(neighbor[1]))
                        neighbors = numpy.array(
                            neighbors.tolist().remove(neighbor))

        plt.figure()
        plt.imshow(ellipse_array)
        plt.show()

        # lets fit the ellipse
        #ellipse_indices = np.column_stack(np.where(ellipse_array > 0))
        #ellipse = cv2.fitEllipse(ellipse_indices)
        #(center_x, center_y), (major_axis, minor_axis), rotation_angle = ellipse
        # ----------------------------------------------------------------------
        """

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

        # let us now refine the position of the minimum 
        # ---> search all pixels in a square environment around (minx, miny) 
        # with a value, which is negative and lower than 1/e*peakheight 

        square_arr = scorr[miny,minx] # square array around minimum position 
        minimum_value = scorr[miny,minx]
        threshold = 1.0 / math.exp(1) * minimum_value
        s=1
        print('before while')
        while (numpy.all(square_arr < threshold)):
            # repeat while all elements in square around min are > minimum val
            s = s+2 # increase size of square array (1x1, 3x3, 5x5, ...) 
            square_arr = scorr[miny-s:miny+s+1, minx-s:minx+s+1]
        print('after while')

        # positions within scorr
        x = numpy.linspace(-int(s/2),int(s/2),s) + minx
        y = numpy.linspace(-int(s/2),int(s/2),s) + miny
        xx, yy = numpy.meshgrid(x, y)

        # determine center of mass (cm) within square_arr

        x_cm, y_cm = 0.0, 0.0
        weight_total = 0.0 # sum of weights
        for i in range(s):
            for j in range(s):
                x = int(xx[i,j])
                y = int(yy[i,j])
                # print('x: ',x,' y: ',y)
                if (scorr[y,x] < 0):
                    x_cm = x_cm + abs(scorr[y,x]) * x
                    y_cm = y_cm + abs(scorr[y,x]) * y
                    weight_total += abs(scorr[y,x])

        try:
            x_cm = x_cm / weight_total
            y_cm = y_cm / weight_total
        except:
            x_cm = minx
            y_cm = miny


        # print('--------- test --------')
        # print('minx: ', minx)
        # print('miny: ',miny)
        # print('xcm: ',x_cm)
        #print('ycm:',y_cm)

        # x_cm and y_cm can now be defined as a more exact measure for the 
        # position of the minimum 
        minx = x_cm
        miny = y_cm

        # Wavelength in pixels:                   
        dx = maxx-minx
        dy = maxy-miny
        wavelength_pix = 2*math.sqrt(dx**2+dy**2)

        # Plot the correlation profile along the line (x0,y0) -- (x1,y1)


        q=2.0
        x0,y0 = maxx-(q*dx),maxy-(q*dy)
        x1,y1 = maxx+(q*dx),maxy+(q*dy)
        # make sure that the indices x0,y0,x1,y1 are valid:
        c1 = bool(0 < x0 < ncols-1)
        c2 = bool(0 < x1 < ncols - 1)
        c3 = bool(0 < y0 < nrows - 1)
        c4 = bool(0 < y1 < nrows - 1)

        print('before 2nd while')
        while not (c1 and c2 and c3 and c4 ):
            q = q - 0.1
            x0, y0 = maxx - (q * dx), maxy - (q * dy)
            x1, y1 = maxx + (q * dx), maxy + (q * dy)

            c1 = bool(0 < x0 < ncols - 1)
            c2 = bool(0 < x1 < ncols - 1)
            c3 = bool(0 < y0 < nrows - 1)
            c4 = bool(0 < y1 < nrows - 1)

        print('after 2nd while')
        # Note that:
        # sqrt( (x1-x0)^2 + (y1-y0)^2 ) = q * wavelength

        # generate a line of num points from (x0,y0) to (x1,y1)
        num = 1000  # number of interpolation points
        lx, ly = numpy.linspace(x0, x1, num), numpy.linspace(y0, y1, num)

        # the line needs to be restricted by the size of scorr (nrows, ncols)
        # (in the case of long wavelengths or small images)
        # Therefore, remove all elements in lx < 0, lx > nx-1, ly < 0, ly > ny-1
        indices1 = numpy.where(lx < 0)[0]
        indices2 = numpy.where(ly < 0)[0]
        indices3 = numpy.where(lx > nx-1)[0]
        indices4 = numpy.where(ly > ny-1)[0]

        rm_indices = numpy.concatenate((indices1,indices2,indices3,indices4))

        if rm_indices.size > 0:
            lx = numpy.delete(lx, rm_indices)
            ly = numpy.delete(ly, rm_indices)

        """
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
        """


        # ----------------- plot scorr with profile line --------------------

        fac = 0.001*pixsize
        # ax.plot((lx-maxx)*fac,(ly-maxy)*fac, color="orange", linewidth=1)

        #ax.plot(0, 0, marker='o', linestyle='None', color='blue', markersize=3)
        #ax.plot(dx*fac, -dy*fac, marker='o', linestyle='None', color='red', markersize=3)

        fig.tight_layout()
        can.draw()
        can.get_tk_widget().place(in_=colormapframe,relx=0.5, rely=0.5, anchor='center', width=600, height=500)
        can._tkcanvas.place(in_=colormapframe,relx=0.5, rely=0.5, anchor='center', width=600, height=500)

        # --------------------------------------------------------------------
        # print('wavelength in pixels: ',wavelength_pix)

        # get profile
        num = 1000 # number of interpolation points

        x, y = numpy.linspace(x0, x1, num), numpy.linspace(y0, y1, num)
        scorr_profile = scorr[y.round().astype(int), x.round().astype(int)]
        distmat_profile= distmat[y.round().astype(int), x.round().astype(int)]

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

        #self.profileframe = Frame(tkparent2)
        #self.profileframe.place(in_=tkparent2, relx=0.5, rely=0.5, anchor='center', width=500, height=500)

        can = FigureCanvasTkAgg(fig, profileframe)

        ax.axes.tick_params(labelsize=14)

        # convert to microns: 
        distmat_profile = distmat_profile * pixsize * 0.001
        wavelength = wavelength_pix * pixsize * 0.001

        ax.plot([distmat_profile[0],distmat_profile[-1]],[0,0], color='black',linewidth=2.0)

        l1 = len(distmat_profile)
        l2 = len(scorr_profile)
        ax.plot(distmat_profile, scorr_profile, linewidth=3, color='darkorange')
        ax.set_ylim([-0.6,1.05])
        ax.set_xlim([-100,100])
        ax.axvline(x=0.5*wavelength,ymin=-0.55,ymax=0.95,linestyle='dashed',color='0.5')
        ax.axvline(x=-0.5*wavelength,ymin=-0.55,ymax=0.95,linestyle='dashed',color='0.5')

        # print the wavelength 'lambda'

        self.wavelength = wavelength
        # print('*********** self.wavelength ************ ', self.wavelength )

        str1 = r"$\lambda$ = "
        str2 = "$%.1f$" %wavelength
        str3 = r" $\mu$m"
        xpos = 0.5*wavelength
        ypos = 0.8
        ax.text(xpos,ypos,str1+str2+str3,fontsize=14)

        ax.set_xlabel(r"Displacement [$\mu$m]", fontsize=16)
        ax.set_ylabel("Correlation", fontsize=16)

        # for the automated analysis pipeline, the minimum value
        # of scorr_profile gets returned (to check if this value is > -0.03)
        return_value = numpy.min(scorr_profile)

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

        self.sclength = xi
        # print xi on plot:
        str1=r'$\xi$'
        str2=" = $%.1f$" %xi
        str3=r" $\mu$m"
        ax.text(0.5*wavelength,0.65,str1+str2+str3,fontsize=14,color='darkorange')

        ax.margins(0.01)
        can.draw()
        can.get_tk_widget().place(in_=profileframe, relx=0.5, rely=0.5, anchor='center', width=600, height=500)
        can._tkcanvas.place(in_=profileframe, relx=0.5, rely=0.5, anchor='center', width=600, height=500)

        if automated:
            # save figure to disk
            #datetime_string = datetime.datetime.now().strftime(
            #    "%Y-%m-%d_%H-%M-%S")
            #output_directory = os.path.join(os.getcwd(),
            #    'Cilialyzer_output_' + datetime_string)
            f = open('config/output_directory.dat', 'r')
            output_directory = f.read()
            f.close()
            # try:
            #    os.mkdir(output_directory)
            #except FileExistsError:
            #    pass
            fname = re.sub(r'[^A-Za-z0-9 ]', "_", output_fname)
            fname = os.path.join(output_directory, fname + '_AUTOCORR_PROFILE.png')
            fig.savefig(fname, format='png', dpi=200)

        return return_value

#if __name__ == '__main__':
#    pass



    """
    def save_plot(self, dirname):
        f = open('output_directory.dat', 'r')
        output_directory = f.read()
        f.close()
        # special characters are replaced by an underline:
        fname = re.sub(r'[^A-Za-z0-9 ]', "_", dirname)
        fname = os.path.join(output_directory, fname + '_ACTIVITYMAP.png')
        self.fig.savefig(fname,format='png',dpi=200)
    """