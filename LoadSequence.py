import os,io
import numpy

if os.sys.version_info.major > 2:
    from tkinter import *
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog import askopenfilename
else:
    from tkinter import *
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog   import asksaveasfilename

import tkinter.messagebox

import tkinter.ttk
import scipy
import scipy.misc
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageTk, ImageEnhance
#from Tkinter import ttk
from PIL import ImageFilter

from bytescl import bytescl

# for video files: 
# from contextlib import closing
# from videosequence import VideoSequence

# for video files (as 'videosequence' doesnt work on windows) 
import subprocess
import shutil

VALID_TYPES = (
    "bmp", "dib", "dcx", "gif", "im", "jpg", "jpe", "jpeg", "pcd", "pcx",
    "png", "pbm", "pgm", "ppm", "psd", "tif", "tiff", "xbm", "xpm"
)

def sort_list(l):
    """
    Mutates l, returns None.
    l: list of filenames.

    Sorts l alphabetically.
	But fixes the fact that, alphabetically, '20' comes before '9'.

    Example:
        if l = ['10.png', '2.jpg']:
            a simple l.sort() would make l = ['10.png', '2.jpg'],
            but this function instead makes l = ['2.jpg', '10.png']
    """
    l.sort()
    numbers, extensions = [], []
    i = 0
    while i < len(l):
        try:
            s = l[i].split(".")
            numbers.append(int(s[0]))
            extensions.append(s[1])
            l.pop(i)
        except ValueError:
            i += 1
    #Selection sort.
    for i in range(len(numbers)):
        for n in range(i, len(numbers)):
            if numbers[i] < numbers[n]:
                numbers[i], numbers[n] = numbers[n], numbers[i]
                extensions[i], extensions[n] = extensions[n], extensions[i]

    for i in range(len(numbers)):
        l.insert(0, "%d.%s" % (numbers[i], extensions[i]))

