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
import tkinter as tk
#import termplotlib as tpl
import crosscorrelation_zp

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

def analyse_windows(array_list, fps):
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
        stcorr = spacetimecorr_zp.stcorr(array,maxtimeshift=round(fps*0.035))

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

                print('dt :', dt)
                print(posx,posy,peakh)
                print('----------------------------------------------------')

        peaks_list.append(peaks)

    return peaks_list



def prepare_windows(PILseq, activitymap, sclength, pixsize, fps, winresults):
    """
    Analyzes each window separately
        Parameters:
        Returns:
    """

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images   

    # initialize numpy float array, which will hold the image sequence  
    array = numpy.zeros((int(nimgs), int(height), int(width)))

    for i in range(nimgs):
        array[i,:,:] = numpy.array(PILseq[i])

    (nt,ni,nj) = numpy.shape(array)

    # We choose the size of the windows based on the spatial correlation length
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
    mask = numpy.zeros((int(ni/winsize), int(nj/winsize)), dtype=bool)

    # get average cbf based on activity map:
    mcbf_total = numpy.nanmean(activitymap)

    # get the standard deviation of the cbf based on the activity map:
    scbf_total = numpy.nanstd(activitymap)

    # scaled activitymap (mean = 0, stddev = 1) 
    activity_scaled = numpy.subtract(activitymap, mcbf_total)
    activity_scaled = activity_scaled / scbf_total

    # use the ratio of the stddev to the mean cbf as a measure for spread:
    spread_total = scbf_total #/ mcbf_total

    # valid_wins: list of valid windows
    valid_wins = []

    # win_centers holds tupels (x,y center coordinates of each valid window)
    win_centers =[]

    # win_meancbf holds the mean cbf within each window (based on activity map)
    win_meancbf = []

    # win_angle holds the direction of the wave propagation
    # win_angle = []

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

            #spread_win = scbf_win / mcbf_win

            #spread_win = numpy.nanstd(activity_scaled[i1:i2,j1:j2])

            #print('spread_win: ', spread_win)

            # check if the CBF-spread within the window is smaller than 
            # 65% of the total CBF-spread: 

            print('10th percentile in window: ', numpy.nanpercentile(activity_scaled[i1:i2,j1:j2],10))

            percentile1 = numpy.nanpercentile(activity_scaled[i1:i2,j1:j2], 10)
            percentile2 = numpy.nanpercentile(activity_scaled[i1:i2,j1:j2], 90)

            spread_win = percentile2 - percentile1

            print('spread_win: ', spread_win)

            # we should add here a condition considering the active percentage
            # within each window, let us demand that the active percentage
            # needs to be at least 80%

            inactive_percentage = numpy.sum(numpy.isnan(activitymap[i1:i2,j1:j2])) / activitymap[i1:i2,j1:j2].size

            if (spread_win < 3) and (inactive_percentage < 0.2) : #*spread_total):
                mask[i,j] = True

                # add windowed array to valid_wins:
                valid_wins.append(array[:,i1:i2,j1:j2])

                # save center location of valid window
                win_centers.append((0.5*(j1+j2),0.5*(i1+i2)))

                # save mean cbf within valid window
                win_meancbf.append(mcbf_win)

            else:
                mask[i,j] = False
                """
                # !!!!!!!!!!!!!!!!!!!! TEST !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
                mask[i,j] = True
                # add windowed array to valid_wins:
                valid_wins.append(array[:,i1:i2,j1:j2])
                # save center location of valid window
                win_centers.append((0.5*(j1+j2),0.5*(i1+i2)))
                # save mean cbf within valid window
                win_meancbf.append(mcbf_win)
                #!!!!!!!!!!!!!!!!!!!!! TEST !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
                """
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

        sublist = valid_wins[istart:istart+int(nwins_per_cpu[i])]
        print('len of sublist:', len(sublist))


        valid_wins_ncpus.append(sublist)

    result = pool.map(analyse_windows,
        [valid_wins_ncpus[i] for i in range(ncpus)], fps)

    # result holds a list
    #print('---------------------------------------------------------------')
    #print(result)

    # result holds a list of a list of arrays 
    # the arrays contain "peaks" with columns: (x, y, height) 
    # the rows correspond to the timeshift 

    speeds = numpy.zeros(n_valid)
    cctimes = numpy.zeros(n_valid)
    cclengths = numpy.zeros(n_valid)
    wave_directions = numpy.zeros(n_valid)

    counter = 0
    for i in range(len(result)):
        # loop over cpus
        peak_list = result[i]

        for j in range(len(peak_list)):
            # loop over windows
            peak = peak_list[j]

            # -----------------------------------------------------------------
            # examine how peak shifts with increasing time delay
            # plot distance vs. time delay
            # shifted_dists = []
            # c = 0
            # while (~numpy.isnan(peak[c+1,0])):
            #    dx = peak[c+1,0] - peak[c,0]
            #    dy = peak[c+1,1] - peak[c,1]
            #    ds = math.sqrt(dx**2 + dy**2)
            #    shifted_dists.append(ds)
            #    c = c+1
            # print(shifted_dists)
            # -----------------------------------------------------------------

            print(' ------------------- peak start -------------------------')
            print(peak)
            print(' -------------------- peak end --------------------------')

            # This is an important note, please read carefully!
            # The space-time correlation C(dx,dy,dt) reprsents the convolution 
            # of I(x,y,t) and I(x+dx,y+dy,t+dt). It is important to note that 
            # the second frame is shifted in space and time simultaneously. 
            # Therefore the displacement of the peak in the 
            # correlogram is given by (-deltax, -deltay) 
            # NOT (deltax, deltay) 

            deltax = -(peak[1,0] - peak[0,0]) # see above comment
            deltay = -(peak[1,1] - peak[0,1]) # see above comment 

            # Note: at this moment (deltax, deltay) corresponds to the movement 
            # of the correlation peak (within delta t) in 'image coordinates'. 
            # A POSITIVE deltay therefore means a vector pointing DOWN, which 
            # corresponds to the orientation of how the video is displayed 

            # However arctan2(y,x) calculates the arctan of y/x 
            # therefore we perform a mirroring around the x-axis 
            # in order to being able to use arctan2 to determine the angles

            deltay = -deltay

            #print('deltax: ',deltax)
            #print('deltay: ',deltay)

            wave_directions[counter] = numpy.arctan2(deltay, deltax)

            # distance in pixels between delta_t = 0 and delta_t = 1 
            dist = math.sqrt(deltax**2 + deltay**2)
            # print('dist: ', dist)

            # print('pixsize: ', pixsize)
            # print('fps: ',fps)

            dist = dist * pixsize / 1000.0 # distance in micrometers

            speeds[counter] = dist * float(fps)

            # determine cross-correlation time
            # first occurence in first column in peak determines cctime
            bla = numpy.argwhere(numpy.isnan(peak[:,0]))
            if (len(bla) > 0):
                cctimes[counter] = min(bla)[0]
            else:
                cctimes[counter] = len(peak[:,0]) - 1

            cclengths[counter] = speeds[counter] * cctimes[counter]

            counter += 1


    # let us write all the interesting information on the disk
    # write center location (pixel units!) of each valid window out:
    # numpy.savetxt('./WindowedAnalysis_Results/win_centers_xy.dat', win_centers)
    # write window-specific mean cbf to file:
    # numpy.savetxt('./WindowedAnalysis_Results/win_meancbf.dat', win_meancbf)
    # write wave speed to file
    #numpy.savetxt('./WindowedAnalysis_Results/win_wavespeed.dat', speeds)
    # write propagation angle to file
    #numpy.savetxt('./WindowedAnalysis_Results/win_waveangle.dat', wave_directions)

    # get wavelengths within each valid window
    wavelengths = numpy.zeros(n_valid)
    for w in range(len(valid_wins)):
        window = valid_wins[w]
        wavelengths[w] = windowed_wavelength.get_wavelength(window,pixsize)
    #numpy.savetxt('./WindowedAnalysis_Results/win_wavelength.dat', wavelengths)

    #print('---------------------- wavelengths -------------------------------')
    #print(wavelengths)
    #print('------------------------------------------------------------------')

    print('average wavelength: ', numpy.average(wavelengths))

    # -------------------------------------------------------------------------
    # print the most important observable values on the tkiner notebook tab
    # -------------------------------------------------------------------------


    # ----------------------- average wave speed ------------------------------
    n_speeds = numpy.count_nonzero(~numpy.isnan(speeds))

    avg_speed = 0.
    for i in range(n_speeds):
        avg_speed += speeds[i]
    avg_speed = avg_speed / float(n_speeds)

    # display average wave speed:
    winresults.mean_wspeed.set(round(avg_speed,2))
    # -------------------------------------------------------------------------


    # ------------------------- SD of wave speed ------------------------------
    sd_wave_speed = numpy.nanstd(speeds)

    # display standard deviation of the wave speed:
    winresults.sd_wspeed.set(round(sd_wave_speed,2))
    # -------------------------------------------------------------------------


    # --------------------- average cross-correlation time --------------------
    winresults.cctime.set(round(1000*numpy.average(cctimes) / float(fps),0))
    # -------------------------------------------------------------------------


    # ---------------------------- wave disorder ------------------------------
    # consider each wave propagation direction as a vector of length 1 
    # get the length of the average vector R 
    # 1-R finally represents the wave disorder
    print('------------------ wave directions -------------------- ')
    print(wave_directions / math.pi * 180)

    avg_sin = numpy.average(numpy.sin(wave_directions))
    avg_cos = numpy.average(numpy.cos(wave_directions))
    winresults.wdisorder.set( round((1 - math.sqrt(avg_sin**2 + avg_cos**2)),2))
    # -------------------------------------------------------------------------


