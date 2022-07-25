from PIL import Image
import numpy
from numpy.fft import fftn
from numpy.fft import ifftn
import math
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit
import multiprocessing
import spacetimecorr_zp
import gaussian2Dfit
import windowed_wavelength


"""
class WinAnalysis:

    def __init__(self):

        # The windowed analysis is exclusively performed on the
        # dynamically filtered ROI sequence
        self.dyn_roiseq = [] # filtered ROI-sequence

        # The window size defines the size of the areas,
        # which we will examine separately
        self.total_windows = None # number of total windows
        self.windowsize = None # window size

        # we need the activity map to exclude areas (windows),
        # which show too much variability (e.g. in CBF)
        self.activitymap = []
"""

def analyse_windows(array_list):
    """
    Analyses the list of windows it receives
    """

    nrwins = len(array_list)

    peaks_list = []

    for i in range(nrwins):

        # 'array' holds a single 'window' with indices t,i,j
        array = array_list[i]

        #print('*************************************************************')
        #print(array)
        #print('*************************************************************')

        # compute sptio-temporal cross-correlogram for 'array' 
        stcorr = spacetimecorr_zp.stcorr(array)

        # peak tracking
        n_timeshifts = len(stcorr)
        peaks = numpy.zeros((n_timeshifts,3)) # holds position (x,y) & height of peak
        peaks[:,:] = numpy.nan

        for dt in range(n_timeshifts):

            # we fit only the middle part of the cross-correlogram 
            # i.e. the peak, which is characterized by the greatest values 
            # therefore, we select only those values, which are 
            # greater than 1/e from the cross-correlogram

            # print('--------------------------------------------------------')

            if ( numpy.max(numpy.subtract(stcorr[dt], 1./math.e)) > 0):

                # print('max1 in stcorr: ', numpy.max(stcorr[dt]))
                stcorr[dt] = numpy.subtract(stcorr[dt], 1./math.e)
                NaN_inds = numpy.where(stcorr[dt] < 0)
                stcorr[dt][NaN_inds] = 0. #float("NaN")

                #print('max2 in stcorr: ', numpy.max(stcorr[dt]))

                sigma = numpy.zeros_like(stcorr[dt]) # weights for Gaussian fit 
                inds = numpy.where(stcorr[dt] > 0)
                sigma[NaN_inds] = 1e7
                sigma[inds] = 1.

                # get position (x,y) and height of peak 
                posx, posy, peakh = gaussian2Dfit.fit(stcorr[dt], sigma)

                peaks[dt,0] = posx
                peaks[dt,1] = posy
                peaks[dt,2] = peakh

                #peak_locs[dt,:] = [posx, posy]
                #peak_heights[dt] = peakheight

                #print('dt :', dt)
                #print(posx,posy,peakh)
                #print('----------------------------------------------------')

        peaks_list.append(peaks)

    return peaks_list



