from autocorrelation_zeropadding import acorr_zp as autocorr
import numpy as np
import matplotlib.pyplot as plt


# plot a sinusoidal signal, determine its autocorr and plot the latter

# Parameters for the sinusoidal signal
frequency = 5      # Frequency in Hz
amplitude = 1      # Amplitude of the signal
sampling_rate = 100 # Samples per second
duration = 2       # Duration in seconds

# Generate the time array
t = np.arange(0, duration, 1/sampling_rate)

# Generate the sinusoidal signal
signal = amplitude * np.sin(2 * np.pi * frequency * t)

# Plotting the signal
fig, axes = plt.subplots(2, 2, figsize=(10, 8))  # 2 rows, 2 columns

axes[0,0].plot(signal)
#plt.show(block=False)

# calculate the autocorr of the sinusoidal
acorr_signal = autocorr(signal)

axes[0,1].plot(acorr_signal)
plt.show()
