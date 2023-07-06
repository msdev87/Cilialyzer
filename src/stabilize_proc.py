import numpy
from pystackreg import StackReg

def subproc(args):

    # this function defines processes, which are ran in parallel

    meanimg = args[0]
    array = args[1]
    #frameskip = args[2]

    nimgs = array.shape[0]
    #print('nimgs: ',nimgs)

    array_stabilized = numpy.copy(array)

    sr = StackReg(StackReg.RIGID_BODY)

    # loop over all images                                           
    for i in range(nimgs):
        # note that only every second image is registered (performance)   
        if ((i % 1) == 0):
            sr.register(meanimg,array[i,:,:])
        # therefore, every second image is transformed as its predecessor
        array_stabilized[i,:,:] = sr.transform(array[i,:,:])

    #print(array_stabilized.shape[0])

    return array_stabilized

