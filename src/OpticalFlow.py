from PIL import Image
import numpy
import math
import matplotlib.pyplot as plt
import os
import multiprocessing
import spacetimecorr_zp
import gaussian2Dfit

import tkinter as tk
import crosscorrelation_zp

import matplotlib
import multiprocessing
import process_opticalflow
import cv2

from scipy import ndimage

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import time
import autocorrelation_zeropadding

from scipy.signal import medfilt2d

def get_opticalflowFB(tkframe, PILseq, pixsize, fps):
    """ compute optical flow based on Farneback's algorithm """

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images   

    u_flow = []
    v_flow = []

    #nimgs = 300

    for t in range(nimgs-1):

        img1 = numpy.array(PILseq[t])
        img2 = numpy.array(PILseq[t+1])

        flow = cv2.calcOpticalFlowFarneback(
            img1, img2, None, 0.9, 1, 15, 5, 5, 1.1, 0)

        # Note the following convention! 
        # The function finds the optical flow, so that: 
        # prev(y,x) ~ next( y+flow(y,x)[1] , x+flow(y,x)[0]) 
        # Therefore we take the negative of flow

        v_flow.append(flow[...,1])
        u_flow.append(flow[...,0])

    # remove outliers in u_flow and v_flow
    # i.e. topmost 0.25% and lowermost 0.5%
    u1 = numpy.percentile(u_flow, 1)
    u2 = numpy.percentile(u_flow, 99)
    v1 = numpy.percentile(v_flow, 1)
    v2 = numpy.percentile(v_flow, 99)

    for i in range(nimgs-1):

        u_flow[i][u_flow[i] < u1] = u1
        u_flow[i][u_flow[i] > u2] = u2
        v_flow[i][v_flow[i] < v1] = v1
        v_flow[i][v_flow[i] > v2] = v2

        # further outlier removal in u_flow and v_flow by median filtering (3x3):   
        u_flow[i] = medfilt2d(u_flow[i])
        v_flow[i] = medfilt2d(v_flow[i])
        # spatial smoothing
        u_flow[i] = ndimage.gaussian_filter(u_flow[i], sigma=2)
        v_flow[i] = ndimage.gaussian_filter(v_flow[i], sigma=2)

    # smooth optical flow by local averaging (2x2) over all axes!  
    u_flow = ndimage.uniform_filter(u_flow, size=2)
    v_flow = ndimage.uniform_filter(v_flow, size=2)

    # normalize the flow field!
    nt, ni, nj = len(u_flow), len(u_flow[0][:,0]), len(u_flow[0][0,:])
    #speeds = numpy.zeros((nt,ni,nj))

    print('start loop maxspeed')
    max_speed = 0.0

    max_speed=numpy.max(numpy.sqrt(numpy.array(u_flow)**2 + numpy.array(v_flow)**2))
    """
    for t in range(nt):
        for i in range(ni):
            for j in range(nj):
                speed = math.sqrt( u_flow[t][i,j]**2 + v_flow[t][i,j]**2 )

                if (speed > max_speed):
                    max_speed = speed
                # speeds[t,i,j] = math.sqrt( u_flow[]**2 + v_flow[]**2 )
    """
    print('finished')



    # normalize: 
    for t in range(nt):
        u_flow[t][:,:] = u_flow[t][:,:] / max_speed
        v_flow[t][:,:] = v_flow[t][:,:] / max_speed

    # contruct matrix holding the pixel positions 
    isize = len(u_flow[0][:,0])
    jsize = len(u_flow[0][0,:])

    xarr = numpy.array(range(jsize)) * pixsize / 1000.0
    yarr = numpy.array(range(isize)) * pixsize / 1000.0

    xmat, ymat = numpy.meshgrid(xarr, yarr)

    # display optical flow field
    fig = plt.figure()
    ax = plt.axes()
    ax.set_aspect('equal', 'box')
    plt.rcParams["figure.figsize"] = (5,5)

    # note: the optical flow fields get downsampled before they are plotted
    shrink_factor = 0.12
    xmat = ndimage.interpolation.zoom(xmat,shrink_factor)
    ymat = ndimage.interpolation.zoom(ymat,shrink_factor)
    vmat = ndimage.interpolation.zoom(u_flow[0][:,:],shrink_factor)
    umat = ndimage.interpolation.zoom(v_flow[0][:,:],shrink_factor)

    ax.quiver(xmat, ymat, umat, vmat,width=0.002,scale=0.12, scale_units='xy',headaxislength=2.0,headwidth=2.0,headlength=2.0)

    can = FigureCanvasTkAgg(fig, tkframe)
    can.draw()
    can.get_tk_widget().place(in_=tkframe, anchor="c", relx=0.25, rely=0.5)
    can._tkcanvas.place(in_=tkframe)

    for t in range(nimgs-1):
        umat = ndimage.interpolation.zoom(u_flow[t][:,:],shrink_factor)
        vmat = ndimage.interpolation.zoom(v_flow[t][:,:],shrink_factor)
        #vmat = -vmat
        ax.clear()
        ax.quiver(xmat, ymat, umat, vmat,width=0.002,scale=0.15, scale_units='xy',headaxislength=3.0,headwidth=3.0,headlength=3.0)
        can.draw()
        #plt.savefig('./png/frame-'+str(i)+'.png')
        #time.sleep(1)
        can.flush_events()
        time.sleep(0.01)
        ax.clear()

    # compute average autocorrelation of optical flow 
    for t in range(nimgs-1):
        umat = u_flow[t][:,:] # ndimage.interpolation.zoom(u_flow[t][:,:], shrink_factor)
        vmat = v_flow[t][:,:] # ndimage.interpolation.zoom(v_flow[t][:,:], shrink_factor)
        ucorr = autocorrelation_zeropadding.acorr2D_zp(umat, centering=False, normalize=False)
        vcorr = autocorrelation_zeropadding.acorr2D_zp(vmat, centering=False, normalize=False)
        if (t == 0):
            corr = ucorr + vcorr
        else:
            corr = corr + ucorr + vcorr

    corr = 1.0 / float(nimgs-1) * corr

    if (numpy.min(corr) < 0):
        corr = corr - numpy.min(corr)

    print('max corr:')
    print(numpy.max(corr))
    print('min corr')
    print(numpy.min(corr))

    # plot 'corr'
    fig = plt.figure()
    ax = plt.axes()
    ax.set_aspect('equal', 'box')
    plt.rcParams["figure.figsize"] = (5,5)

    ax.set_xlabel("$\Delta$x [$\mu$m]",fontsize=16)
    ax.set_ylabel("$\Delta$y [$\mu$m]",fontsize=16)
    ax.axes.tick_params(labelsize=15)
    fig.tight_layout()

    left = -len(umat[0,:])/2.0 * pixsize * 0.001
    right = -left
    bot = -len(umat[:,0])/2.0 * pixsize * 0.001
    top = -bot

    ax.imshow(numpy.sqrt(corr), extent=(left,right,bot,top),cmap="gray")
    can = FigureCanvasTkAgg(fig, tkframe)
    can.draw()
    can.get_tk_widget().place(in_=tkframe, anchor="c", relx=0.75, rely=0.5)
    can._tkcanvas.place(in_=tkframe)



