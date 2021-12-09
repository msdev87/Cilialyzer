import numpy
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import math

array = numpy.loadtxt('scorr.dat')

absarray = numpy.absolute(array)


# plot colors of scorr 
ax = plt.subplot()
img = ax.imshow(absarray, cmap='bwr',vmin=-1,vmax=1)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(img, cax=cax)
#plt.title('mean spatial autocorrelation')#,loc='left')
#plt.imsave('msautocorr_abs.png', 
plt.show()



# plot the profile of the correlogram along the line                    
# connecting the two minima (and the global maximum)                    

# get the location of the extrema in scorr (in pixel coordinates)       
maxy, maxx = numpy.unravel_index(numpy.argmax(array,axis=None),array.shape)
miny, minx = numpy.unravel_index(numpy.argmin(array,axis=None),array.shape)

# get the profile along the line, which is given by the connection      
# of the maximum and minimum coordinates                                

# calculate the 2D distance matrix 'distmat' (in pixels)                
distmat = numpy.zeros(array.shape)

for y in range(array.shape[0]):
    for x in range(array.shape[1]):
        dx = x-maxx
        dy = y-maxy
        distmat[y,x] = math.sqrt(dx**2+dy**2)

# the wavelength is defined as twice the distance between the           
# maximum and the minimum!                                              

# wavelength in pixels:                                                 
dx = maxx-minx
dy = maxy-miny
wavelength_pix=2*math.sqrt(dx**2+dy**2)

# plot the correlation profile along the line (x0,y0) -- (x1,y1)        
x0,y0 = maxx-(30*dx),maxy-(30*dy)
x1,y1 = maxx+(30*dx),maxy+(30*dy)


nrows = len(array[:,0]) # number of rows                
ncols = len(array[0,:]) # number of columns             


# the line needs to be restricted by the size of scorr (nrows, ncols) 
# (in the case of long wavelengths or small images)                   
if (x0 > x1):
    if (x0 > ncols-1):
        x0 = ncols-1
    if (x1 < 0):
        x1 = 0
else:
    if (x0 < 0):
        x0 = 0
    if (x1 > ncols-1):
        x1 = ncols-1

if (y0 > y1):
    if (y0 > nrows-1):
        y0 = nrows-1
    if (y1 < 0):
        y1 = 0
else:
    if (y0 < 0):
        y0 = 0
    if (y1 > nrows-1):
        y1 = nrows-1


# plot mean spatial autocorrelation with profile line 

ax = plt.subplot()
img = ax.imshow(array, cmap='bwr',vmin=-1,vmax=1)
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(img, cax=cax)
#plt.title('mean spatial autocorrelation (absolute values',loc='right')
ax.plot([x0, x1], [y0, y1], color="black", linewidth=1)
plt.show()



# get profile along line!! 

num = 2000
print('x0,x1,y0,y1',x0,x1,y0,y1)
x, y = numpy.linspace(x0, x1, num), numpy.linspace(y0, y1, num)
scorr_profile = array[y.astype(numpy.int), x.astype(numpy.int)]
distmat_profile= distmat[y.astype(numpy.int), x.astype(numpy.int)]


# distmat_profile determines the x-axis in the profile plot           
# half of all values need to be negative                              
dm = numpy.argmin(distmat_profile) # dm = location of correlation max.

distmat_profile[0:dm+1] = -distmat_profile[0:dm+1]

#plt.hlines(0,0,300)
plt.plot(distmat_profile,scorr_profile,linewidth=3,color='0.3')
plt.show()




















