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

def get_opticalflowFB(tkframe, PILseq, pixsize, fps):
    """ compute optical flow based on Farneback's algorithm """

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images   

    u_flow = []
    v_flow = []

    for t in range(nimgs-1):

        img1 = numpy.array(PILseq[t])
        img2 = numpy.array(PILseq[t+1])

        flow = cv2.calcOpticalFlowFarneback(
            img1, img2, None, 0.75, 3, 16, 5, 5, 1.1, 0)

        # Note the following convention! 
        # The function finds the optical flow, so that: 
        # prev(y,x) ~ next( y+flow(y,x)[1] , x+flow(y,x)[0]) 

        v_flow.append(-flow[...,1])
        u_flow.append(-flow[...,0])

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
    shrink_factor = 0.25
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
        ax.quiver(xmat, ymat, umat, vmat,width=0.002,scale=0.12, scale_units='xy',headaxislength=2.0,headwidth=2.0,headlength=2.0)
        can.draw()
        can.flush_events()
        time.sleep(0.01)
        ax.clear()

    # compute average autocorrelation of optical flow 
    for t in range(nimgs-1):
        umat = ndimage.interpolation.zoom(u_flow[t][:,:],shrink_factor)
        vmat = ndimage.interpolation.zoom(v_flow[t][:,:],shrink_factor)
        ucorr=autocorrelation_zeropadding.acorr2D_zp(umat)
        vcorr=autocorrelation_zeropadding.acorr2D_zp(vmat)
        if (t==0):
            corr=ucorr+vcorr
        else:
            corr=corr+ucorr+vcorr

    # plot 'corr'
    fig = plt.figure()
    ax = plt.axes()
    ax.set_aspect('equal', 'box')
    plt.rcParams["figure.figsize"] = (5,5)

    ax.imshow(corr)
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



