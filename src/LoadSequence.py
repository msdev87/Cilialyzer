import os,io
import numpy
import cv2

if os.sys.version_info.major > 2:
    from tkinter import *
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog import askopenfilename
else:
    from tkinter import *
    from tkinter.filedialog import askdirectory

import tkinter.messagebox

import tkinter.ttk
from scipy.ndimage import gaussian_filter

from PIL import Image
#from Tkinter import ttk
#from math_utils import bytescl

from math_utils.bytescl import bytescl

# for video files: 
# from contextlib import closing
# from videosequence import VideoSequence

import subprocess
import shutil
import threading

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

    # our image sequences are named as follows: 
    # base-name-numbering.ending 
    # here is a concrete example: '30fps_RT_1_swirl_2018-12-21-151557-0467.tif'

    # leading zeros may or may not be present! (both cases are handled) 

    numbering, basename = [], []
    i = 0
    while i < len(l):
        try:

            fname = l[i]
            s = fname.split(".")
            file_ending = s[-1]

            # check whether the image number is separated by 
            # a subtract sign, or an underline:

            if ('-' in s[0][-6:]):
                bla = s[0].split("-")
            if ('_' in s[0][-6:]):
                bla = s[0].split("_")

            number = bla[-1]
            numbering.append(number)

            del_chars = len(file_ending) + 1 + len(number)
            basename.append(fname[0:-del_chars])

            l.pop(i) # pop removes the i-th element from list 'l'

        except ValueError:
            i += 1

    for i in range(len(numbering)):
        for n in range(i, len(numbering)):
            if int(numbering[i]) < int(numbering[n]):
                numbering[i], numbering[n] = numbering[n], numbering[i]
                basename[i], basename[n] = basename[n], basename[i]

    for i in range(len(numbering)):
        l.insert(0, "%s%s.%s" % (basename[i],numbering[i],file_ending))


