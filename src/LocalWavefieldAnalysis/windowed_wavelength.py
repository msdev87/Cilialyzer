import numpy
import math
from math_utils import autocorrelation_zeropadding
from scipy.ndimage import gaussian_filter
import cv2

def get_local_wavelength_elongation(array, pixsize):
    # input: dynamically filtered sequence of images (window)
    # return: wavelength

    # input array indices: array[time, row, column]

    nimgs = len(array[:,0,0])
    firstimg = array[0,:,:]
    width, height = firstimg.shape

    # corr: spatial correlogram 
    corr = numpy.zeros((height, width))
    scorr = numpy.zeros((height, width)) # sum (over time) of spatial acorrs

    # 2D arrays, which will be correlated
    frame = numpy.zeros((height, width), dtype=float)
    scorr = numpy.zeros((height, width), dtype=float)

    # as the spatial autocorrelation hardly varies over time
    # we do not have to average over the whole image stack
    # averaging over 10% of all images is a good approximation for overall avg

    nimgs = int(0.1*nimgs)

    for t in range(nimgs): # loop over time

        # autocorrelate
        frame[:,:] = numpy.array(array[t,:,:])
        corr = autocorrelation_zeropadding.acorr2D_zp(frame)
        scorr = numpy.add(scorr, corr)

    scorr = scorr / float(nimgs)
    # get rid of extra dimensions
    scorr = numpy.squeeze(scorr)

    maxy, maxx = numpy.unravel_index(numpy.argmax(scorr, axis=None), scorr.shape)
    miny, minx = numpy.unravel_index(numpy.argmin(scorr, axis=None), scorr.shape)

    # slightly smooth scorr:
    scorr = gaussian_filter(scorr, sigma=1.0, truncate=2.0)

    # ---------------------------------------------------------------------
    # fit ellipse to all values > 1/e
    ellipse_array = numpy.zeros_like(scorr)
    inds = numpy.argwhere(scorr > 1 / math.e)
    rows = inds[:, 0]
    cols = inds[:, 1]
    ellipse_array[rows, cols] = 1
    ellipse_indices = numpy.column_stack(numpy.where(ellipse_array > 0))
    try:
        ellipse = cv2.fitEllipse(ellipse_indices)
        (center_x, center_y), (semi_axis1, semi_axis2), rotation_angle = ellipse

        major_axis = max(semi_axis1, semi_axis2)
        minor_axis = min(semi_axis1, semi_axis2)

        cbp_elongation = major_axis / minor_axis
    except:
        cbp_elongation = -1.0
    # --------------------------------------------------------------------------
    # calculate the 2D distance matrix 'distmat' (in pixels)
    distmat = numpy.zeros(scorr.shape)

    for y in range(scorr.shape[0]):
        for x in range(scorr.shape[1]):
            dx = x - maxx
            dy = y - maxy
            distmat[y, x] = math.sqrt(dx ** 2 + dy ** 2)

    square_arr = scorr[miny, minx]  # square array around minimum position
    minimum_value = scorr[miny, minx]
    threshold = 1.0 / math.e * minimum_value
    s = 1
    while (numpy.all(square_arr < threshold)):
        # repeat while all elements in square around min are > minimum val
        s = s + 2  # increase size of square array (1x1, 3x3, 5x5, ...)
        square_arr = scorr[miny - s:miny + s + 1, minx - s:minx + s + 1]

    # positions within scorr
    x = numpy.linspace(-int(s / 2), int(s / 2), s) + minx
    y = numpy.linspace(-int(s / 2), int(s / 2), s) + miny
    xx, yy = numpy.meshgrid(x, y)

    # determine center of mass (cm) within square_arr

    try:
        x_cm, y_cm = 0.0, 0.0
        weight_total = 0.0  # sum of weights
        for i in range(s):
            for j in range(s):
                x = int(xx[i, j])
                y = int(yy[i, j])
                # print('x: ',x,' y: ',y)
                if scorr[y, x] < 0:
                    x_cm = x_cm + abs(scorr[y, x]) * x
                    y_cm = y_cm + abs(scorr[y, x]) * y
                    weight_total += abs(scorr[y, x])
    except:
        x_cm = minx
        y_cm = miny


    try:
        x_cm = x_cm / weight_total
        y_cm = y_cm / weight_total
    except:
        x_cm = minx
        y_cm = miny

    # x_cm and y_cm can now be defined as a more exact measure for the
    # position of the minimum
    minx = x_cm
    miny = y_cm

    # Determine wavelength
    dx = maxx - minx
    dy = maxy - miny
    wavelength_pix = 2 * math.sqrt(dx ** 2 + dy ** 2)
    wavelength = wavelength_pix * pixsize * 0.001

    return wavelength, cbp_elongation
