import numpy as np
from PIL import Image
#generate a sequence showing a particle moving from one edge to the other edge

def draw_particle(x,y,r):
    sigma_x = r/2
    sigma_y = r/2
    x = np.linspace(x-2*r, x+2*r)
    y = np.linspace(y-2*r, y+2*r)
    X, Y = np.meshgrid(x, y)

    Z = (1 / (2 * np.pi * sigma_x * sigma_y)) * np.exp(-0.5 * (
                (X - mu_x) ** 2 / sigma_x ** 2 + (
                    Y - mu_y) ** 2 / sigma_y ** 2))




fps = 100 # frames per second
pixelsize = 100 # in nm

# plot a particle in the lower left edge


frame = np.zeros((400,400),dtype=np.uint8)
nt = 300

x = 5
y = 5

for t in range(nt):

    frame[:,:] = np.random.rand(400, 400)*10

    frame[x,y] = 100
    #frame[x-2:x+2,y-2:y+2] = 100

    x += 1
    y += 1

    image = Image.fromarray(frame)
    image.save('./trajectory/frame-'+str(t).zfill(5)+'.png')


