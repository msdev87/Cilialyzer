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

import matplotlib.pyplot as plt
import multiprocessing
import process_opticalflow

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

    wsize = 7

    li = len(range(wsize, int(ni)-wsize))
    lj = len(range(wsize,int(nj)-wsize))

    optical_flow = numpy.zeros((li,lj))
    x_arr = numpy.zeros((li*lj))
    y_arr = numpy.zeros((li*lj))
    u_arr = numpy.zeros((li*lj))
    v_arr = numpy.zeros((li*lj))

    #print('li',li,'lj',lj)

    u_matrix = numpy.zeros_like(optical_flow)
    v_matrix = numpy.zeros_like(optical_flow)

    speed_matrix = numpy.zeros_like(optical_flow) # optical flow speed

    # we do not determine the optical flow at the margins 
    # (therefore we skip pixels having i=0 , i=1, j=0 or j=1)
    # the window size needs to be chosen to an even number (nr of pixels) 

    # start nrproc processes 
    nrproc = 5
    arguments=[]
    flist1=[]
    flist2=[]
    tlist =[]
    steps = 10 # number of optical flow fields calculated per process 
    for k in range(nrproc):
        for s in range(steps):
            flist1.append(array[nrproc*s+k,:,:])
            flist2.append(array[nrproc*s+k+1,:,:])
            tlist.append(nrproc*s+k)

        arguments.append((flist1,flist2,tlist,fps,pixsize))

    pool = multiprocessing.Pool(nrproc)
    pool.map(process_opticalflow.process, [arguments[i] for i in range(nrproc)])



