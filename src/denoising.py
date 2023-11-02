import numpy
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageTk, ImageEnhance
from bytescl import bytescl
"""
Input: 3D array (stack of images)
Output: denoised image sequence
"""

def denoise(PILseq):

    firstimg = PILseq[0] # first image of roi sequence  
    width, height = firstimg.size # dimension of images 
    nimgs = len(PILseq) # number of images  

    # create numpy array 'array' 
    array = numpy.zeros((int(nimgs),int(height),int(width)))

    for i in range(nimgs):
        array[i,:,:] = numpy.array(PILseq[i])
    (nt,ni,nj) = numpy.shape(array)

    """
    # Gaussian blur in space
    for i in range(nimgs):
        array[i,:,:] = gaussian_filter(array[i,:,:],sigma=0.5)

    # Gaussian blur in time
    for w in range(width):
        for h in range(height):
            array[:,h,w] = gaussian_filter(array[:,h,w],sigma=0.5)
            array = numpy.uint8(bytescl(array))
    """

    #array = gaussian_filter(array,sigma=0.5)
    array = gaussian_filter(array,sigma=0.5)

    array = numpy.uint8(bytescl(array))

    for i in range(nimgs):
        img = Image.fromarray(array[i,:,:])
        PILseq[i] = img


