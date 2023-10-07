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

    print('li',li,'lj',lj)

    u_matrix = numpy.zeros_like(optical_flow)
    v_matrix = numpy.zeros_like(optical_flow)

    speed_matrix = numpy.zeros_like(optical_flow) # optical flow speed

    # we do not determine the optical flow at the margins 
    # (therefore we skip pixels having i=0 , i=1, j=0 or j=1)
    # the window size needs to be chosen to an even number (nr of pixels) 

    for t in range(nt):
        cnt = 0
        for i in range(wsize,int(ni)-wsize):
            for j in range(wsize,int(nj)-wsize):

                i1 = i-wsize
                i2 = i+wsize
                j1 = j-wsize
                j2 = j+wsize

                window1 = array[t,i1:i2,j1:j2]
                window2 = array[t+1,i1:i2,j1:j2]

                # cross-correlate window1 and window2 

                local_cc = crosscorrelation_zp.ccorr2D_zp(window1, window2)

                # find peak in cross-correlogram (local_cc) 
                #print('-----------')
                #print(local_cc)

                sigma = numpy.zeros_like(local_cc)
                sigma[:,:] = 1.0

                try:
                    # get position (x,y) and height of peak 
                    posx, posy, peakh = gaussian2Dfit.fit(local_cc, sigma)
                except:
                    posx, posy, peakh = float(wsize), float(wsize), 0.5

                # displacement of the peak:
                u = posx - wsize
                v = posy - wsize

                # note that from the crosscorrelation, we get -u and -v 
                # (as the second image provided to crosscorris shifted in time)
                u_arr[cnt] = -u
                v_arr[cnt] = -v
                x_arr[cnt] = j+0.5-wsize
                y_arr[cnt] = i+0.5-wsize

                u_matrix[i-wsize,j-wsize] = u_arr[cnt] * pixsize * fps * 0.001
                v_matrix[i-wsize,j-wsize] = v_arr[cnt] * pixsize * fps * 0.001

                speed_matrix[i-wsize,j-wsize] = math.sqrt((u_arr[cnt]**2) + (v_arr[cnt]**2)) * pixsize * fps * 0.001

                cnt = cnt + 1

        # plot optical flow field
        #plt.rcParams["figure.figsize"] = (25,25)
        #plt.quiver(x_arr, y_arr, u_arr, v_arr)
        #plt.savefig('opticalflow.png')

        # write optical flow to disk:
        numpy.savetxt('./Data/OpticalFlow_27thFeb2023_9T20x/opticalflow_ws'+str(int(wsize))+'_xpos_'+str(t)+'.dat',x_arr)
        numpy.savetxt('./Data/OpticalFlow_27thFeb2023_9T20x/opticalflow_ws'+str(int(wsize))+'_ypos_'+str(t)+'.dat',y_arr)
        numpy.savetxt('./Data/OpticalFlow_27thFeb2023_9T20x/opticalflow_ws'+str(int(wsize))+'_v_'+str(t)+'.dat',v_arr)
        numpy.savetxt('./Data/OpticalFlow_27thFeb2023_9T20x/opticalflow_ws'+str(int(wsize))+'_u_'+str(t)+'.dat',u_arr)
        numpy.savetxt('./Data/OpticalFlow_27thFeb2023_9T20x/opticalflow_ws'+str(int(wsize))+'_speed_'+str(t)+'.dat',speed_matrix)


        """
        # -------------------------------------------------------------------
        # calculate the autocorrelation of the optical flow field!

        delta_i = -int(ni/2)
        delta_j = -int(nj/2)

        autocorr = numpy.zeros_like(u_matrix)

        # loop over displacements
        for di in range(ni):
            for dj in range(nj):

                summe = 0.0
                # for each displacement loop over indices
                for i in range(ni):
                    for j in range(nj):

                        try:
                            i1 = i
                            j1 = j
                            i2 = i - int(ni/2) + di
                            j2 = j - int(nj/2) + dj

                            scalarproduct = (u_matrix[i1,j1] * u_matrix[i2,j2]) + (v_matrix[i1,j1] * v_matrix[i2,j2])
                        except:
                            scalarproduct = 0.0

                        summe = summe + scalarproduct

                autocorr[di,dj] = summe

        plt.imshow(numpy.sqrt(numpy.absolute(autocorr)))
        plt.savefig('autocorr'+string(t)+'.png')
        """
