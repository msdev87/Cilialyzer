import numpy
from math_utils import crosscorrelation_zp

def stcorr(array, maxtimeshift=3):
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

    array = numpy.array(array, dtype=numpy.float32)

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

    return stcorrgram

