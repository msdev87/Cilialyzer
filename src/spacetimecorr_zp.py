import numpy
import crosscorrelation_zp
import PIL
import matplotlib.pyplot as plt
import bytescl
import sys

def stcorr(array, maxtimeshift=15):
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

    nimgs = array.shape[0]
    width, height = array.shape[2], array.shape[1]

    stcorrgram = []

    # img1 and img2 are the two images, which get cross-correlated
    img1 = numpy.zeros((height,width))
    img2 = numpy.zeros((height,width))

    # initialize scc
    img1[:,:] = 1
    img2[:,:] = 1
    scc = crosscorrelation_zp.ccorr2D_zp(img1, img2, centering=False)
    scc[:,:] = 0.0

    # loop over timeshifts and time
    for deltat in range(maxtimeshift):

        scc[:,:] = 0.0
        for t in range(nimgs-maxtimeshift):

            img1 = numpy.squeeze(numpy.array(array[t,:,:]))
            img2 = numpy.squeeze(numpy.array(array[t+deltat,:,:]))

            # compute spatial cross-correlation and sum up over all time steps
            cc = crosscorrelation_zp.ccorr2D_zp(img1, img2, centering=True)

            # as the second image gets shifted in space and time simultaneously
            # we need to flip its orientation in x and y!
            cc = numpy.flip(cc)

            scc = scc + cc

        scc = (1.0 / (nimgs-maxtimeshift)) * scc # average 

        # at this stage 'scc' ranges from -1 to +1
        # scc = numpy.absolute(scc)
        # scc = bytescl.bytescl(scc)
        # convert scc to a PIL image and append to space-time correlogram
        # stcorrgram.append(PIL.Image.fromarray(numpy.uint8(scc)))

        # the returned scc (spatial cross-corr) ranges from -1 to +1 
        stcorrgram.append(numpy.copy(scc))


    stcorrgram = numpy.array(stcorrgram)
    print('shape of stcorrgram: ', stcorrgram.shape)

    print('-------------------------------------------------')
    print('within spacetimecorr_zp')
    print('max stcorr[0,:,:]: ', numpy.max(stcorrgram[0, :, :]))
    print('min stcorr[0,:,:]: ', numpy.min(stcorrgram[0, :, :]))
    print('max stcorr[1,:,:]: ', numpy.max(stcorrgram[1, :, :]))
    print('min stcorr[1,:,:]: ', numpy.min(stcorrgram[1, :, :]))
    print('-------------------------------------------------')

    return stcorrgram

