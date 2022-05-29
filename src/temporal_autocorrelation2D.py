import numpy
import autocorrelation_zeropadding

def avg_tacorr(args):
    """
    This function returns the average temporal autocorrelation

        Parameters:
            array:  assumes dimensions t,i,j and performs the autocorrelation
                    along the time-axis 't'
            mask:   boolean, indicates which pixels i,j should be considered

        Returns:
            the average temporal autoccorelation (along t, averaged over i,j)
    """

    array = args[0]
    mask = args[1]

    (nt, ni, nj) = numpy.shape(array)

    print('----------------------------')
    print(nt, ni, nj)

    # initialize meanacorr
    meanacorr = autocorrelation_zeropadding.acorr_zp(array[:,0,0])
    meanacorr[:] = 0.0

    counter = 0

    for i in range(ni):
        for j in range(nj):

            if (mask[i,j]):
                timeseries = array[:,i,j]
                acorr = autocorrelation_zeropadding.acorr_zp(timeseries)
                meanacorr = numpy.add(meanacorr, acorr)
                counter = counter + 1

    meanacorr = meanacorr / float(counter)

    return meanacorr
