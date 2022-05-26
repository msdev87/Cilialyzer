import numpy
import crosscorrelation_zp
import PIL
import matplotlib.pyplot as plt
import bytescl

def stcorr(sequence, maxtimeshift=10):
    """
    Returns the space-time correlation of an input image sequence

    Note that the computatoin takes care of the wrap-around artifact.
    In the spatial domain, the Wiener-Khinchin theorem is used to comptue the
    cross-correlation between two images. Zero-padding (and its subsequent)
    correction is applied in the spatial domain. In the time-domain, the
    time-shift is choosen explicitly.

        Parameters:
            sequence: holds the PIL images.
                sequence[0] = first image
                sequence[1] = second image and so on...

        Returns:
            stcorr: list of PIL images holding the space-time correlogram
    """

    stcorrgram = []

    nimgs = len(sequence)
    firstimg = sequence[0]
    width, height = firstimg.size

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

            img1[0:height,0:width] = numpy.array(sequence[t])
            img2[0:height,0:width] = numpy.array(sequence[t+deltat])

            # compute spatial cross-correlation and sum up over all time steps
            cc = crosscorrelation_zp.ccorr2D_zp(img1, img2)
            scc = scc + cc

        scc = (1.0 / (nimgs-maxtimeshift)) * scc # average 


        # at this stage 'scc' ranges from -1 to +1 
        scc = numpy.absolute(scc)
        scc = bytescl.bytescl(scc)

        # convert scc to a PIL image and append to space-time correlogram
        stcorrgram.append(PIL.Image.fromarray(numpy.uint8(scc)))

    return stcorrgram