class ImageSequence:

    # let the user set/choose the directory, 
    # from which the image sequence will be loaded

    def __init__(self):

        # initially we load a "fake image"  

        self.directory = './fakesequence'

        self.sequence  = [] # holds the PIL image sequence  
        with open('./fakesequence/frame1.png', "rb") as f:
            fh = io.BytesIO(f.read())
            #Create a PIL image from the data                     
        img = Image.open(fh, mode="r")
        img = img.convert("L")  # convert to 8 Bit grayscale  
        self.sequence.append(img)


        self.files     = None
        self.width     = None
        self.height    = None
        self.seqlength = 1
        self.videofile = '' # path to video   
        self.pbstyle = None

        self.dirname = StringVar() # new feb 2021
        self.fname = StringVar()  # feb 2021

    def choose_directory(self):
    #def choose_directory(self,dirname,fname):

        try:
            # read file
            f=open('user_settings.dat','r')
            initdir=f.read()
        except:
            initdir=os.getcwd()

        self.directory = askdirectory(title="Select Directory",
                                            initialdir=initdir)
        f = open('user_settings.dat','w')
        f.write(self.directory) # write choosen directory into file 'f' 
        f.close()

        # update the label, which displays the directory name:
        self.dirname.set(self.directory)

        # update the name of the first image:
        f = os.listdir(self.directory)
        sort_list(f)
        #self.fname = self.fname.set(f[0])
        self.fname.set(f[0])



    def get_files(self):
        """
        directory: str, directory to search for files.

        Returns a sorted generator of all the files in directory
        that are a valid type (in VALID_TYPES).
        """
        files = []
        for f in os.listdir(self.directory):
            if len(f.split(".")) > 1 and f.split(".")[1].lower() in VALID_TYPES:
                files.append(f)
        sort_list(files)

        return (self.directory+"/"+f for f in files)

    def get_images(self):

        """
        directory: str, path to look for files in.
        screen: tuple, (w, h), screen size to resize images to fit on.

        Sorted generator. Yields resized PIL.Image objects for each
        supported image file in directory.
        """

        for filename in self.get_files():

            with open(filename, "rb") as f:
                #print(f)
                fh = io.BytesIO(f.read())
            #Create a PIL image from the data
            img = Image.open(fh, mode="r")
            #print "image format" 
            #print img.format

            img = img.convert("L")  # convert to 8 Bit grayscale 
            w,h = img.size
            # crop images to get rid of the embedded image information
            img = img.crop((1,1,w-1,h-1)) # left,top,right,bottom 

            yield img # yields a generator (PIL images)  

    def load_imgs(self):

        # basically loads the image sequence into self.sequence
        # by calling get_images()
        # finally self.sequence[i] holds the i-th frame (8 Bit, PIL image) 

        # if directory not selected yet: 
        if (self.directory==''):
            tkinter.messagebox.showinfo("Title","Please select directory first")
            self.choose_directory()

        # create a toplevel window to display the progress indicator 
        progresswin = Toplevel()
        progresswin.minsize(width=500,height=30)
        progresswin.title("Loading Image Sequence, Please Wait...")

        # get the monitor dimensions:
        screenw = progresswin.winfo_screenwidth()
        screenh = progresswin.winfo_screenheight()

        # place the progress indicator in the center of the screen 
        placement = "+%d+%d" % (screenw/2-300,screenh/2-15)
        progresswin.geometry(placement)

        # count the number of images in selected sequence (ni) 
        ni = 0
        for filename in self.get_files():
            ni = ni+1
        self.seqlength = ni

        self.pbstyle = tkinter.ttk.Style()
        self.pbstyle.theme_use("default")
        self.pbstyle.configure("TProgressbar", thickness=10)

        pbvar = IntVar() # progressbar variable (counts number of loaded imgs)   
        pb=tkinter.ttk.Progressbar(progresswin,mode="determinate",
			variable=pbvar,maximum=self.seqlength,length=600,
			style="TProgressbar")
        pb.grid(row=1,column=0,pady=5)

        progress = 0

        # reset image sequence before loading a newly choosen sequence 
        if (len(self.sequence) != 0):
            self.sequence = []

        for img in self.get_images():
            pbvar.set(progress)
            if (not(progress % 10)):
                progresswin.update()
            self.sequence.append(img)
            progress +=1

        progresswin.destroy()
        #style.configure("TProgressbar", thickness=5)

        # determine width and height of images: 
        firstimg = self.sequence[0]
        self.width, self.height = firstimg.size

    def load_video(self,dirname,fps):

        try:
            # read file
            f=open('user_settings.dat','r')
            initdir=f.read()
        except:
            initdir=os.getcwd()

        self.videofile = askopenfilename(title="Select Video",
                                        initialdir=initdir)

        f = open('user_settings.dat','w')
        f.write(os.path.split(self.videofile)[0])
	# writes choosen directory (value of 'directory') into file 'f' 
        f.close()

        # update the label, which displays the directory name:
        dirname.set(self.directory)


        # unfortunately it seems to be a paing to install the videosequence module in windows 
        # lets open the video and iterate over the frames, convert to 8Bit,PIL
        # with closing(VideoSequence(self.videofile)) as frames:
        #    ni = 0 
        #    for frame in frames: 
        #        frame = frame.convert("L")  # convert to 8 Bit grayscale   
        #        self.sequence.append(frame)  
        #        ni = ni + 1 




        # create a directory, which will hold the image sequence we will 
        # generate with ffmpeg, and set 'self.directory' to its corresponding path 

        self.directory =  self.videofile.split(".")[0]
        if os.path.exists(self.directory):
            shutil.rmtree(self.directory)  
        os.mkdir(self.directory) 

        # generate the image sequence in the just generated folder 

        #seqname = os.path.split(os.path.split(self.directory)[1])

        subprocess.call(['ffmpeg','-i',self.videofile,'-r',fps,self.videofile.split(".")[0]+'/frame_%04d.png'])  

        #firstimg = self.sequence[0] 
        #self.width, self.height = firstimg.size
        #self.seqlength = ni 





    def removepattern(self):
        firstimg = self.sequence[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        nimgs = len(self.sequence) # number of images   

        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs),int(height),int(width)),dtype=float)
        
        sumimg = numpy.zeros((int(height),int(width)),dtype=float)

        # PIL images -> numpy array 
        for i in range(nimgs):
            array[i,:,:] = numpy.array(self.sequence[i])


        # calc mean image 
        for i in range(nimgs):
            sumimg = numpy.add(sumimg,array[i,:,:])
        meanimg = numpy.multiply(1.0/float(nimgs), sumimg)  

        #print(meanimg) 

        # remove sensor pattern         
        for i in range(nimgs):
            array[i,:,:] = numpy.subtract(array[i,:,:], numpy.subtract(meanimg, gaussian_filter(array[i,:,:], sigma=1)))
  

        array = numpy.uint8(bytescl(array))
        for i in range(nimgs):
            self.sequence[i] = Image.fromarray(array[i,:,:])
        





    def imagereg(self):
        import imreg_dft

        from pystackreg import StackReg
        sr = StackReg(StackReg.RIGID_BODY)

        firstimg = self.sequence[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        nimgs = len(self.sequence) # number of images   

        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs),int(height),int(width)))


        # gaussian blurring 
        for i in range(nimgs):
            self.sequence[i] = self.sequence[i].filter(ImageFilter.GaussianBlur(radius=10))

        
        # PIL images -> numpy array 
        #for i in range(nimgs):
        #    array[i,:,:] = numpy.array(self.sequence[i])
        
        #print(len(array.shape)) 
        #aligned = sr.register_transform_stack(array, reference='previous',verbose=True)
        #for i in range(nimgs):
        #    #if (i > 0):
        #    mydict = imreg_dft.imreg.similarity(array[0,:,:],array[i,:,:])
        #    array[i,:,:] = mydict["timg"]


        #for i in range(nimgs):
        #    self.sequence[i] = Image.fromarray(numpy.uint8(scipy.misc.bytescale(aligned[i,:,:])))



    def extractmotion(self):
        firstimg = self.sequence[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        nimgs = len(self.sequence) # number of images   

        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs),int(height),int(width)),dtype=float)

        sumimg = numpy.zeros((int(height),int(width)),dtype=float)

        # PIL images -> numpy array 
        for i in range(nimgs):
            array[i,:,:] = numpy.array(self.sequence[i])

        # calc mean image 
        for i in range(nimgs):
            sumimg = numpy.add(sumimg,array[i,:,:])
        meanimg = numpy.multiply(1.0/float(nimgs), sumimg)  

        # extract motion  
        for i in range(nimgs):
            array[i,:,:] = numpy.subtract(array[i,:,:], meanimg)

        array = numpy.uint8(bytescl(array))
        for i in range(nimgs):
            self.sequence[i] = Image.fromarray(array[i,:,:])


    def wackeldackel(self):
        # PIL image sequence -> to numpy array

        seq = self.sequence # PIL sequence 
        wmax = self.width
        hmax = self.height 
        tmax = self.seqlength

        refimg = numpy.array(seq[0]) 
 
        cutborder = 30
        import matplotlib      
        import scipy
        from PIL import Image
        ref = numpy.fft.fft2(numpy.array(seq[0]))
        for t in range(tmax):
            img = numpy.array(seq[t])
            bla = numpy.fft.fft2(numpy.array(img))  
            corr = numpy.real(numpy.fft.ifft2(numpy.multiply(ref,numpy.conjugate(bla)))) 
            shift = numpy.unravel_index(numpy.argmax(corr, axis=None),corr.shape) 
            #matplotlib.pyplot.imshow(numpy.uint8(scipy.misc.bytescale(corr))) 
            #if shift[0] > cutborder : shift[0] = shift[0] - (wmax) 
            #if shift[1] > cutborder : shift[1] = shift[1] - (hmax) 
            #print shift 
            shifted = numpy.roll(img,shift,axis=(0,1))
            # cut shifted img  
            self.sequence[t] = Image.fromarray(numpy.uint8(bytescl(shifted[cutborder:wmax-cutborder,cutborder:hmax-cutborder])))

        # reassign object atributes 

        # determine width and height of images: 
        firstimg = self.sequence[0] 
        self.width, self.height = firstimg.size
        #print self.width


