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

        peak_locs = numpy.zeros((n_timeshifts,2))
        peak_heights = numpy.zeros(n_timeshifts)

        for dt in range(n_timeshifts):

            # we fit only the middle part of the cross-correlogram 
            # i.e. the peak, which is characterized by the greatest values 
            # therefore, we select only those values, which are 
            # greater than 1/e from the cross-correlogram

            print('--------------------------------------------------------------')
            
            print('max1 in stcorr: ', numpy.max(stcorr[dt]))
            stcorr[dt] = numpy.subtract(stcorr[dt], 1./math.e)
            NaN_inds = numpy.where(stcorr[dt] < 0)
            stcorr[dt][NaN_inds] = 0. #float("NaN")

            print('max2 in stcorr: ', numpy.max(stcorr[dt]))

            sigma = numpy.zeros_like(stcorr[dt])
            inds = numpy.where(stcorr[dt] > 0)
            sigma[NaN_inds] = 1e6
            sigma[inds] = 1.


            posx, posy, peakh = gaussian2Dfit.fit(stcorr[dt], sigma)

            #peak_locs[dt,:] = [posx,posy]
            #peak_heights[dt] = peakheight

            print('dt :', dt)
            print(posx,posy,peakh)
            print('--------------------------------------------------------------')


    return (posx, posy, peakh)



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

    print('nt:',nt, '  ni:',ni,'  nj:',nj)

    # we choose the size of the windows based on the spatial correlation length
    # i.e. each window measures: ( 2 x spatialcorrlength )**2

    winsize = int(2*sclength / pixsize * 1000) # side length of a window (in pixels)

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

            if (spread_win < 0.65*spread_total):
                mask[i,j] = True

                # add windowed array to valid_wins:
                valid_wins.append(array[:,i1:i2,j1:j2])

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
    # nwins_per_cpu: number of windows, which we analyze per cpu
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

    # test
    #res = analyse_windows(valid_wins_ncpus[0])

