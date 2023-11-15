# imports 
import crosscorrelation_zp
from numpy import savetxt
from numpy import zeros_like
import gaussian2Dfit
from math import sqrt
from numpy import shape
from numpy import zeros
from numpy import zeros_like


def process(args):

    # catch the arguments:

    flist1 = args[0]
    flist2 = args[1]
    tlist = args[2]
    pixsize = args[4]
    fps = args[3]
    wsize=15
    (ni,nj) = shape(flist1[0])

    li = len(range(wsize, int(ni)-wsize))
    lj = len(range(wsize,int(nj)-wsize))

    optical_flow = zeros((li,lj))
    x_arr = zeros((li*lj))
    y_arr = zeros((li*lj))
    u_arr = zeros((li*lj))
    v_arr = zeros((li*lj))

    #print('li',li,'lj',lj)

    u_matrix = zeros_like(optical_flow)
    v_matrix = zeros_like(optical_flow)

    speed_matrix = zeros_like(optical_flow) # optical flow speed


    #print('tlist')
    #print(tlist)


    for t in range(len(tlist)):
        cnt=0
        for i in range(wsize,int(ni)-wsize):
            for j in range(wsize,int(nj)-wsize):

                i1 = i-wsize
                i2 = i+wsize
                j1 = j-wsize
                j2 = j+wsize

                frame1 = flist1[t]
                frame2 = flist2[t]

                window1 = frame1[i1:i2,j1:j2]
                window2 = frame2[i1:i2,j1:j2]

                # cross-correlate window1 and window2 

                local_cc = crosscorrelation_zp.ccorr2D_zp(window1, window2)

                # find peak in cross-correlogram (local_cc)  

                sigma = zeros_like(local_cc)
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

                speed_matrix[i-wsize,j-wsize] = sqrt((u_arr[cnt]**2) + (v_arr[cnt]**2)) * pixsize * fps * 0.001

                cnt = cnt+1

        # write optical flow to disk:
        savetxt('../Data/OpticalFlow_1stNov2023_ALI2_1T20x/opticalflow_ws'+str(int(wsize))+'_xpos_'+str(tlist[t])+'.dat',x_arr)
        savetxt('../Data/OpticalFlow_1stNov2023_ALI2_1T20x/opticalflow_ws'+str(int(wsize))+'_ypos_'+str(tlist[t])+'.dat',y_arr)
        savetxt('../Data/OpticalFlow_1stNov2023_ALI2_1T20x/opticalflow_ws'+str(int(wsize))+'_v_'+str(tlist[t])+'.dat',v_arr)
        savetxt('../Data/OpticalFlow_1stNov2023_ALI2_1T20x/opticalflow_ws'+str(int(wsize))+'_u_'+str(tlist[t])+'.dat',u_arr)
        savetxt('../Data/OpticalFlow_1stNov2023_ALI2_1T20x/opticalflow_ws'+str(int(wsize))+'_speed_'+str(tlist[t])+'.dat',speed_matrix)


