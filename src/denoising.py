import numpy

"""
Input: 3D array (stack of images)

bandpass filter in all 3 dimensions (space and time)

Output: denoised image sequence
"""

def denoise(PILseq, fps, pixsize):

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images  

    # create numpy array 'array' 
    array = numpy.zeros((int(nimgs),int(height),int(width)))
    for i in range(nimgs):
        array[i,:,:] = numpy.array(PILseq[i])
    (nt,ni,nj) = numpy.shape(array)

    filtering = numpy.zeros((nt,ni,nj))

    # define the bandpass filter 'filtering'

    # space-domaing filtering: get rid of Nyquist frequency in kx and ky




