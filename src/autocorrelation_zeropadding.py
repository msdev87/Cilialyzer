import numpy

def acorr_zp(signal):
    """
    computes the 1D autocorrelation of the input signal

    The autocovariance is computed by an FFT and with a zero padding
    made in order to double the size of the signal. However the
    returned function is of the same size as the signal.
    """

    # Get a centered version of the signal 
    centered_signal = signal - numpy.mean(signal)

    # Pad the centered signal with zeros, in such a way that the padded
    # signal is twice as big as the input
    zero_padding = numpy.zeros_like(centered_signal)
    padded_signal = numpy.concatenate((centered_signal,
        zero_padding))

    # The Fourier transform is computed using the FFT
    ft_signal = numpy.fft.fft(padded_signal)

    # We get an erroneous autocovariance by taking the inverse transform
    # of the power spectral density
    pseudo_powerSpectralDensity = numpy.abs(ft_signal)**2
    pseudo_autocovariance = numpy.fft.ifft(pseudo_powerSpectralDensity)

    # We repeat the same process (except for centering) on a 'mask'
    # signal, in order to estimate the error made on the previous computation 
    # the mask consists of ones of size N and zeros of size N, 
    # when N denotes the signal length 
    input_domain = numpy.ones_like(centered_signal)
    mask = numpy.concatenate(( input_domain, zero_padding ))
    ft_mask = numpy.fft.fft(mask)
    mask_correction_factors = numpy.fft.ifft(numpy.abs(ft_mask)**2)

    # The "error" made can now be easily corrected by an element-wise division
    autocovariance = pseudo_autocovariance / mask_correction_factors

    autocovariance = autocovariance[0:int(len(signal)/2)]

    # All values of the autocovariance function are pure real numbers, we
    # can get rid of the "complex" representation resulting from the use
    # of the FFT. Also we make sure that we return a signal of the same
    # size as the input signal.

    # The normalization is made by the variance of the signal, which
    # corresponds to the very first value of the autocovariance.

    variance = autocovariance.flat[0]

    # Taking care of the case when the signal has zero variance (when it
    # is constant nearly everywhere), we can then proceed to the
    # normalisation.

    if variance==0.:
        return np.zeros(autocovariance.shape)
    else:
        return (autocovariance / variance)



def acorr2D_zp(signal, centering=True, normalize=True, mask=None):
    """
    computes the 2D autocorrelation of the input signal

    Note that the binary 'mask' indicates the validity of each pixel
    The signal might contain missing values!

    The autocovariance is computed by an FFT and with a zero padding
    made in order to double the size of the signal.
    The returned autocorrelation is not necessarily of the same size as the
    input signal
    """

    # the computation is more safe and simple when we make first sure 
    # that the signal has an even number of elements along both dimensions 
    # along the width and the height
    ni, nj = signal.shape

    # if mask is None (default), we assume that all pixels in signal are valid: 
    if mask is None:
        mask = numpy.ones_like(signal)

    if (ni % 2):
        # if ni mod 2 == 1 then ni is an odd number -> remove one row
        signal = signal[0:ni-1,:]
        mask = mask[0:ni-1,:]
    if (nj % 2):
        signal = signal[:,0:nj-1]
        mask = mask[:,0:nj-1]

    # the signal (and the mask) has now an even number of rows and columns 
    ni, nj = signal.shape

    #print('******************************************************************')
    #print('ni: ',ni,'nj: ',nj)
    #print('******************************************************************')

    # make sure there are no nan-values in signal 
    # (this is just for the calculation of the mean)
    for i in range(ni):
        for j in range(nj):
            if (not mask[i,j]):
                signal[i,j] = 0

    # Get the signal's mean (excluding missing values)
    mean = numpy.sum(numpy.multiply(signal, mask)) / numpy.sum(mask)

    # Missing numbers are now set to the signal's mean
    # This way, missing numbers will then be zero after centering
    for i in range(ni):
        for j in range(nj):
            if (not mask[i,j]):
                signal[i,j] = mean

    # Get a centered version of the signal (if centering is True)
    if (centering):
        centered_signal = numpy.subtract(signal, mean)
    else:
        centered_signal = signal

    # Pad the centered signal with zeros, in such a way that the padded
    # signal is twice as big as the input signal
    padded_signal = numpy.zeros((2*ni, 2*nj))

    # fill in the signal:
    padded_signal[int(ni/2):int(3*ni/2),int(nj/2):int(3*nj/2)] = centered_signal

    # The Fourier transform is computed using the FFT
    fft_signal = numpy.fft.fft2(padded_signal)

    # We get an erroneous autocovariance by taking the inverse transform
    # of the power spectral density 
    # (due to missing values substitued by zero and the zero-padding)

    pseudo_powerSpectralDensity = numpy.multiply(fft_signal,
        numpy.conjugate(fft_signal))
    pseudo_autocovariance = numpy.real( numpy.fft.ifft2(
        pseudo_powerSpectralDensity))

    # We repeat the same process (except for centering) on a masked_signal
    # in order to estimate the error made on the previous computation 
    # the mask_signal has as entries ones (for signal) and zeros (for no signal) 

    masked_signal = numpy.zeros((2*ni, 2*nj))
    masked_signal[int(ni/2):int(3*ni/2),int(nj/2):int(3*nj/2)] = mask

    fft_masked_signal = numpy.fft.fft2(masked_signal)
    mask_correction_factors = numpy.real(numpy.fft.ifft2( numpy.multiply(
        fft_masked_signal, numpy.conjugate(fft_masked_signal))))

    # The "error" made can now be easily corrected by an element-wise division
    autocovariance = pseudo_autocovariance / mask_correction_factors

    if (normalize):
        variance = autocovariance.flat[0]
    else:
        variance = 1.0

    # fft-shift:
    autocovariance = numpy.fft.fftshift(autocovariance)
    autocovariance = autocovariance[int(ni/2):int(3*ni/2),int(nj/2):int(3*nj/2)]

    return (autocovariance / variance)


