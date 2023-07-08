import numpy
from pystackreg import StackReg

def subproc(args):

    # this function defines processes, which are ran in parallel

    meanimg = args[0]
    array = args[1]
    skipframe = args[2] # number of frames to be skipped

    nimgs = array.shape[0]
    #print('nimgs: ',nimgs)

    array_stabilized = numpy.copy(array)

    sr = StackReg(StackReg.RIGID_BODY)

    # loop over all images                                           
    for i in range(nimgs):
        # note that only every x-th image is registered (performance)  
        # where x is given by 'skipframe'
        if ((i % skipframe) == 0):
            sr.register(meanimg,array[i,:,:])
        # every other images are transformed as its predecessor(s)
        array_stabilized[i,:,:] = sr.transform(array[i,:,:])

    #print(array_stabilized.shape[0])

    return array_stabilized

