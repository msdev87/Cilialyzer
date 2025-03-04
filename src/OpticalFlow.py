from PIL import Image
import PIL
import numpy
#import math_utils
import matplotlib.pyplot as plt
import os
#import multiprocessing
#import spacetimecorr_zp
#import gaussian2Dfit
from scipy.ndimage import gaussian_filter
#import tkinter as tk
#import crosscorrelation_zp

import matplotlib
import multiprocessing
import process_opticalflow
import cv2

from scipy import ndimage

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
#from matplotlib.figure import Figure
import time
from math_utils import autocorrelation_zeropadding

from scipy.signal import medfilt2d

#import FlipbookROI

def get_opticalflowFB(tkframe, PILseq, pixsize, validity_mask, fps):
    """ compute optical flow based on Farneback's algorithm """

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images   

    u_flow = []
    v_flow = []

    # ws: window size in Farneback's optical flow
    ws = round(1750.0 / pixsize)  # we set the window size to about 2 microns
    if (ws < 5): ws = 5

    if (nimgs > 600): nimgs=600

    for t in range(nimgs-1):

        img1 = gaussian_filter(PILseq[t], sigma=(1, 1), truncate=1.0)
        img2 = gaussian_filter(PILseq[t+1], sigma=(1, 1), truncate=1.0)

        flow = cv2.calcOpticalFlowFarneback(
            img1, img2, None, 0.9, 2, ws, 7, 7, 1.5, 0)

        # Note the following convention
        # The function finds the optical flow, so that: 
        # prev(y,x) ~ next( y+flow(y,x)[1] , x+flow(y,x)[0]) 

        v_flow.append(flow[...,1])
        u_flow.append(flow[...,0])

    # remove outliers in u_flow and v_flow
    u1 = numpy.percentile(u_flow, 0.1)
    u2 = numpy.percentile(u_flow, 99.9)
    v1 = numpy.percentile(v_flow, 0.1)
    v2 = numpy.percentile(v_flow, 99.9)

    for i in range(nimgs-1):

        u_flow[i][u_flow[i] < u1] = u1
        u_flow[i][u_flow[i] > u2] = u2
        v_flow[i][v_flow[i] < v1] = v1
        v_flow[i][v_flow[i] > v2] = v2

        # further outlier removal in u_flow and v_flow by median filtering (3x3):   
        u_flow[i] = medfilt2d(u_flow[i])
        v_flow[i] = medfilt2d(v_flow[i])
        # spatial smoothing
        ss = 700.0 / pixsize
        u_flow[i] = ndimage.gaussian_filter(u_flow[i], sigma=ss, truncate=2.0)
        v_flow[i] = ndimage.gaussian_filter(v_flow[i], sigma=ss, truncate=2.0)

    # smooth optical flow by local averaging (2x2) over all axes!  
    u_flow = ndimage.uniform_filter(u_flow, size=2)
    v_flow = ndimage.uniform_filter(v_flow, size=2)

    # normalize the flow field!
    nt, ni, nj = len(u_flow), len(u_flow[0][:,0]), len(u_flow[0][0,:])
    #speeds = numpy.zeros((nt,ni,nj))

    max_speed=numpy.max(numpy.sqrt(numpy.array(u_flow)**2 + numpy.array(v_flow)**2))

    # Normalize:
    for t in range(nt):
        u_flow[t][:,:] = u_flow[t][:,:] / max_speed
        v_flow[t][:,:] = v_flow[t][:,:] / max_speed

    # Write optical flow speed to disk (directory ofspeed)
    speedmat = numpy.zeros_like(u_flow)
    for t in range(nimgs-1):
        speedmat[t][:,:] = numpy.sqrt(u_flow[t][:,:]**2 + v_flow[t][:,:]**2)

    mx = numpy.max(speedmat)
    mi = numpy.min(speedmat)
    for i in range(nimgs-1):
        img = speedmat[i][:,:]
        img = PIL.Image.fromarray(numpy.uint8((img - mi) / (mx-mi) * 255))
        #img.save('./ofspeed/ofspeed-'+str(i).zfill(3)+'.png')


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
    can.get_tk_widget().place(in_=tkframe, anchor="c", relx=0.2, rely=0.5)
    can._tkcanvas.place(in_=tkframe)

    color = numpy.sqrt(umat**2 + vmat**2)

    plt.set_cmap("Greys")

    for t in range(nimgs-1):
        umat = ndimage.interpolation.zoom(u_flow[t][:,:],shrink_factor)
        vmat = ndimage.interpolation.zoom(v_flow[t][:,:],shrink_factor)
        color = numpy.sqrt(umat**2 + vmat**2)

        #vmat = -vmat
        ax.clear()
        ax.quiver(xmat, ymat, umat, -vmat,color,width=0.002,scale=0.14, scale_units='xy',headaxislength=4.0,headwidth=4.0,headlength=4.0)
        can.draw()

        # check if folder 'png exists in current working directory
        if not os.path.exists('png'):
            # Create the folder if it does not exist
            os.makedirs('png')

        if os.name == 'nt':
            # on windows
            can.print_figure('.\\png\\frame-' + str(t).zfill(3) + '.png')
        else:
            can.print_figure('./png/frame-'+str(t).zfill(3)+'.png')

        #plt.savefig('./png/frame-'+str(t)+'.png')
        #time.sleep(1)
        can.flush_events()
        time.sleep(0.01)
        ax.clear()

    # ------------ Compute average autocorrelation of optical flow -------------
    for t in range(nimgs-1):
        umat = u_flow[t][:,:] # ndimage.interpolation.zoom(u_flow[t][:,:], shrink_factor)
        vmat = v_flow[t][:,:] # ndimage.interpolation.zoom(v_flow[t][:,:], shrink_factor)
        #ucorr = autocorrelation_zeropadding.acorr2D_zp(umat, centering=False, normalize=False, mask=validity_mask)
        #vcorr = autocorrelation_zeropadding.acorr2D_zp(vmat, centering=False, normalize=False, mask=validity_mask)

        ucorr = autocorrelation_zeropadding.acorr2D_zp(umat, mask=validity_mask)
        vcorr = autocorrelation_zeropadding.acorr2D_zp(vmat, mask=validity_mask)

        if (t == 0):
            corr = ucorr + vcorr
        else:
            corr = corr + ucorr + vcorr

    corr = 1.0 / float(nimgs-1) * corr / 2.0

    #if (numpy.min(corr) < 0):
    #    corr = corr - numpy.min(corr)


    corr = gaussian_filter(corr, sigma=round(500/pixsize), truncate=2.0)


    print('max corr:')
    print(numpy.max(corr))
    print('min corr')
    print(numpy.min(corr))

    # plot 'corr'
    fig = plt.figure()
    ax = plt.axes()
    #ax.set_aspect('equal', 'box')
    plt.rcParams["figure.figsize"] = (5,5)

    ax.set_xlabel("$\Delta$x [$\mu$m]",fontsize=17)
    ax.set_ylabel("$\Delta$y [$\mu$m]",fontsize=17)
    ax.axes.tick_params(labelsize=16)
    fig.tight_layout()

    ny, nx = corr.shape

    # nx = corr.shape #int(100.0 / (pixsize*0.001))
    # ny = #int(100.0 / (pixsize*0.001))

    corrplot = numpy.zeros((ny,nx))
    corrplot[:,:] = corr #numpy.nan

    #dy = ny - len(corr[:,0])
    #dx = nx - len(corr[0,:])

    """
    # the plot is supposed to always span from -50 to +50 micrometers 
    if ((dx > 0) and (dy > 0)):
            corrplot[dy//2:len(corr[:,0])+dy//2,dx//2:len(corr[0,:])+dx//2] = corr
    if ((dx > 0) and (dy <= 0)):
            corrplot[:,dx//2:len(corr[0,:])+dx//2] = corr[-dy//2:len(corr[:,0])+dy//2,:]

    if ((dx <= 0) and (dy > 0)):
        corrplot[dy//2:len(corr[:,0])+dy//2,:] = corr[:,-dx//2:len(corr[0,:])+dx//2]
    if ((dx <= 0) and (dy <= 0)):
        corrplot[:,:] = corr[-dy//2:len(corr[:,0])+dy//2,-dx//2:len(corr[0,:])+dx//2]
    """

    vmax = numpy.max(corr)

    # adapt orientation of corrplot so that the orientation matches 
    # the orientation of the images taken in reflection!
    #corrplot = numpy.flip(corrplot, 1)
    xstart, xend = -0.5 * nx * pixsize * 0.001, 0.5 * nx * pixsize * 0.001
    ystart, yend = -0.5 * nx * pixsize * 0.001, 0.5 * nx * pixsize * 0.001

    ax.imshow(corrplot, extent=(xstart,xend,ystart,yend),cmap="bwr",vmin=-0.35*vmax,vmax=0.35*vmax)

    maxy, maxx = numpy.unravel_index(numpy.argmax(corr, axis=None), corr.shape)
    miny, minx = numpy.unravel_index(numpy.argmin(corr, axis=None), corr.shape)

    ax.plot(0, 0, marker='o', linestyle='None', color='blue', markersize=3)
    ax.plot(minx*pixsize/1000.0, -miny*pixsize/1000.0, marker='o',
        linestyle='None', color='red', markersize=3)

    can = FigureCanvasTkAgg(fig, tkframe)
    can.draw()
    can.get_tk_widget().place(in_=tkframe, anchor="c", relx=0.75, rely=0.5)
    can._tkcanvas.place(in_=tkframe)


    # determine the location of the maximum and the minimum in the correlogram
    # to determine the wavelength

















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



