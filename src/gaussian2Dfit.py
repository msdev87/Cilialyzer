import numpy as np
from scipy.optimize import curve_fit
import math

def gaussian(x, y, mx, my, sx, sy, rho):

    #print('----------------------')
    #print('mx:   ', mx)
    #print('my:   ', my)
    #print('sx:   ', sx)
    #print('sy:   ', sy)
    #print('rho:  ', rho)
    #print('----------------------')

    A = 1.0 / (2 * math.pi * sx * sy * math.sqrt(1.0 - rho**2))

    return A * np.exp((-0.5/(1-rho**2)) * ( ((x-mx)/sx)**2 - (2*rho*(x-mx)*(y-my))/(sx*sy) + ((y-my)/sy)**2) )

def _gaussian(M, *args):
    x, y = M
    arr = np.zeros(x.shape)
    arr = gaussian(x, y, *args)
    return arr


def fit(array, sigma):

    Z = np.absolute(array)

    xmin, xmax, nx = 0, array.shape[1]-1, array.shape[1]
    ymin, ymax, ny = 0, array.shape[0]-1, array.shape[0]
    x, y = np.linspace(xmin, xmax, nx), np.linspace(ymin, ymax, ny)
    X, Y = np.meshgrid(x, y)

    # initial guesses for the fit parameters
    fitpars0 = [0.5*xmax, 0.5*ymax, 3., 3., 0.]

    fitpars_range = ([0.,0.,0.,0.,-1.],[xmax,ymax,xmax,ymax,1.])

    # ravel the meshgrids X, Y to a pair of 1-D arrays
    xdata = np.vstack((X.ravel(), Y.ravel()))

    # Do the fit, using our custom _gaussian function which understands our
    # flattened (ravelled) ordering of the data points
    fitpars, pcovs = curve_fit(_gaussian, xdata, Z.ravel(), fitpars0, bounds = fitpars_range, sigma=sigma.ravel())

    # from the fit, we are only interested in the position and the height 
    # of the peak:  

    posx = fitpars[0]
    posy = fitpars[1]
    peakheightfit = gaussian(posx, posy, fitpars[0], fitpars[1], fitpars[2],
        fitpars[3], fitpars[4])


    # posx and posy are not integers 
    # lets us bilinearly interpolate Z to approximate Z(posx,posy)
    # remains to be done..

    return (posx, posy, peakheightfit)




