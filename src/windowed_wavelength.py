import numpy
import math

def get_wavelength(array, pixsize):
    # input: dynamically filtered sequence of images (window)
    # return: wavelength

    # input array indices: array[time, row, column]

    nimgs = len(array[:,0,0])
    firstimg = array[0,:,:]
    width, height = firstimg.shape

    # corr: spatial correlogram 
    corr = numpy.zeros((height,width))
    scorr = numpy.zeros((height,width)) # sum (over time) of spatial acorrs 

    # 2D arrays, which will be correlated
    img1 = numpy.zeros((height, width), dtype=float)
    img2 = numpy.zeros((height, width), dtype=float)

    # as the spatial autocorrelation hardly varies over time
    # we do not have to average over the whole image stack
    # consequently, the average over 10% of all images is a good approximation 
    # for the overall average 

    nimgs = int(0.1*nimgs)

    for t in range(nimgs): # loop over time

        # pair of images, which we correlate 
        img1[:,:] = numpy.array(array[t,:,:])
        img2[:,:] = numpy.array(array[t,:,:])

        # calculate the correlation between img1 and img2
	# given by the inverse FFT of the product: FFT(img1)*FFT(img2)

        fft1 = numpy.fft.fft2(img1)
        fft2 = numpy.fft.fft2(img2)

        prod = numpy.multiply(fft1,numpy.conjugate(fft2)) / float(width*height)
        ifft = numpy.real(numpy.fft.ifft2(prod))

        stdv1 = numpy.std(img1)
        stdv2 = numpy.std(img2)

        corr = numpy.subtract(ifft,(numpy.mean(img1) * numpy.mean(img2)))
        corr = corr / (stdv1 * stdv2)

        scorr = numpy.add(scorr,corr)

    scorr = scorr / float(nimgs)
    scorr = numpy.fft.fftshift(scorr)

    scorr = numpy.squeeze(scorr) # get rid of extra dimensions

    nrows = len(scorr[:,0]) # number of rows
    ncols = len(scorr[0,:]) # number of columns


    # get the location of the extrema in scorr (in pixel coordinates) 
    maxy, maxx = numpy.unravel_index(numpy.argmax(scorr,axis=None),scorr.shape)
    miny, minx = numpy.unravel_index(numpy.argmin(scorr,axis=None),scorr.shape)




    # calculate the 2D distance matrix 'distmat' (in pixels)        
    distmat = numpy.zeros(scorr.shape)

    for y in range(scorr.shape[0]):
        for x in range(scorr.shape[1]):
            dx = x-maxx
            dy = y-maxy
            distmat[y,x] = math.sqrt(dx**2+dy**2)

    # the wavelength is defined as twice the distance between the
    # maximum and the minimum!                                   

    # wavelength in pixels:                   
    dx = maxx-minx
    dy = maxy-miny
    wavelength_pix=2*math.sqrt(dx**2+dy**2)


    """
    # correlation profile along the line (x0,y0) -- (x1,y1) 
    x0,y0 = maxx-(4*dx),maxy-(4*dy)
    x1,y1 = maxx+(4*dx),maxy+(4*dy)

    # note that:
    # sqrt( (x1-x0)^2 + (y1-y0)^2 ) = 4 * wavelength

    # the line needs to be restricted by the size of scorr (nrows, ncols) 
    # (in the case of long wavelengths or small images)  
    if (x0 > x1):
        if (x0 > ncols-1):
            x0 = ncols-1
        if (x1 < 0):
            x1 = 0
    else:
        if (x0 < 0):
            x0 = 0
        if (x1 > ncols-1):
            x1 = ncols-1

    if (y0 > y1):
        if (y0 > nrows-1):
            y0 = nrows-1
        if (y1 < 0):
            y1 = 0
    else:
        if (y0 < 0):
            y0 = 0
        if (y1 > nrows-1):
            y1 = nrows-1

    """
    #fac = 0.001*pixsize

    # get profile
    #num = 1000
    #print('x0,x1,y0,y1',x0,x1,y0,y1)
    #x, y = numpy.linspace(x0, x1, num), numpy.linspace(y0, y1, num)
    #scorr_profile = scorr[y.astype(numpy.int), x.astype(numpy.int)]
    #distmat_profile= distmat[y.astype(numpy.int), x.astype(numpy.int)]

    # note that the spacing corresponds now to 4*wavelength/num

    # distmat_profile determines the x-axis in the profile plot 
    # half of all values need to be negative
    #dm = numpy.argmin(distmat_profile) # dm = location of correlation max.  

    #distmat_profile[0:dm+1] = -distmat_profile[0:dm+1]

    #distmat_profile = distmat_profile * pixsize * 0.001
    wavelength = wavelength_pix * pixsize * 0.001

    return wavelength

