def get_opticalflow(PILseq, pixsize, fps):

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images   

    # initialize numpy float array, which will hold the image sequence  
    array = numpy.zeros((int(nimgs),int(height),int(width)))

    for i in range(nimgs):
        array[i,:,:] = numpy.array(PILseq[i])

    (nt,ni,nj) = numpy.shape(array)

    #print('nt:',nt, '  ni:',ni,'  nj:',nj)

    #wsize = 7

    #li = len(range(wsize, int(ni)-wsize))
    #lj = len(range(wsize,int(nj)-wsize))
    #optical_flow = numpy.zeros((li,lj))
    #x_arr = numpy.zeros((li*lj))
    #y_arr = numpy.zeros((li*lj))
    #u_arr = numpy.zeros((li*lj))
    #v_arr = numpy.zeros((li*lj))

    #print('li',li,'lj',lj)

    #u_matrix = numpy.zeros_like(optical_flow)
    #v_matrix = numpy.zeros_like(optical_flow)

    #speed_matrix = numpy.zeros_like(optical_flow) # optical flow speed

    # we do not determine the optical flow at the margins 
    # (therefore we skip pixels having i=0 , i=1, j=0 or j=1)
    # the window size needs to be chosen to an even number (nr of pixels) 

    # start nrproc processes 
    nrproc = 15
    arguments=[]

    steps = 15 # number of optical flow fields calculated per process 
    for k in range(nrproc):
        flist1=[]
        flist2=[]
        tlist=[]
        for s in range(steps):
            flist1.append(array[nrproc*s+k,:,:])
            flist2.append(array[nrproc*s+k+1,:,:])
            tlist.append(nrproc*s+k)

        arguments.append((flist1,flist2,tlist,fps,pixsize))

    pool = multiprocessing.Pool(nrproc)
    pool.map(process_opticalflow.process, [arguments[i] for i in range(nrproc)])



