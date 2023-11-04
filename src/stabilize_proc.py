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

    maxdiff=0.0 # maximum transformation

    # loop over all images                                           
    for i in range(nimgs):
        # note that only every x-th image is registered (performance)  
        # where x is given by 'skipframe'
        if ((i % skipframe) == 0):
            sr.register(meanimg,array[i,:,:])
        # every other images are transformed as its predecessor(s)
        array_stabilized[i,:,:] = sr.transform(array[i,:,:])

        #img = Image.fromarray(bytescl.bytescl(sr.transform(dummy)).astype(uint8))
        #img.save('dummy'+str(i)+'.png')
        if (numpy.sum(numpy.absolute(dummy - sr.transform(dummy))) > maxdiff):
            maxdiff=numpy.sum(numpy.absolute(dummy - sr.transform(dummy)))


    #TODO check for negative values in stabilized array 



    h = array_stabilized.shape[1]
    w = array_stabilized.shape[2]

    if (h < w):
        croppix = int(maxdiff // h + 5)
    else:
        croppix = int(maxdiff // w + 5)

    #print(array_stabilized.shape[0])

    return (array_stabilized, croppix)

