from numpy import copy
from pystackreg import StackReg
from numpy import zeros
from PIL import Image
import bytescl
from numpy import uint8
import numpy

def subproc(args):

    # this function defines processes, which are ran in parallel

    meanimg = args[0]
    array = args[1]
    skipframe = args[2] # number of frames to be skipped

    nimgs = array.shape[0]
    #print('nimgs: ',nimgs)

    array_stabilized = copy(array)

    border = 50
    dummy = zeros((array.shape[1]+border,array.shape[2]+border))
    dummy[border//2:array.shape[1]+border//2,border//2:array.shape[2]+border//2] = 1

    sr = StackReg(StackReg.RIGID_BODY)

    maxdiff=0.0 # maximum difference between transformed images

    # Loop over all images                                           
    for i in range(nimgs):
        # Note that only every x-th image is registered (computation time)  
        # where x is given by 'skipframe+1'
        if ((i % (skipframe+1)) == 0):
            sr.register(meanimg, array[i,:,:])
        # every other images are transformed as its predecessor(s)
        array_stabilized[i,:,:] = sr.transform(array[i,:,:])

        # img = Image.fromarray(bytescl.bytescl(sr.transform(dummy)).astype(uint8))
        # img.save('dummy'+str(i)+'.png')
        if (numpy.sum(numpy.absolute(dummy - sr.transform(dummy))) > maxdiff):
            maxdiff=numpy.sum(numpy.absolute(dummy - sr.transform(dummy)))

    # Check for negative values in stabilized array and set them to mean
    array_stabilized[numpy.argwhere(array_stabilized < 0)] = 0

    h = array_stabilized.shape[1]
    w = array_stabilized.shape[2]

    if (h < w):
        croppix = int(maxdiff // h + 5)
    else:
        croppix = int(maxdiff // w + 5)

    # Reduce the intensity of highly scattering structures by slightly 
    # croping distribution of the intensity (0.1% from dark and bright side)
    cut1 = numpy.percentile(array_stabilized, 0.05)
    cut2 = numpy.percentile(array_stabilized, 99.95)
    array_stabilized[array_stabilized < cut1] = cut1
    array_stabilized[array_stabilized > cut2] = cut2

    return (array_stabilized, croppix)
