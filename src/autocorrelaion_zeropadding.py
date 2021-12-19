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