def prepare_windows(PILseq, activitymap, sclength, pixsize, fps):
    """
    Analyzes each window separately


        Parameters:

        Returns:

    """

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images   

    # initialize numpy float array, which will hold the image sequence  
    array = numpy.zeros((int(nimgs),int(height),int(width)))

    for i in range(nimgs):
        array[i,:,:] = numpy.array(PILseq[i])

    (nt,ni,nj) = numpy.shape(array)

    #print('nt:',nt, '  ni:',ni,'  nj:',nj)

    # we choose the size of the windows based on the spatial correlation length
    # i.e. each window measures: ( 2 x spatialcorrlength )**2

    winsize = int(2.*sclength / pixsize * 1000) # side length of a window (in pixels)

    print('winsize (in pixels): ', winsize)

    # Split up the dynamically filtered ROI-sequence 'array'
    # (note that the size of the ROI can vary)

    n_windows = int(ni / winsize) * int(nj / winsize) # number of windows 

    windows = []

    # let us define a validity mask, which is based on a windowed version
    # of the activity map and indicates whether the CBF varies to an acceptable
    # degree in each window 
    mask = numpy.zeros((int(ni/winsize),int(nj/winsize)), dtype=bool)

    # get average cbf based on activity map:
    mcbf_total = numpy.nanmean(activitymap)
    # get the standard deviation of the cbf based on the activity map:
    scbf_total = numpy.nanstd(activitymap)

    # use the ratio of the stddev to the mean cbf as a measure for spread:
    spread_total = scbf_total / mcbf_total

    # valid_wins: list of valid windows
    valid_wins = []

    # win_centers holds tupels (x,y center coordinates of each valid window)
    win_centers =[]

    # win_meancbf holds the mean cbf within each window (based on activity map)
    win_meancbf = []

    # win_angle holds the direction of the wave propagation
    win_angle = []

    for i in range(int(ni/winsize)):
        for j in range(int(nj/winsize)):

            i1 = i * winsize
            i2 = (i+1) * winsize
            j1 = j * winsize
            j2 = (j+1) * winsize

            windows.append(array[:,i1:i2,j1:j2])

            # check the spread of the CBF within the window_ij:
            mcbf_win = numpy.nanmean(activitymap[i1:i2,j1:j2])
            scbf_win = numpy.nanstd(activitymap[i1:i2,j1:j2])

            spread_win = scbf_win / mcbf_win

            # check if the CBF-spread within the window is smaller than 
            # 65% of the total CBF-spread: 

            if (spread_win < 0.666*spread_total):
                mask[i,j] = True

                # add windowed array to valid_wins:
                valid_wins.append(array[:,i1:i2,j1:j2])

                # save center location of valid window
                win_centers.append((0.5*(j1+j2),0.5*(i1+i2)))

                # save mean cbf within valid window
                win_meancbf.append(mcbf_win)

            else:
                mask[i,j] = False

    print(mask)

    # the analysis is only performed for windows_ij for which mask[i,j] is true

    # get the number of windows for which we perform the analysis:
    n_valid = numpy.sum(mask)
    print('n_valid: ', n_valid)

    # number of available cpus:
    multiprocessing.freeze_support()
    ncpus = multiprocessing.cpu_count()
    if (ncpus > 1):
        ncpus = ncpus-1
    pool = multiprocessing.Pool(ncpus)

    # ncpus: number of processes we will start
    # nwins_per_cpu (list): number of windows, which we analyze per cpu
    nwins_per_cpu = numpy.zeros(ncpus)
    nwins_per_cpu[:] = int(n_valid / ncpus)
    nwins_per_cpu[-1] = n_valid - ((ncpus-1)*int(n_valid / ncpus))

    #print('------------------------------------------------------------------')
    #print('nwins_per_cpu')
    #print(nwins_per_cpu)
    #print('------------------------------------------------------------------')

    # valid_wins holds the array of windows for which we perform the analysis

    # valid_wins_split: holds a list of lists of valid windows! 

    valid_wins_ncpus = []
    for i in range(ncpus):
        if (i > 0):
            istart = int(numpy.sum(nwins_per_cpu[0:i]))
        else:
            istart = 0

        sublist = valid_wins[istart:istart+int(nwins_per_cpu[i-1])]
        valid_wins_ncpus.append(sublist)

    result = pool.map(analyse_windows,
        [valid_wins_ncpus[i] for i in range(ncpus)])

    # result holds a list
    #print('---------------------------------------------------------------')
    #print(result)

    # result hodls a list of a list of arrays 
    # the arrays contain "peaks" with columns: (x, y, height) 
    # the rows correspond to the timeshift 

    speeds = numpy.zeros(n_valid)

    counter = 0
    for i in range(len(result)):
        # loop over cpus
        peak_list = result[i]

        for j in range(len(peak_list)):
            # loop over windows
            peak = peak_list[j]


            print(peak)

            deltax = peak[1,0] - peak[0,0]
            deltay = peak[1,1] - peak[0,1]

            #print('deltax: ',deltax)
            #print('deltay: ',deltay)

            win_angle.append(numpy.arctan2(deltay, deltax)/math.pi*180)

            # distance in pixels between delta_t = 0 and delta_t = 1 
            dist = math.sqrt(deltax**2 + deltay**2)
            print('dist: ', dist)


            print('pixsize: ', pixsize)
            print('fps: ',fps)

            dist = dist * pixsize / 1000.0 # distance in micrometers

            speeds[counter] = dist * float(fps)
            counter += 1


    print(' ------------------------------------------------------------')
    print(speeds)


    # let us write all the interesting information on the disk

    # write center location (pixel units!) of each valid window out:
    numpy.savetxt('./WindowedAnalysis_Results/win_centers_xy.dat', win_centers)

    # write window-specific mean cbf to file:
    numpy.savetxt('./WindowedAnalysis_Results/win_meancbf.dat', win_meancbf)

    # write wave speed to file
    numpy.savetxt('./WindowedAnalysis_Results/win_wavespeed.dat', speeds)

    # write propagation angle to file
    numpy.savetxt('./WindowedAnalysis_Results/win_waveangle.dat', win_angle)


    # get wavelengths within each valid window
    wavelengths = numpy.zeros(n_valid)

    for w in range(len(valid_wins)):
        window = valid_wins[w]
        wavelengths[w] = windowed_wavelength.get_wavelength(window,pixsize)

    numpy.savetxt('./WindowedAnalysis_Results/win_wavelength.dat', wavelengths)




