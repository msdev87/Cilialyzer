# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 19:30:32 2022

@author: Dominic Diem
"""

from PIL import Image
import numpy as np
from numpy.fft import fftn
from numpy.fft import ifftn
import math
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit

#TODO what is the actual dimension of fps? 

'''**************** Velocity of the space time correlogarm: ***************************

    These are the main functions of this class
        
        + I := I[t,x,y]:  Is the video in array format
            - images of size 512x512 pixels
            - around 900 images 

        + fps:  is in dimension [s]

        + pixelsize:  is in dimension [μm]

        + maxCorrTime:  is maximal time-range over wich a correlogram will be drawn [s]

        + vectorMagnification:  since the vectors are too small to be visible one can choose a magnification with which they are drawn

******************************************************'''

# 'total' indicates that the whole field of view is used 

def draw_total_spactime_correlogram_with_velocity_vectors_of_the_peak(I, fps, pixelsize, maxCorrTime, vectorMagnification):
    C = calc_spaceTime_correlogram_manually(I, maxCorrTime);
    correlogram = crop(C);
    Vf = gauss_velocity_field(correlogram, 35);
    V = Vf[0]*vectorMagnification;
    origins = Vf[1];

    x_label_list = [int(i*pixelsize) for i in [50 , -50,-30, -10, 10, 30]];
    y_label_list = [int(i*pixelsize) for i in [-50 , 50, 30, 10, -10, -30]];

    # i entspricht delta t 
    for i in range(maxCorrTime):

        fig, ax  = plt.subplots();
        plt.suptitle("Space time correlogram:" + "  dt = " + str(i/fps) + " [s]")
        im1 = plt.imshow(correlogram[i,:,:], cmap='viridis', interpolation = 'bilinear')

        ax.set_xticklabels(x_label_list)
        ax.set_yticklabels(y_label_list)

        plt.colorbar(im1, orientation='vertical')
        plt.clim(0, 1)
        plt.xlabel('dx [μm]');
        plt.ylabel('dy [μm]');
        plt.quiver(origins[0,i], origins[1,i],  V[0,i], V[1,i], color='r');
        plt.grid()
        plt.savefig("corr" + str(i) + ".png")

'''**************** ROIs velocity field: ***************************

    - Look above for description of the inputs.

******************************************************'''
def draw_my_ROI_velocity_field(I, ROI_x, ROI_y, fps, pixelsize, maxCorrTime, vectorMagnification):

    I = calc_spaceTime_correlogram_of_ROIs_manually(I, ROI_x, ROI_y, maxCorrTime);
    j=i=0;
    V_list = [];
    origins_list =  [];

    # loop over ROIs 
    while(j < I.shape[2]-ROI_y):
            i = 0;
            while(i < I.shape[1]-ROI_x):
                ROI = I[:,i:(i+ROI_x), j:(j+ROI_y)];
                results = gauss_velocity_field(ROI, 10)
                vs = results[0];
                origins_ROI = results[1];
    # ======== Ausreisser ==========================================================
                for m in range(vs.shape[0]):
                    if(np.linalg.norm(vs[:,m], ord=2) > 1):
                        vs[:,m] = [0,0]
                        origins_ROI[:,m] = [0,0]
    # =============================================================================
                vs = vs*vectorMagnification;
                V_list.append(vs);
                for l in range(results[1].shape[1]):
                    origins_ROI[:,l] += [i,j]
                origins_list.append(origins_ROI);
                i += ROI_x;
            j += ROI_y;

    V = np.asarray(V_list);
    origins = np.asarray(origins_list); # kind of peak positions 

    x_label_list = [int(i*pixelsize) for i in [50 , -50,-30, -10, 10, 30]];
    y_label_list = [int(i*pixelsize) for i in [-50 , 50, 30, 10, -10, -30]];

    for k in range(maxCorrTime):
        fig, ax  = plt.subplots();
        plt.suptitle("Space time correlogram:" + "  dt = " + str(k/fps) + " [s]")
        im1 = plt.imshow(I[k,:,:], cmap='viridis', interpolation = 'bilinear')

        ax.set_xticklabels(x_label_list)
        ax.set_yticklabels(y_label_list)

        plt.colorbar(im1, orientation='vertical')
        plt.clim(0, 1)
        plt.xlabel('dx [μm]');
        plt.ylabel('dy [μm]');
        plt.grid()

        for j in range(V.shape[0]):
            origins_ROI = origins[j,:,:];
            V_ROI = V[j,:,:];
            plt.quiver(origins_ROI[0,k], origins_ROI[1,k],  V_ROI[0,k], V_ROI[1,k], color='r');
        plt.savefig("ROI_velocity_" + str(k) + ".png", bbox_inches='tight', pad_inches = 0) 


#TODO
# Ist die in R90 definierte Funktion wirklich eine Rotation im Gegenuhrzeigersinn um 90 grad? 
# bspw: v = (-1, -1) wird auf v' = (-1, 1) abgebildet. M.E. 
#
# Folgende Matrix definiert Abbildung (keine Rotation?) 
#     1  0 
# M = 
#     0 -1

'''**************** Mathematics: *****************************

    Here we list all self inplemented mathematics we kept using
    during this algorithm.

    - R90: rotates a 2D vector 90° counterclockwise

    - Gauss2D: is the bivariant normal distribution

*******************************************************'''

def R90(v):#rotates a 2D vector for 90 degrees
    return [-v[1], v[0]]

# elliptic gaussian
# TODO amplitude A muss nicht als fit-parameter übergeben werden
def Gauss2D(x, y,  mu_x, mu_y,  sig_x, sig_y, A, rho):#mu = expected value, sig = standard deviation
    z = (x - mu_x)**2/ sig_x**2 - 2*rho*(x - mu_x)*(y - mu_y)/(sig_x*sig_y) + (y - mu_y)**2/ sig_y**2
    A = A*1/(2*math.pi*sig_x*sig_y*np.sqrt(1 - rho**2))
    return  A * np.exp( - z/(2*(1 - rho**2)))

def _Gauss2D(M, *args):
        x, y = M
        arr = np.zeros(x.shape)
        for i in range(len(args)//6):
           arr += Gauss2D(x, y, *args[i*6:i*6+6]) #TODO !!!!! WOZU?!! 
        return arr

'''**************** Some helpers: *****************************

    Here we list an arbitrary collection of helper functions.

    - remove_...:  we compute the overall mean picture of the whole video (array) I and the subtract it in order to reduce the background.

    - zeropadding_xy:  8x enlarges the size of the image by surrounding it with zeros... this is needed to not obatin a wrap around effect doing fourier transforms

    - crop:  crops a image of size 512x512 to size 100x100 which is the essential part of the correlogram.

*******************************************************'''    

def remove_overall_mean_from_every_frame_in_I(I):
    # removes the average frame from every frame

    I_mean = np.zeros((I.shape[1],I.shape[2]));
    for i in range(I.shape[0]):
        I_mean += I[i,:,:]/I.shape[0];
    for i in range(I.shape[0]):
        I[i,:,:] = I[i,:,:] - I_mean;
    return I

def zeropadding_xy(I):
    #TODO I DO NOT UNDERSTAND THE ZERO-PADDING
    # es scheint, als würde links und rechts (bzw. unten und oben) gepadded
    # das ist nicht nötig 
    I_zp = np.zeros((I.shape[0], I.shape[1]*3-2, I.shape[2]*3-2));
    I_zp[:,I.shape[1]-2:2*I.shape[1]-2,I.shape[2]-2:2*I.shape[2]-2 ] = I;
    return I_zp

def crop(I):
    return I[:, 206:306, 206:306]



'''**************** Space time correlogram: *****************************
   
    - We compute the space time correlogram by exploting the 2D Wiener-Khinchin theorem
    and then summing over the whole time-domain.
    
    - We first need to zeropad the xy-domain (prevent wrap arounds), and then repeat the whole process with a equally sized xy-field
    entirely made out of ones in order to remove the effects induced by zeropadding.
    

*******************************************************'''

def calc_spaceTime_correlogram_manually(I, dt_max):
    # removes average image: 
    I = remove_overall_mean_from_every_frame_in_I(I) 
    I = I - np.mean(I[:,:,:]) # centering of the array  
    corr_tot = np.zeros(I.shape);#before zero padding
    mask_correction_factors = np.zeros(I.shape);
    I = zeropadding_xy(I);
    xy = np.complex128(np.zeros((I.shape[1], I.shape[2])));

    # We compute dt in [1, dt_max]
    for dt in range(dt_max):
        for t in range(I.shape[0]-dt):
            # räumliches cross-correlogram
            xy += np.fft.ifftshift(ifftn( (np.multiply(np.conjugate(np.fft.fftshift(fftn(I[t,:,:]))), np.fft.fftshift(fftn(I[t+dt,:,:]))))/(I.shape[1] * I.shape[2])))/I.shape[0];# das ganze mal 1/N_t
            if(t %50 == 0):
                print(str( round((dt*(I.shape[0]-dt) + t)/(dt_max*I.shape[0])*100, 1)) + "%"); 
        corr_tot[dt,:,:] = (abs(xy)/np.var(I))[int(corr_tot.shape[1]-2):int(2*corr_tot.shape[1]-2), int(corr_tot.shape[2]-2):int(2*corr_tot.shape[2]-2)];
        xy = np.complex128(np.zeros((I.shape[1], I.shape[2])));

    #TODO Ich verstehe nicht ganz wieso die Maske so konstruiert wird. 
    # Die Maske scheint kein zeropadding zu haben? 
    # Ergebnis wird so doch nicht korrekt normiert? 

    # Ausserdem: die Maske bleibt für jeden Zeitschritt dieselbe 
    # Die Normierung muss nur einmal berechnet werden!


    #remove the mask
    input_domain  = np.ones_like(I)
    for dt in range(dt_max):
        for t in range(input_domain.shape[0]-dt):
            xy += np.fft.ifftshift(ifftn( (np.multiply(np.conjugate(np.fft.fftshift(fftn(input_domain[t,:,:]))), np.fft.fftshift(fftn(input_domain[t+dt,:,:]))))/(input_domain.shape[1] * input_domain.shape[2])))/input_domain.shape[0];# das ganze mal 1/N_t
        mask_correction_factors[dt,:,:] = abs(xy)[int(corr_tot.shape[1]-2):int(2*corr_tot.shape[1]-2), int(corr_tot.shape[2]-2):int(2*corr_tot.shape[2]-2)];
        xy = np.complex128(np.zeros((input_domain.shape[1], input_domain.shape[2])));
    
    if(abs(mask_correction_factors.all()) > 0):
        autocorr = corr_tot / mask_correction_factors    
    else:
        autocorr = corr_tot
    return autocorr



def calc_spaceTime_correlogram_of_ROIs_manually(I, ROI_x, ROI_y, dt_max):#I := I(t,x,y)
    j = 0;
    corr = np.zeros_like(I);
    while(j < I.shape[2]):
        i = 0;
        while(i < I.shape[1]):
            ROI = I[:,i:(i+ROI_x), j:(j+ROI_y)];
            corr[:,i:(i+ROI_x), j:(j+ROI_y)] = calc_spaceTime_correlogram_manually(ROI, dt_max);
            i += ROI_x;
        j += ROI_y;
    return corr



'''**************** Peak velocity of the correlogram: *****************************
   
    We compute the velocity and its direction of the peak by first using:
        
        - where_is_my_Gaussian_maximum:  fits the correlogram 'corr1' with a general bivariant Gaussian distribution & then finds and returns it's maximum.
    
    then the algorithm
    
        - gauss_velocity_field: computes the velocity and its direction in dimension [pixel] by computing the shift of two upfollowing correlgrom. (Note that we only use physical dimensions in the main function).
    
    estimates the velocity and its direction.
    
    Note:
        
        - gauss_velocity_field:  returs an array i.e. vectorspace of the form:
                
                V = [[v0_x, v0_y], [v1_x, v1_y], ...]
                
        - snip:  is how much to crop off from each side so we obtain a better fit

*******************************************************'''
    
def where_is_my_Gaussian_maximum(corr1, snip):
    #snip = 35; # that much we snip at each side so we can do a better fit
    corr = corr1[snip:(corr1.shape[0] - snip), snip:(corr1.shape[1] - snip)]
    corr = np.where(corr > 1/math.e, corr, 1/math.e); # irgendwie muesmäh > 1/math_utils.e, wiume aui ussert diäh nan setzt bi dem befäääu!!
    corr = corr - 1/math.e;
    
    xmin, xmax, nx = 0, corr.shape[0], corr.shape[0]
    ymin, ymax, ny = 0, corr.shape[1], corr.shape[1]
    x, y = np.linspace(xmin, xmax, nx), np.linspace(ymin, ymax, ny)
    X, Y = np.meshgrid(x, y)

   
    #TODO Initialisierung??

    guess_prms = [( 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9)] # Initial guesses to the fit parameters 
    bnds = (0,[75, 75, 75, 75, 75, 0.99, 75])#(mu_x, mu_y, sig_x, sig_y, A, rho, '**')
    
    p0 = [p for prms in guess_prms for p in prms] # Flatten the initial guess parameter list.
    
    xdata = np.vstack((X.ravel(), Y.ravel())) # We need to ravel the meshgrids of X, Y points to a pair of 1-D arrays.
    while True:
        try:
            popt, pcov = curve_fit(_Gauss2D, xdata , corr.ravel(), p0, bounds=bnds);
            RMSE = np.sqrt(np.mean((corr.ravel() - Gauss2D(xdata, *popt))**2)/(corr.ravel().shape[0]));
            if(RMSE > 0):
                print ("RMSE : ", RMSE)
            peak = [popt[0] + snip, popt[1] + snip]
            break;
        except RuntimeError:
            print("exception")
            peak = [0, 0];
            break;
    return peak;


def gauss_velocity_field(corrs, snip):
    V = np.zeros((2, corrs.shape[0]));
    origins = np.zeros((2, corrs.shape[0]));
    for i in range(corrs.shape[0]-1):
        origins[:, i] = where_is_my_Gaussian_maximum(corrs[i,:,:], snip);
        V[:, i] = R90(where_is_my_Gaussian_maximum(corrs[i+1,:,:], snip) - origins[:, i]); #We rotate our vectors for 90 degrees because in the final plot the origin of the coordinates will be in the upper left corner, while we computed it as it was at the bottom left.
    return [V,origins]



'''**************** Testing: ***************************
    A few things that need to be defined per hand are:
        + fps
        + Amount of frames 
        + path to the images
******************************************************'''
#==========================================>
def bytescl(array):
     # simple function bytescaling a numpy array
     fac = 255.0/(np.amax(array)-np.amin(array))
     array = (array-np.amin(array)) * fac
     return array
 
def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = np.asarray(Image.open(os.path.join(folder,filename)));
        if img is not None:
            images.append(img)
    return np.asarray(images)   
#==========================================>



fps = 10
path_to_Test_data = r'Dynamics\Test';
I = bytescl(load_images_from_folder(path_to_Test_data));
draw_total_spactime_correlogram_with_velocity_vectors_of_the_peak(I, 300, 4, 3, 100);
draw_my_ROI_velocity_field(I, 50, 50, 10, 4, 3, 4)#(I, ROI_x, ROI_y, fps, pixelsize, maxCorrTime, vectorMagnification)

