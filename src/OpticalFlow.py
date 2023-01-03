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

    print('nt:',nt, '  ni:',ni,'  nj:',nj)

    optical_flow = numpy.zeros_like(array[0,:,:])
    x_arr = numpy.zeros((ni*nj))
    y_arr = numpy.zeros((ni*nj))
    u_arr = numpy.zeros((ni*nj))
    v_arr = numpy.zeros((ni*nj))

    u_matrix = numpy.zeros_like(optical_flow)
    v_matrix = numpy.zeros_like(optical_flow)

    speed_matrix = numpy.zeros_like(optical_flow) # optical flow speed



    # we do not determine the optical flow at the margins 
    # (therefore we skip pixels having i=0 , i=1, j=0 or j=1)
    # the window size needs to be chosen to an even number (nr of pixels) 

    wsize = 7

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
                u_arr[cnt] = posx - wsize
                v_arr[cnt] = posy - wsize
                x_arr[cnt] = j+0.5
                y_arr[cnt] = i+0.5

                u_matrix[i,j] = u_arr[cnt]
                v_matrix[i,j] = v_arr[cnt]

                speed_matrix[i,j] = math.sqrt((u_arr[cnt]**2) + (v_arr[cnt]**2))

                cnt = cnt + 1

        # plot optical flow field
        #plt.rcParams["figure.figsize"] = (25,25)
        #plt.quiver(x_arr, y_arr, u_arr, v_arr)
        #plt.savefig('opticalflow.png')

        # write optical flow to disk:
        numpy.savetxt('./OpticalFlow_23rdNov2022_12_50x/opticalflow_ws'+str(int(wsize))+'_xpos_'+str(t)+'.dat',x_arr)
        numpy.savetxt('./OpticalFlow_23rdNov2022_12_50x/opticalflow_ws'+str(int(wsize))+'_ypos_'+str(t)+'.dat',y_arr)
        numpy.savetxt('./OpticalFlow_23rdNov2022_12_50x/opticalflow_ws'+str(int(wsize))+'_v_'+str(t)+'.dat',v_arr)
        numpy.savetxt('./OpticalFlow_23rdNov2022_12_50x/opticalflow_ws'+str(int(wsize))+'_u_'+str(t)+'.dat',u_arr)
        numpy.savetxt('./OpticalFlow_23rdNov2022_12_50x/opticalflow_ws'+str(int(wsize))+'_speed_'+str(t)+'.dat',speed_matrix)



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


