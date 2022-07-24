import numpy
import matplotlib.pyplot as plt

cbf=numpy.loadtxt('win_meancbf.dat')

wspeed = numpy.loadtxt('win_wavespeed.dat')

wangle =  numpy.loadtxt('win_waveangle.dat')


#plt.scatter(cbf, wspeed)
#plt.title('wspeed vs cbf')
#plt.show()

plt.scatter(wangle, wspeed)
plt.title('wspeed vs wangle')
plt.show()





