import numpy
def bytescl(array):
    # simple function bytescaling a numpy array 
    fac = 254.99/(numpy.amax(array)-numpy.amin(array))
    array = (array-numpy.amin(array)) * fac
    return array
