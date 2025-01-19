import numpy
from math import sqrt

def ccorr2D_zp(signal1, signal2, mask=None, normalize=True, centering=True):
    """
    Computes the 2D cross-correlation of the input signals

    Note that the binary 'mask' indicates the validity of each pixel
    (the validity-mask is the same for signal1 and signal2)

    The crosscovariance is computed by an FFT and with a zero padding
    made in order to double the size of the input signals.
    The returned cross-correlation is not necessarily of the same size as the
    input signals
    """

    ni, nj = signal1.shape

    # If mask is None (default), we assume that all pixels in signal are valid:
    if mask is None:
        mask = numpy.ones_like(signal1)

    # Make sure there are no NaN-values (just for the calculation of the means)
    # if mask[i,j] = False, then set signal[j,j] = 0
    signal1[~numpy.array(mask,dtype=bool)] = 0.0
    signal2[~numpy.array(mask,dtype=bool)] = 0.0

    ni, nj = signal1.shape

    # Get the signals' means (excluding missing values)
    mean1 = numpy.sum(numpy.multiply(signal1, mask)) / numpy.sum(mask)
    mean2 = numpy.sum(numpy.multiply(signal2, mask)) / numpy.sum(mask)

    # Missing numbers are now set to the signals' mean
    # This way, missing numbers will later be zero after centering signals
    signal1[~numpy.array(mask, dtype=bool)] = mean1
    signal2[~numpy.array(mask, dtype=bool)] = mean2

    # Get a centered version of the signals
    if (centering):
        centered_signal1 = numpy.subtract(signal1, mean1)
        centered_signal2 = numpy.subtract(signal2, mean2)
    else:
        centered_signal1 = signal1
        centered_signal2 = signal2

    # Pad the centered signal with zeros, in such a way that the padded
    # signal is twice as big as the input signal
    padded_signal1 = numpy.zeros((2*ni, 2*nj))
    padded_signal2 = numpy.zeros((2*ni, 2*nj))

    # Fill in the signal:
    padded_signal1[0:ni, 0:nj] = centered_signal1
    padded_signal2[0:ni, 0:nj] = centered_signal2

    # The Fourier transform is computed using the FFT
    fft_signal1 = numpy.fft.fft2(padded_signal1)
    fft_signal2 = numpy.fft.fft2(padded_signal2)

    # We get an erroneous autocovariance by taking the inverse transform
    # of the power spectral density 
    # (due to missing values substitued by zero and the zero-padding)

    pseudo_powerSpectralDensity = numpy.abs(numpy.multiply(fft_signal1,
        numpy.conjugate(fft_signal2)))
    pseudo_crosscovariance = numpy.real(numpy.fft.ifft2(
        pseudo_powerSpectralDensity))

    # We repeat the same process (except for centering) on a masked_signal
    # in order to estimate the error made on the previous computation 
    # the mask_signal has as entries ones (for signal) and zeros (for no signal)
    masked_signal = numpy.zeros((2*ni, 2*nj))
    masked_signal[0:ni,0:nj] = mask

    fft_masked_signal = numpy.fft.fft2(masked_signal)
    mask_correction_factors = numpy.abs(numpy.fft.ifft2( numpy.multiply(
        fft_masked_signal, numpy.conjugate(fft_masked_signal))))

    # The "error" made can now be easily corrected by an element-wise division
    crosscovariance = pseudo_crosscovariance / mask_correction_factors

    # fft-shift:
    crosscovariance = numpy.fft.fftshift(crosscovariance)
    crosscovariance = crosscovariance[int(ni/2):int(3*ni/2),int(nj/2):int(3*nj/2)]

    if normalize:
        var1 = numpy.var(signal1)
        var2 = numpy.var(signal2)
    else:
        var1 = 1.0
        var2 = 1.0

    crosscorrelation = crosscovariance / (sqrt(var1 * var2))

    return crosscorrelation

