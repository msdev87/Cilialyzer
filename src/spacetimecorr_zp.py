import numpy
import crosscorrelation_zp
import PIL
import matplotlib.pyplot as plt
import bytescl

def stcorr(array, maxtimeshift=10):
    """
    Returns the space-time correlation of an input image sequence

    Note that the computation takes care of the wrap-around artifact.
    In the spatial domain, the Wiener-Khinchin theorem is used to compute the
    cross-correlation between two images. Zero-padding (and its subsequent)
    correction is applied in the spatial domain. In the time-domain, the
    time-shift is chosen explicitly.

        Parameters:
            array: holds the numpy-array of images (time, row, column)

        Returns:
            stcorr: list holding the space-time cross-correlograms
    """

    stcorrgram = []

    nimgs = array.shape[0]
    width, height = array.shape[2], array.shape[1]

    # img1 and img2 are the two images, which get cross-correlated
    img1 = numpy.zeros((height,width))
    img2 = numpy.zeros((height,width))

    # initialize scc
    img1[:,:] = 1
    img2[:,:] = 1
    scc = crosscorrelation_zp.ccorr2D_zp(img1, img2)
    scc[:,:] = 0.0

    # loop over time and timeshifts 
    for deltat in range(maxtimeshift):

        for t in range(nimgs-maxtimeshift):

            img1[0:height,0:width] = numpy.array(array[t,:,:])
            img2[0:height,0:width] = numpy.array(array[t+deltat,:,:])

            # compute spatial cross-correlation and sum up over all time steps
            cc = crosscorrelation_zp.ccorr2D_zp(img1, img2)
            scc = scc + cc

        scc = (1.0 / (nimgs-maxtimeshift)) * scc # average 


        # at this stage 'scc' ranges from -1 to +1 
        scc = numpy.absolute(scc)
        scc = bytescl.bytescl(scc)

        # convert scc to a PIL image and append to space-time correlogram
        #stcorrgram.append(PIL.Image.fromarray(numpy.uint8(scc)))
        stcorrgram.append(scc)

    return stcorrgram

