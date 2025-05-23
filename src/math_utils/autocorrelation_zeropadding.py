import numpy

def acorr_zp(signal):
    """
    Computes the one-dimensional autocorrelation of an input signal

    The autocovariance is computed by making use of the  Wiener Khinchin theorem
    A zero padding of the size of the input signal is added. The
    returned correlation function has the same size as the original input signal

    Input:
    signal: signal of interest, list or numpy array of measured values

    Output:
    autocorrelation function of input signal (of same length as input signal)
    """

    # Get a centered version of the signal 
    centered_signal = signal - numpy.mean(signal)

    # Pad the centered signal with zeros, in such a way that the padded
    # signal is twice as big as the input
    zero_padding = numpy.zeros_like(centered_signal)
    padded_signal = numpy.concatenate((centered_signal, zero_padding))

    # The Fourier transform is computed using the FFT
    ft_signal = numpy.fft.fft(padded_signal)

    # We get an 'erroneous' autocovariance by taking the inverse transform
    # of the power spectral density
    pseudo_powerSpectralDensity = numpy.abs(ft_signal)**2
    pseudo_autocovariance = numpy.fft.ifft(pseudo_powerSpectralDensity)

    # We repeat the same process (except for centering) on a 'mask'
    # signal, in order to estimate the error made on the previous computation 
    # the mask consists of ones of size N and zeros of size N, 
    # where N denotes the length of the input signal
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
    # size as the input signal

    # The normalization is made by diving by the variance of the signal, which
    # corresponds to the very first value of the autocovariance
    variance = autocovariance.flat[0]
    #if (normalize):
    #    variance = numpy.sum(numpy.multiply(centered_signal,centered_signal)) / numpy.sum(mask)
    #else:
    #    variance = 1.0

    # Taking care of the case when the signal has zero variance (when it
    # is constant nearly everywhere), we can then proceed to the
    # normalisation:

    if variance==0.:
        return np.zeros(autocovariance.shape)
    else:
        return (autocovariance / variance)


def acorr2D_zp(signal, centering=True, normalize=True, mask=None):
    """
    Computes the 2D autocorrelation of a two-dimensional input array

    Note that the binary mask indicates the validity of each pixel
    The signal may therefore contain missing values

    The autocovariance is computed by an FFT and with a zero padding at the edges

    The returned autocorrelation is of the same size as the input signal

    Input:
    signal: two-dimensional array
    mask: two-dim array (same size as signal) indicating validity of each pixel

    Output:
    Autocorrelation of input signal
    """

    # Get the number of rows and columns
    ni, nj = signal.shape

    # If mask is None (default), we assume that all pixels in signal are valid:
    if mask is None:
        mask = numpy.ones_like(signal) # 1 means valid

    # Make sure there are no NaN-values in signal
    # (this is only for the calculation of the mean)
    signal[~numpy.array(mask, dtype=bool)] = 0.0

    # Get the signal's mean (excluding missing values)
    mean = numpy.sum(numpy.multiply(signal, mask)) / numpy.sum(mask)

    # Missing numbers are now set to the signal's mean
    # This way, missing numbers will then be zero after centering
    signal[~numpy.array(mask, dtype=bool)] = mean

    # Get a centered version of the signal (if centering is True)
    if centering:
        centered_signal = numpy.subtract(signal, mean)
    else:
        centered_signal = signal

    # Pad the centered signal with zeros, in such a way that the padded
    # signal is twice as big as the input signal
    padded_signal = numpy.zeros((2*ni, 2*nj))

    # Note: padded signal has now an even number of values along row and column

    # Fill in the signal:
    padded_signal[0:ni,0:nj] = centered_signal

    # The Fourier transform is computed using the FFT (Wiener Khinchin theorem)
    fft_signal = numpy.fft.fft2(padded_signal)

    # We get an erroneous autocovariance by taking the inverse transform
    # of the power spectral density 
    # (due to missing values substituted by zero and the zero-padding)
    pseudo_power_spectral_density = numpy.abs(numpy.multiply(fft_signal,
        numpy.conjugate(fft_signal)))
    pseudo_autocovariance = numpy.real( numpy.fft.ifft2(
        pseudo_power_spectral_density))

    # We repeat the same process (except for centering) on a masked_signal
    # in order to estimate the error made on the previous computation 
    # the mask_signal has as entries ones (for signal) and zeros (for no signal) 
    # Note that the mask has also to be placed in the center of the padded array
    # This mask can then be used to correctly normalize
    # (i.e. to adjust the normalization by counting overlapping valid pixels only)
    masked_signal = numpy.zeros((2*ni, 2*nj))
    masked_signal[0:ni,0:nj] = mask

    fft_masked_signal = numpy.fft.fft2(masked_signal)
    mask_correction_factors = numpy.abs(numpy.fft.ifft2( numpy.multiply(
        fft_masked_signal, numpy.conjugate(fft_masked_signal))))

    # Avoid division by zero
    mask_correction_factors = numpy.where(mask_correction_factors == 0, 1,
                                       mask_correction_factors)

    # The "error" made can now be easily corrected by an element-wise division
    autocovariance = pseudo_autocovariance / mask_correction_factors

    if (normalize):
        variance = numpy.sum(numpy.multiply(centered_signal,centered_signal)) / numpy.sum(mask)
    else:
        variance = 1.0

    # fft-shift:
    autocovariance = numpy.fft.fftshift(autocovariance)

    # The zero-shift is now located in the middle of the array
    # If the length of the array is 2*ni, the zero shift corresponds to index ni
    # (first ni negative shifts, then shift of zero, finally ni-1 positive shifts)
    autocovariance = autocovariance[int(ni/2):int(3*ni/2),int(nj/2):int(3*nj/2)]

    return (autocovariance / variance)
