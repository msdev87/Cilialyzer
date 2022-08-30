import numpy
import matplotlib.pyplot as plt

cbf=numpy.loadtxt('win_meancbf.dat')

wspeed = numpy.loadtxt('win_wavespeed.dat')

wlength = numpy.loadtxt('win_wavelength.dat')
#wangle =  numpy.loadtxt('win_waveangle.dat')



prod = wlength * cbf

print(cbf)
print(wlength)

#plt.scatter(cbf, wspeed)
#plt.title('wspeed vs cbf')
#plt.show()

#plt.scatter(wangle, wspeed)
#plt.title('wspeed vs wangle')

plt.scatter(prod, wspeed)

plt.show()