class results:

    def __init__(self, parent):

        self.parent_tktab = parent

        # ------- preparing the frames to display the mean wave speed ---------

        # text label displaying "Mean wave speed" 
        self.mean_wspeed_label = tk.Label(self.parent_tktab,
            text="Mean wave speed [μm/s]: ", anchor='e',
            font=("TkDefaultFont",12),width=30)
        self.mean_wspeed_label.place(in_=self.parent_tktab,
            anchor="c", relx=0.35, rely=0.7)

        # label to display the numeric value of the mean wave speed: 
        self.mean_wspeed = tk.StringVar()
        self.mean_wspeed.set(0)
        self.mean_wspeed_display = tk.Label(self.parent_tktab,
            textvariable=self.mean_wspeed, anchor='w',
            font=("TkDefaultFont",12), width=10)
        self.mean_wspeed_display.place(in_=self.parent_tktab, anchor="c",
                relx=0.65, rely=0.7)


        # ----- preparing the frames to display the SD of the wave speed ------

        # text label displaying "SD wave speed" 
        self.sd_wspeed_label = tk.Label(self.parent_tktab,
            text="SD wave speed [μm/s]: ", anchor='e',
            font=("TkDefaultFont",12), width=30)
        self.sd_wspeed_label.place(in_=self.parent_tktab,
            anchor="c", relx=0.35, rely=0.75)

        # label to display the numeric value of the mean wave speed:
        self.sd_wspeed = tk.StringVar()
        self.sd_wspeed.set(0)
        self.sd_wspeed_display = tk.Label(self.parent_tktab,
            textvariable=self.sd_wspeed, anchor='w',
            font=("TkDefaultFont",12), width=10)
        self.sd_wspeed_display.place(in_=self.parent_tktab, anchor="c",
                relx=0.65, rely=0.75)

        # ---- preparing the frames to display the avg cross-corr time -------

        # text label displaying the "average cross-corr time" 
        self.cctime_label = tk.Label(self.parent_tktab,
            text="Average cross-correlation time [ms]: ", anchor='e',
            font=("TkDefaultFont",12), width=30)
        self.cctime_label.place(in_=self.parent_tktab,
            anchor="c", relx=0.35, rely=0.8)

        # label to display the numeric value of the average cctime 
        self.cctime = tk.StringVar()
        self.cctime.set(0)
        self.cctime_display = tk.Label(self.parent_tktab,
            textvariable=self.cctime, anchor='w',
            font=("TkDefaultFont",12), width=10)
        self.cctime_display.place(in_=self.parent_tktab, anchor="c",
                relx=0.65, rely=0.8)

        # ---- preparing the frames to display the avg cross-corr length -------

        # text label displaying the "average cross-corr length"
        self.cclength_label = tk.Label(self.parent_tktab,
            text="Average cross-correlation length [μm]: ", anchor='e',
            font=("TkDefaultFont",12), width=30)
        self.cclength_label.place(in_=self.parent_tktab,
            anchor="c", relx=0.35, rely=0.85)

        # label to display the numeric value of the average cclength
        self.cclength = tk.StringVar()
        self.cclength.set(0)
        self.cclength_display = tk.Label(self.parent_tktab,
            textvariable=self.cclength, anchor='w',
            font=("TkDefaultFont",12), width=10)
        self.cclength_display.place(in_=self.parent_tktab, anchor="c",
                relx=0.65, rely=0.85)

        # ------ preparing the frames to display the "wave disorder" ---------

        # text label displaying the "wave disorder" 
        self.wdisorder_label = tk.Label(self.parent_tktab,
            text="Wave disorder: ", anchor='e',
            font=("TkDefaultFont",12), width=30)
        self.wdisorder_label.place(in_=self.parent_tktab,
            anchor="c", relx=0.35, rely=0.9)

        # label to display the numeric value of the wave disorder 
        self.wdisorder = tk.StringVar()
        self.wdisorder.set(0)
        self.wdisorder_display = tk.Label(self.parent_tktab,
            textvariable=self.wdisorder, anchor='w',
            font=("TkDefaultFont",12), width=10)
        self.wdisorder_display.place(in_=self.parent_tktab, anchor="c",
                relx=0.65, rely=0.9)











