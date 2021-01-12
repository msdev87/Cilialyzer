import numpy
import math
from PIL import Image

# punkt springt zwei grad pro frame
# radius = 100 pixel

rows = 300
cols = 300
nt = 90

array = numpy.zeros((rows,cols,nt),dtype=numpy.uint8)

array[:,:,:] = 180

# center 
cx = array.shape[1] / 2
cy = array.shape[0] / 2

radius = 100

for i in range(nt):

    phi = i / nt * math.pi # angle in radians  

    rx = radius * math.cos(phi)
    ry = radius * math.sin(phi)


    array[int(cy+ry)-2:int(cy+ry)+2,int(cx+rx)-2:int(cx+rx)+2,i] = 20

    img = array[:,:,i]


    # save img
    fname = 'test' + str(i+10) + '.png'

    im = Image.fromarray(img)
    im.save(fname)