class ImageSequence:

    # let the user set/choose the directory,
    # from which the image sequence will be loaded

    def __init__(self):

        # initially we load a "fake sequence"

        self.directory = './fakesequence'

        self.sequence  = [] # holds the PIL image sequence  
        with open('../images/fakesequence/frame1.png', "rb") as f:
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
        self.dirname.set("No Directory Selected")
        self.fname = StringVar()  # feb 2021
        self.fname.set("No Directory Selected")

        self.busy_indicator = None
        self.thread1 = None
        self.busywin = None

    def choose_directory(self, automated=0):

        try:
            # try to read file holding previously chosen directory
            f = open('config/previous_directory.dat', 'r')
            initdir=f.read()
        except:
            initdir=os.getcwd()

        self.directory = askdirectory(title="Select Directory", initialdir=initdir)

        f = open('config/previous_directory.dat', 'w')
        f.write(self.directory) # write chosen directory into file 'f'
        f.close()

        # update the label, which displays the directory name:
        self.dirname.set(self.directory)

        if not automated:
        # update the name of the first image:
            f = os.listdir(self.directory)
            sort_list(f)
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

            # print('filename: ',filename)
            #with open(filename, "rb") as f:
            #    #print(f)
            #    fh = io.BytesIO(f.read())
            ##Create a PIL image from the data
            img = Image.open(filename, mode="r")

            if (img.mode == "L"):
                pass

            elif(img.mode == "RGB"):
                img=img.convert("L")

            else:
                # conversion of 16 bit images 
                numpyimg = numpy.array(img)
                numpyimg = numpyimg / 65536.0 * 255
                numpyimg.astype(int)

                img = Image.fromarray(numpyimg)
                img = img.convert("L")  # convert to 8 Bit grayscale

            w,h = img.size
            # crop images to get rid of the embedded image information
            img = img.crop((1,1,w-1,h-1)) # left,top,right,bottom 

            yield img # yields a generator (PIL images)  

    def load_imgs(self, nimgscombo, automated=0):

        # basically loads the image sequence into self.sequence
        # by calling get_images()
        # finally self.sequence[i] holds the i-th frame (8 Bit, PIL image) 

        # nimgscombo holds the number of images, which are to be read
        nimgs = nimgscombo.get()
        # print('-------------------------------------------------------------')
        # print(nimgs)
        # print(type(nimgs))

        if (nimgs!='all'):
            nimgs=int(nimgs)

        # print('starting to load images...')

        # if directory not selected yet:
        if not automated:
            if (self.directory==''):
                tkinter.messagebox.showinfo("Title","Please select directory first")
                self.choose_directory(automated=automated)

        if not automated:
            # create a toplevel window to display the progress indicator
            progresswin = Toplevel(height=10)
            progresswin.minsize(width=500,height=10)
            progresswin.title("Loading Image Sequence, Please Wait...")



            # get the monitor dimensions:
            screenw = progresswin.winfo_screenwidth()
            screenh = progresswin.winfo_screenheight()

            # place the progress indicator in the center of the screen
            placement = "+%d+%d" % (screenw/2-300,screenh/2-15)
            progresswin.geometry(placement)
            progresswin.update()



        # count the number of images in selected sequence (ni) 
        ni = 0
        for filename in self.get_files():
            ni = ni+1

        if ((nimgs != 'all') and (nimgs < ni)):
            self.seqlength = nimgs
        else:
            self.seqlength = ni

        if not automated:
            self.pbstyle = tkinter.ttk.Style()
            self.pbstyle.theme_use("default")
            self.pbstyle.configure("TProgressbar", thickness=10)

            pbvar = IntVar() # progressbar variable (counts number of loaded imgs)
            pb=tkinter.ttk.Progressbar(progresswin,mode="determinate",
                variable=pbvar, maximum=self.seqlength, length=600, style="TProgressbar")
            pb.place(in_=progresswin)
            progresswin.update()


        progress = 0

        # reset image sequence before loading a newly chosen sequence
        if (len(self.sequence) != 0):
            self.sequence = []

        for img in self.get_images():
            if (progress < self.seqlength):
                if (not(progress % 100)):
                    if not automated:
                        pbvar.set(progress)
                        progresswin.update()
                self.sequence.append(img)
                progress+=1

        if not automated:
            progresswin.destroy()
            #style.configure("TProgressbar", thickness=5)

        # determine width and height of images: 
        firstimg = self.sequence[0]
        self.width, self.height = firstimg.size

    def splitvideo_ffmpeg(self, fps):
        subprocess.call(['ffmpeg', '-i', self.videofile, '-r', fps, self.videofile.split(".")[0]+'/frame-%04d.png'])

    def video_to_sequence(self, fps):
        """
        ffmpeg gets used to convert the selected video to a sequence
        """

        try:
            # read file
            f=open('config/previous_directory.dat', 'r')
            initdir=f.read()
        except:
            initdir=os.getcwd()

        self.videofile = askopenfilename(title="Select Video",\
            initialdir=initdir)

        f = open('config/previous_directory.dat', 'w')
        f.write(os.path.split(self.videofile)[0])
	    # writes choosen directory (value of 'directory') into file 'f'
        f.close()

        # update the label, which displays the directory name:
        # dirname.set(self.directory)

        # unfortunately it seems to be a pain to install the videosequence module in windows 
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

        # seqname = os.path.split(os.path.split(self.directory)[1])

        # handle exception (ffmpeg might not be installed)
        try:
            # start thread, which splits the video file 
            self.thread1=threading.Thread(target=self.splitvideo_ffmpeg, args=[fps])
            self.thread1.start()

            self.busywin = Toplevel()
            self.busywin.minsize(width=500,height=20)
            self.busywin.title("Operation in progress")
            # get the monitor dimensions:
            screenw = self.busywin.winfo_screenwidth()
            screenh = self.busywin.winfo_screenheight()
            # place the busy indicator in the center of the screen 
            placement = "+%d+%d" % (screenw/2-300,screenh/2-15)
            self.busywin.geometry(placement)

            # add text label
            tl=Label(self.busywin,\
                text=' Please wait, the video will be read in a moment ', font="TkDefaultFont 11")
            tl.grid(row=0,column=0,pady=5)
            self.busywin.columnconfigure(0, weight=1)
            self.busywin.rowconfigure(0, weight=1)

            tl.update()
            self.busywin.update()

            self.thread1.join()

            self.busywin.destroy()

        except:
            tkinter.messagebox.showinfo("warning","Please check your ffmpeg installation!")

    def load_video(self, fps):
        """
        Convert the selected video (avi, mpeg, ...) to a PIL image sequence
        """

        # try to set 'initdir' to the most recently selected directory
        try:
            f=open('config/previous_directory.dat', 'r')
            initdir=f.read()
        except:
            initdir=os.getcwd()

        # self.videofile holds the path to the selected video 
        self.videofile = askopenfilename(title="Select Video",\
            initialdir=initdir)

        f = open('config/previous_directory.dat', 'w')
        f.write(os.path.split(self.videofile)[0])
	    # writes choosen directory (value of 'directory') into file 'f'
        f.close()

        # ---------------------------------------------------------------------
        # indicate busy status
        # ---------------------------------------------------------------------
        busywin = tkinter.Toplevel()
        busywin.minsize(width=500,height=20)
        busywin.title("Operation in progress")
        # get the monitor dimensions:
        screenw = busywin.winfo_screenwidth()
        screenh = busywin.winfo_screenheight()
        # place the busy indicator in the center of the screen 
        placement = "+%d+%d" % (screenw/2-300,screenh/2-15)
        busywin.geometry(placement)
        # add text label
        tl=tkinter.Label(busywin,\
        text=' Please wait, the video is being loaded... ', font="TkDefaultFont 11")
        tl.grid(row=0,column=0,pady=5)
        busywin.columnconfigure(0, weight=1)
        busywin.rowconfigure(0, weight=1)
        tl.update()
        busywin.update()
        # ---------------------------------------------------------------------

        cap = cv2.VideoCapture(self.videofile)
        nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fwidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fheight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.seqlength = nframes
        self.width = fwidth
        self.height = fheight

        nparray = numpy.zeros((int(nframes), int(fheight), int(fwidth), 3), dtype=numpy.float32)

        fc = 0
        ret = True

        while ((fc < nframes) and ret):
            ret, nparray[fc] = cap.read()
            fc += 1

        cap.release()

        # reset image sequence before loading a newly choosen sequence 
        if (len(self.sequence) != 0):
            self.sequence = []

        # average over RGB and convert the monochromatic frames to PIL sequence
        for i in range(nframes):
            frame = (nparray[i,:,:,0] + nparray[i,:,:,1] + nparray[i,:,:,2])/3.0
            self.sequence.append(Image.fromarray(numpy.uint8(frame)))

        # self.sequence holds now the image sequence 

        # destroy busywin as soon as video has been loaded
        busywin.destroy()

    def removepattern(self):
        firstimg = self.sequence[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        nimgs = len(self.sequence) # number of images   

        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs),int(height),int(width)),dtype=numpy.float32)

        sumimg = numpy.zeros((int(height),int(width)),dtype=numpy.float32)

        # PIL images -> numpy array 
        for i in range(nimgs):
            array[i,:,:] = numpy.array(self.sequence[i])

        # calc mean image 
        for i in range(nimgs):
            sumimg = numpy.add(sumimg,array[i,:,:])
        meanimg = numpy.multiply(1.0/float(nimgs), sumimg)  

        # remove sensor pattern         
        for i in range(nimgs):
            array[i,:,:] = numpy.subtract(array[i,:,:],
                numpy.subtract(meanimg, gaussian_filter(array[i,:,:], sigma=1)))

        array = numpy.uint8(bytescl.bytescl(array))
        for i in range(nimgs):
            self.sequence[i] = Image.fromarray(array[i,:,:])

    def imagereg(self):

        from pystackreg import StackReg
        sr = StackReg(StackReg.RIGID_BODY)

        firstimg = self.sequence[0] # first image of roi sequence  
        width, height = firstimg.size # dimension of images 
        nimgs = len(self.sequence) # number of images   

        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs),int(height),int(width)), dtype=numpy.float32)

        # PIL images -> numpy array 
        for i in range(nimgs):
            array[i,:,:] = numpy.array(self.sequence[i])

        # set reference to 'first', 'previous', or 'mean'
        aligned = sr.register_transform_stack(array, reference='mean', verbose=True)

        for i in range(nimgs):
            self.sequence[i] = Image.fromarray(numpy.uint8(aligned[i,:,:]))


    def extractmotion(self, roiseq):
        """
        this method subtracts the mean image in self.sequence, which contains
        the whole field of view, or, if it has already been defined, it
        subtracts the mean image from the roi-sequence (argument 'roiseq')
        Note that subtracting the mean is equivalent to removing the
        zero-frequency (static) contribution
        """

        sequence = roiseq

        firstimg = sequence[0] # first image of roi sequence
        width, height = firstimg.size # dimension of images 
        nimgs = len(sequence) # number of images

        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs), int(height), int(width)), dtype=numpy.float32)
        # sumimg: sum of images
        sumimg = numpy.zeros((int(height), int(width)), dtype=numpy.float32)

        # convert stack of PIL images to numpy array
        for i in range(nimgs):
            array[i, :, :] = numpy.array(sequence[i])

        # calculate the mean image
        for i in range(nimgs):
            sumimg = numpy.add(sumimg,array[i,:,:])
        meanimg = numpy.multiply(1.0/float(nimgs), sumimg)

        # extract motion  
        for i in range(nimgs):
            array[i,:,:] = numpy.subtract(array[i,:,:], meanimg)

        # subtract the minimum value of array from array  
        # (as the minimum value is always negative)
        # this ensures that all values are positive in 'array'

        array = numpy.subtract(array, numpy.amin(array))

        array = numpy.uint8(bytescl.bytescl(array))

        # print('max', numpy.amax(array))
        # print('min', numpy.amin(array))



        for i in range(nimgs):
            img = Image.fromarray(array[i,:,:])
            #self.sequence[i] = img
            roiseq[i] = img

    def binning(self, roiplayer):

        firstimg = roiplayer.roiseq[0] # first image of roi sequence
        width, height = firstimg.size # dimension of images 
        nimgs = len(roiplayer.roiseq) # number of images

        # initialize numpy float array, which will hold the image sequence  
        # array = numpy.zeros((int(nimgs), int(height), int(width)), dtype=float)

        for i in range(nimgs):
            roiplayer.roiseq[i] = roiplayer.roiseq[i].resize((width//2,height//2),
                resample=Image.BICUBIC)

        """
        # convert stack of PIL images to numpy array
        for i in range(nimgs):
            array[i, :, :] = numpy.array(roiseq[i])

        w=int(width/2)
        h=int(height/2)
        binned = numpy.zeros((nimgs,h,w))
        for t in range(nimgs):
            print(t)
            for i in range(h):
                for j in range(w):
                    iinds=[2*i,2*i,1+2*i,1+2*i]
                    jinds=[2*j,1+2*j,2*j,1+2*j]
                    tinds=[t,t,t,t]
                    inds = [tinds,iinds,jinds]
                    binned[t,i,j] = numpy.mean([array[t,2*i,2*j],array[t,2*i,1+2*j],array[t,1+2*i,2*j],array[t,1+2*i,1+2*j]])

        # convert numpy array back to PIL sequence
        for i in range(nimgs):
            roiseq[i] = Image.fromarray(numpy.uint8(binned[i,:,:]))
        """

        # Start to replay the binned sequence: 
        # roiplayer.stop = 0
        # roiplayer.animate()
        #roiplayer.refreshing = 1

        roiplayer.stop = 2
        roiplayer.frame.destroy()
        roiplayer.__init__(roiplayer.master, roiplayer.directory, roiplayer.refreshing, roiplayer.roiseq, roiplayer.seqlength, roiplayer.roiobj, roiplayer.selectroi)
        roiplayer.animate()
        roiplayer.stop = 0
        roiplayer.refreshing = 0 # as refreshing ends here  


    def denoise(self, roiseq):

        sequence = roiseq

        firstimg = sequence[0] # first image of roi sequence
        width, height = firstimg.size # dimension of images 
        nimgs = len(sequence) # number of images

        # initialize numpy float array, which will hold the image sequence  
        array = numpy.zeros((int(nimgs), int(height), int(width)), dtype=float)

        # convert stack of PIL images to numpy array
        for i in range(nimgs):
            array[i, :, :] = numpy.array(sequence[i])

        # median filter  
        #for i in range(nimgs):
        #    img = sequence[i]
        #    roiseq[i] = img.filter(ImageFilter.MedianFilter(size=5))

        # Gaussian blur in space
        for i in range(nimgs):
            array[i,:,:] = gaussian_filter(array[i,:,:],sigma=0.5)

        # Gaussian blur in time
        for w in range(width):
            for h in range(height):
                array[:,h,w] = gaussian_filter(array[:,h,w],sigma=0.5)

        array = numpy.uint8(bytescl.bytescl(array))

        for i in range(nimgs):
            img = Image.fromarray(array[i,:,:])
            roiseq[i] = img



    def wackeldackel(self):
        # PIL image sequence -> to numpy array

        seq = self.sequence # PIL sequence 
        wmax = self.width
        hmax = self.height 
        tmax = self.seqlength

        refimg = numpy.array(seq[0]) 
 
        cutborder = 30
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
            self.sequence[t] = Image.fromarray(numpy.uint8(bytescl.bytescl(shifted[cutborder:wmax-cutborder,cutborder:hmax-cutborder])))

        # reassign object atributes 

        # determine width and height of images: 
        firstimg = self.sequence[0] 
        self.width, self.height = firstimg.size

