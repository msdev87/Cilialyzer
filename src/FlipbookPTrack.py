import sys
import io, os
from PIL import Image, ImageTk, ImageEnhance
#import psutil 
import time
import numpy
import tkinter.ttk
import math
import bytescl
if os.sys.version_info.major > 2:
    from tkinter.filedialog import askdirectory
    import tkinter as tk
    from tkinter import Button
else:
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog import asksaveasfilename
    import tkinter as tk
    from tkinter import Button

import scipy

from scipy.ndimage.filters import uniform_filter
from scipy.ndimage.measurements import variance

from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.filters import uniform_filter

#from pyradar.filters.lee import lee_filter

import circle_fit

from pandastable import Table
import pandas
import pandastable

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

def get_files(directory):
    """
    directory: str, directory to search for files.

    Returns a sorted generator of all the files in directory
    that are a valid type (in VALID_TYPES).
    """
    files = []
    for f in os.listdir(directory):
        if len(f.split(".")) > 1 and f.split(".")[1].lower() in VALID_TYPES:
            files.append(f)
    sort_list(files)

    return (directory+"/"+f for f in files)

def GetMinMaxIntensity(self):

    pixls = self.PILimgs[0] # pixls = PIL image
    w,h = pixls.size # width and height of image

    # we crop the relevant part of the image 
    # (avoiding byte coded camera information at the border)  
    pixbox = pixls.crop((4,4,int(w-4),int(h-4)))
    pix_box = list(pixbox.getdata())

    self.MaxIntensity = max(pix_box)
    self.MinIntensity = min(pix_box)

    #print self.MaxIntensity 
    #print self.MinIntensity 


def LeeFilter(self):

    if (self.leefilter):

        #print "extractparticles: "
        #print self.extractparticles 

        pix = numpy.array(self.currentimg)
        leefiltered = numpy.subtract(pix,
                gaussian_filter(lee_filter(pix,self.leewin), self.gausswin))

        m = numpy.mean(leefiltered)
        std = numpy.std(leefiltered)

        if (int(self.pcolor.get()) == 1):
            # bright particles  
            leefiltered[numpy.where(leefiltered < (m+2*std))] = m
        else:
            leefiltered[numpy.where(leefiltered > (m-2*std))] = m

        leefiltered = bytescl.bytescl(leefiltered)

        # write the current image out as a png
        # self.currentimg.save("img" + str(self.index) + ".png", "PNG")

        self.currentimg = Image.fromarray(numpy.uint8(leefiltered),'L')

        # export lee filtered sequence (for timelapse)  
        #self.currentimg.save("img" + str(self.index) + ".png", "PNG")  		

def GammaScale(self):
    self.currentimg =\
        ImageEnhance.Contrast(self.currentimg).enhance(self.contrast)

def Sharpen(self):
    self.currentimg =\
        ImageEnhance.Sharpness(self.currentimg).enhance(self.sharp)

def Brighten(self):
    self.currentimg =\
        ImageEnhance.Brightness(self.currentimg).enhance(self.bright)

def bytescale(self):

    # lambda function performs the byte-scaling (contrast enhancement)  
    #pixls = self.currentimg      

    self.currentimg = Image.eval(self.currentimg,lambda xy: round((abs(
        xy-self.MinIntensity)/float(self.MaxIntensity-self.MinIntensity))*255))

def ResizeCurrentImage(self):
    w,h = self.currentimg.size
    scale = min((self.screen[0]/float(w), self.screen[1]/float(h)))
    self.currentimg=self.currentimg.resize((int(w*scale), int(h*scale)))

class ImgSeqPlayer(object):

    """
    Creates a tk.Frame and packs it onto the main window (master).
    Creates a tk.Canvas and packs it onto the frame.

    master: tk.Tk window.
    """

    def __init__(self, master, directory, refreshing, PILseq, seqlength,
                 roiobj,selectroi,FPS,pixsize):

        #self.searchbox = 10 # search box size 

        self.pspeed = tk.StringVar() # particle speed 

        self.ptracking = True # indicates activity-status of particle tracking  

        self.tracenumber = 0

        self.circlefit = [] # holds the output from the circlefit 

        self.recordingfps = float(FPS)
        self.pixsize = None
        self.recordedpixsize = pixsize

        self.roiseq = PILseq
        self.ROI = None
        self.anchor = None
        self.item = None
        self.bbox = None
        self.roiobj = roiobj

        # vars and lists to collect the particle trajectories

        self.trace_array = [] # array/list holding the trace (x,y,t,boxsize) 
        self.alltracesarray = [] # list holding all trace arrays  

        self.latesttrace = [] # the current trajectory
        self.smoothtrace = []
        self.alltraces = [] # holds all particle traces 
        self.latesttrajectoryfinish = 0
        self.track_cnt = 0
        self.start_track = 0


        self.selectroi = selectroi

        self.particle_coords = (None,None)

        self.leefilter = 0
        self.leewin = 7 # window for leefilter 
        self.gausswin = 20 # window for gaussian blur 

        self.refreshing = refreshing

        self.frame = tk.Frame(master,takefocus=0)
        self.frame.place(in_=master, anchor="c", relx=.5, rely=.5)

        self.seqlength = seqlength

        w,h = PILseq[0].size
        # create progressbar (indicator for the position of the current image in sequence)
        self.pbvar = tk.IntVar() # progress bar variable
        s = tkinter.ttk.Style()
        s.theme_use("default")
        s.configure("TProgressbar", thickness=5)
        progbar = tkinter.ttk.Progressbar(self.frame,mode="determinate",\
            variable=self.pbvar,maximum=seqlength,length=0.5*w,\
            style="TProgressbar")
        progbar.grid(column=1,row=2)

        self.frame2 = tk.LabelFrame(self.frame, takefocus=1, text='Player Controls', \
                labelanchor='n',borderwidth = 4,padx=3,pady=3,font=("Helvetica", 11, "bold"))
        self.frame2.grid(row=3,column=1)

        # ----------------------------------------------------------------------
        # **************** Particle Tracking Controls (Frame) ******************

        # add frame holding the 'particle tracking controls' (trackcframe) 
        self.trackcframe = tk.LabelFrame(self.frame,takefocus=1,
            text='Particle Tracking Controls',labelanchor='n',borderwidth=4,
            padx=2,pady=4,font=("Helvetica", 11, "bold"))
        self.trackcframe.grid(row=4,column=1)

        # radiobutton to specify the 'color' of particles 
        # (if self.pcolor=1 --> bright, if self.pcolor=2 --> dark)   
        self.radiocolor = [("Bright Particles", 1),("Dark Particles", 2)]

        if hasattr(self, 'pcolor'):
            pass
        else:
            self.pcolor = tk.StringVar()
            self.pcolor.set(2) # initialize with dark particles 

        self.pcolorB = tk.Radiobutton(self.trackcframe,text="Bright Particles",
            variable=self.pcolor,command=self.pcolor_func,value=1,bd=4,width=12)
        self.pcolorB.grid(row=0, column=0)
        self.pcolorB = tk.Radiobutton(self.trackcframe,text="Dark Particles",
            variable=self.pcolor,command=self.pcolor_func,value=2,bd=4,width=12)
        self.pcolorB.grid(row=1, column=0)

        fakepixel = ImageTk.PhotoImage(file=r"../icons/fakepixel.png")
        # "Lee-Filter button" 
        self.extractparticlesB = tk.Button(self.trackcframe,
            text='Extract Particles',command=self.extractparticles,width=20,
            height=1)

        #self.extractparticlesB = tk.Button(self.trackcframe,height=15,width=120,
        #    text='Extract Particles',command=self.extractparticles,image=fakepixel,compound=tk.LEFT)
        self.extractparticlesB.grid(row=0,column=1,padx=5)

	# export trajectory button 
        self.exportB =tk.Button(self.trackcframe,text='Export Trajectory',\
                                          command=self.export_trajectory,width=20,height=1)
        self.exportB.grid(row=1,column=1)

        # spinbox for the window size of the gaussian blur 
        gaussL=tk.Label(self.trackcframe, text="Gaussian: ", height=2,width=18) 
        gaussL.grid(row=0,column=2,columnspan=1)
        self.gaussB = tk.Spinbox(self.trackcframe, from_=1.0, to=30.0, increment=1.0,command=self.setgausswin,width=4)
        self.gaussB.grid(row=0,column=3,columnspan=1)
        #self.gaussB.delete(0, "end")
        self.gaussB.insert(0,20.0)

        # spinbox for lee filter
        leeL=tk.Label(self.trackcframe, text="Lee filter: ", height=2,width=18) 
        leeL.grid(row=1,column=2,columnspan=1)
        self.leeB = tk.Spinbox(self.trackcframe, from_=1.0, to=30.0, increment=1.0,command=self.setleewin,width=4)
        self.leeB.grid(row=1,column=3,columnspan=1)
        #self.gaussB.delete(0, "end")
        self.leeB.insert(0,7.0)

        # Button to delete the latest particle trace 
        self.delParticleB = tk.Button(self.trackcframe, text='Delete Particle', 
                                command=self.delParticle, width=20, height=1)
        self.delParticleB.grid(row=0,column=4,padx=5)

        # Button to continue the particle tracking
        self.continuetrackingB = tk.Button(self.trackcframe,
                text='Continue Tracking', command = self.continuetracking,
                width=20, height=1)
        self.continuetrackingB.grid(row=1,column=4,padx=5)

        # **********************************************************************

        # create frame holding buttons: "pause, play, next, previous,.."

        with open("../icons/prev2.png","rb") as f:
            fh = io.BytesIO(f.read())
        img = Image.open(fh, mode="r")
        previcon = ImageTk.PhotoImage(img)
        #previcon = tk.PhotoImage(file="./icons/prev2.gif")
        self.prevB = Button(self.frame2, image=previcon, command=self.previous_image)
        self.prevB.image = previcon
        self.prevB.grid(row=1,column=0)

        with open("../icons/pause2.png","rb") as f:
            fh = io.BytesIO(f.read())
        img = Image.open(fh, mode="r")
        pauseicon = ImageTk.PhotoImage(img)
        #pauseicon = tk.PhotoImage(file="./icons/pause2.gif")
        self.pauseB = Button(self.frame2, image=pauseicon, command=self.zero_fps)
        self.pauseB.image = pauseicon
        self.pauseB.grid(row=1,column=2)

        with open("../icons/play2.png","rb") as f:
            fh = io.BytesIO(f.read())
        img = Image.open(fh, mode="r")
        playicon = ImageTk.PhotoImage(img)
        #playicon = tk.PhotoImage(file="./icons/play2.gif")
        self.playB = Button(self.frame2, image=playicon, command=self.play)
        self.playB.image = playicon # save image from garbage collection 
        self.playB.grid(row=1,column=1)

        with open("../icons/stop2.png","rb") as f:
            fh = io.BytesIO(f.read())
        img = Image.open(fh, mode="r")
        stopicon = ImageTk.PhotoImage(img)
        #stopicon = tk.PhotoImage(file="./icons/stop2.gif")
        self.stopB = Button(self.frame2, image=stopicon, command=self.escape)
        self.stopB.image = stopicon
        self.stopB.grid(row=1,column=3)

        with open("../icons/next2.png","rb") as f:
            fh = io.BytesIO(f.read())
        img = Image.open(fh, mode="r")
        nexticon = ImageTk.PhotoImage(img)
        #nexticon = tk.PhotoImage(file="./icons/next2.gif")
        self.nextB = Button(self.frame2, image=nexticon, command=self.next_image)
        self.nextB.image = nexticon
        self.nextB.grid(row=1,column=4)


        # For Zoom -> radiobutton!

        # frame 10 is for zoom frame!
        self.frame10 = tk.Frame(self.frame,takefocus=1)
        self.frame10.grid(row=1,column=0)

        self.zoomframe = tk.LabelFrame(self.frame10,takefocus=1,text='Zoom',\
            labelanchor='n',borderwidth = 4,padx=0,pady=0,
            font=("Helvetica", 11, "bold"))
        self.zoomframe.grid(row=0,column=0,padx=3,pady=3)

        self.zooom =\
            [(" 25%",1),("50%",2),("75%",3),("100%",4),("150%",5),("200%",6)]

        if (not self.refreshing):
            if hasattr(self, 'var'):
                pass
            else:
                self.var = tk.StringVar()
                self.var.set(1) # initialize zoom to 25% 

        for text, mode in self.zooom:
            self.zoomB = tk.Radiobutton(self.zoomframe, text=text, variable=self.var,
            value=mode, bd=4, width=6,command=self.refresh)
            self.zoomB.pack(side=tk.BOTTOM)

        # ---------------------------------------------------------------------
        # Spinbox to set the size of the search box
        # ---------------------------------------------------------------------
        self.searchboxframe = tk.LabelFrame(self.frame,takefocus=1,
                                text='Search Box',labelanchor='n',borderwidth=4,
                                padx=22,pady=3,font=("Helvetica",11,"bold"))
        self.searchboxframe.grid(row=0,column=2)

        if hasattr(self, 'sboxsize'):
            pass
        else:
            self.sboxsize = 16

        self.searchboxB = tk.Spinbox(self.searchboxframe, from_=2, to=50,
            increment=2,command=self.setsearchbox,width=4)
        self.searchboxB.grid(row=0,column=0,columnspan=1)
        self.searchboxB.delete(0, "end")
        self.searchboxB.insert(0,16)
        # ----------------------------------------------------------------------


        # checkbox for contrast bytescaling ------------------------------------

        if hasattr(self, 'bscontrast'):
            pass
            #if (self.refreshing):
            #    #print "self.contrast is set to"
            #    print self.bscontrast 
            #    time.sleep(5)
        else:
            self.bscontrast = 0
            #print "self.contrast is not set, now set to"
            #print self.bscontrast 
            #time.sleep(5)

        self.frame5 = tk.LabelFrame(self.frame,takefocus=1,
            text='Contrast Settings',labelanchor='n',borderwidth=4,padx=2,
            pady=1,font=("Helvetica", 11, "bold"))
        self.frame5.grid(row=0,column=1)

        self.bscontrastB = tk.Checkbutton(self.frame5, text="Bytescaling",
            variable=self.bscontrast,command=self.setbscontrast)
        self.bscontrastB.grid(row=0,column=0,columnspan=2)

        if (self.bscontrast):
            self.bscontrastB.select()
        else:
            self.bscontrastB.deselect()


        # ------------------------- Gamma Faktor ------------------------------  

        if hasattr(self, 'contrast'):
            pass
        else:
            self.contrast = 1.0 # init value  

        contrastL=tk.Label(self.frame5, text="Gamma Correction: ", height=1,width=18)
        contrastL.grid(row=1,column=0,columnspan=1)

        self.contrastB = tk.Spinbox(self.frame5,from_=0.5,to=5.0,increment=0.2,
            command=self.setcontrast,width=3)
        self.contrastB.grid(row=1,column=1,columnspan=1)
        self.contrastB.delete(0, "end")
        self.contrastB.insert(0,1.0)

        # ---------------------------------------------------------------------- 

        # Image Sharpness 
        if hasattr(self, 'sharp'):
            pass
        else:
            self.sharp = 1.0 # init value  

        sharpnessL=tk.Label(self.frame5, text="Sharpness: ", height=1,width=18)
        sharpnessL.grid(row=0,column=2,columnspan=1)

        self.sharpnessB = tk.Spinbox(self.frame5,from_=0.5,to=5.0,
            increment=0.5,command=self.sharpener,width=3)
        self.sharpnessB.grid(row=0,column=3,columnspan=1)
        self.sharpnessB.delete(0, "end")
        self.sharpnessB.insert(0,1.0)

        # ----------------------------------------------------------------------

        # ----------------------- Image Brightness -----------------------------

        if hasattr(self, 'bright'):
            pass
        else:
            self.bright = 1.0 # init value  

        brightnessL=tk.Label(self.frame5,text="Brightness: ",height=2,width=18)
        brightnessL.grid(row=1,column=2,columnspan=1)

        self.brightnessB = tk.Spinbox(self.frame5,from_=0.5,to=5.0,
            increment=0.1,command=self.setbrightness,width=3)
        self.brightnessB.grid(row=1,column=3,columnspan=1)
        self.brightnessB.delete(0, "end")
        self.brightnessB.insert(0,1.0)

        # ----------------------------------------------------------------------

        # another radiobutton to set the replaying frame rate (FPS)  
        self.frame12 = tk.Frame(self.frame,takefocus=1)
        self.frame12.grid(row=1,column=2)

        self.fpsframe = tk.LabelFrame(self.frame12,takefocus=1,
            text='Replay Speed',labelanchor='n',borderwidth=4,padx=0,pady=0,
            font=("Helvetica", 11, "bold"))
        self.fpsframe.grid(row=0,column=1,padx=3,pady=3)

        self.radio_fps = [  ("  1 FPS",1), (" 10 FPS", 2), (" 20 FPS", 3),
                            (" 30 FPS", 4),(" 40 FPS", 5), (" 50 FPS", 6) ]

        if hasattr(self, 'fps'):
            pass
        else:
            self.fps = tk.StringVar()
            self.fps.set(3) # initialize with 20 fps 

        for text, mode in self.radio_fps:
            self.fpsB = tk.Radiobutton(self.fpsframe,text=text,
                variable=self.fps,value=mode,bd=4,width=6,
                command=self.fps_button)
            self.fpsB.pack(side=tk.BOTTOM)

        # ----------------------------------------------------------------------
        # *************** results frame at the right ***************************
        # ----------------------------------------------------------------------

        # display the particle speed, radius, circ frequency

        self.resultsframe = tk.LabelFrame(self.frame,takefocus=1,text='Results',
            labelanchor='n',borderwidth=4,padx=0,pady=0,
            font=("Helvetica", 11, "bold"), width=300, height=400)
        self.resultsframe.grid(row=1,column=3,rowspan=3,padx=40,pady=7)
        self.resultsframe.grid_propagate(0)

        # pandas frame
        #col_names = ["Radius [μm]","Speed [μm/s]","Omega [°/s]"]
        col_names =["Speed [μm/s]"]
        self.pandadf = pandas.DataFrame(columns = col_names)
        self.resultstable = Table(self.resultsframe, dataframe=self.pandadf,
                showtoolbar=True, showstatusbar=True)
        options = {'fontsize' : 12, 'floatprecision': 1}
        pandastable.config.apply_options(options, self.resultstable)
        self.resultstable.show()

        # **********************************************************************

        # get image size 

        #Scale image to the screen size while keeping aspect ratio.
        #w = self.roi[2] - self.roi[0]
        #h = self.roi[3] - self.roi[1]

        w,h= PILseq[0].size

        ctrl_height = 0
        add_width = 0

        # Set the canvas size according to the size of the rescaled image

        if (self.var.get() == '1'):
            self.can = tk.Canvas(self.frame,width=int(0.25*w),
                height=int(0.25*h))
            self.screen = int(0.25*w), int(0.25*h)
            self.zoomfac = 0.25
        if (self.var.get() == '2'):
            self.can = tk.Canvas(self.frame,width=int(0.5*w),
				height = int(0.5*h))
            self.screen = int(0.5*w), int(0.5*h)
            self.zoomfac = 0.5
        if (self.var.get() == '3'):
            self.can = tk.Canvas(self.frame, width = int(0.75*w),
				height = int(0.75*h))
            self.screen = int(0.75*w), int(0.75*h)
            self.zoomfac = 0.75
        if (self.var.get() == '4'):
            self.can = tk.Canvas(self.frame, width = int(1*w),
            height = int(1*h))
            self.screen = int(1*w), int(1*h)
            self.zoomfac = 1.0
        if (self.var.get() == '5'):
            self.can = tk.Canvas(self.frame, width = int(1.5*w),
            height = int(1.5*h))
            self.screen = int(1.5*w), int(1.5*h)
            self.zoomfac = 1.5
        if (self.var.get() == '6'):
            self.can = tk.Canvas(self.frame, width = int(2*w),
            height = int(2*h))
            self.screen = int(2*w), int(2*h)
            self.zoomfac = 2.0

        # place the canvas in which the images will be shown in the center 
        self.can.grid(row=1,column=1,padx=5,pady=5)

        # as the zoom-factor (self.zoomfac) has now been set 
        # we can initialize the pixelsize:
        self.pixsize = self.recordedpixsize / self.zoomfac
        #print("actual pixel size: ",self.pixsize)

        master.update()

        # if (not self.refreshing):
        #    # generate the array of PIL images 'self.PILimgs'    
        #    self.PILimgs = PILseq

        self.PILimgs = PILseq

        self.MaxIntensity = 0.0
        self.MinIntensity = 255.0

        GetMinMaxIntensity(self)

        # if not self.photos:  #len(self.photos) must be > 0.
        # raise FolderError(directory)

        self.index = 0  # Index of next photo to draw in self.photos.
        self.current_image = False  #Start with no image drawn on screen.

        self.current_photo = False
        self.currentimg = False

        #center position of photos on screen.
        self.center = (self.screen[0]+add_width)//2, (self.screen[1]+ctrl_height//3)//2

        # self.speed corresponds to the replayed "frames per second"
        if hasattr(self, 'speed'):
            pass
        else:
            self.speed = 20 # initialize with 20 frames per second  

        self.master, self.directory = master, directory

        self.stop = 0 # variable to stop if spacebar gets hit 

        # Label displaying FPS  
        #self.labeltext = tk.StringVar()
        #self.labeltext.set('playback speed [FPS]: ' + str(self.speed))
        #self.label = tk.Label(self.frame, textvariable=self.labeltext)
        #self.label.pack(side=tk.TOP)

    def animate(self):
        #print("starting animate") 

        global t0,t1

        #print "point 1: " + str(time.time()*1000.0)

        """
        Destroys old image (if there is one) and shows the next image
        of the sequence in self.photos. If at end of sequence, restart.
        Re-calls itself after 1./self.speed second
        """

        if (self.stop == 1):
            self.index = self.index
            #self.frame.quit()

        else:
            # Continue to next image if possible; otherwise, go back to beginning.
            # note the cheat here!
            # if 200 fps -> replay every second image with 100 fps!
            # if 300 fps -> display every third image
            if (self.speed < 100):
                #print "self.speed is set to:" 
                #print self.speed 
                self.index = self.index + 1 if self.index + 1 < len(self.PILimgs) else 0
            if (self.speed == 100):
                self.index = (self.index + 2)%len(self.PILimgs)
            if (self.speed == 200):
                self.index = (self.index + 4)%len(self.PILimgs)
            if (self.speed == 300):
                self.index = (self.index + 6)%len(self.PILimgs)

        # update progressbar: 
        self.pbvar.set(self.index)

        # check selected tab (from the notebook/mainloop) -> tabindex
        # if (self.tabindex):
        # self.frame.destroy()

        """
        def on_mouse_down(event):
            self.anchor = (event.widget.canvasx(event.x), event.widget.canvasy(event.y))
            self.item = None
        def on_mouse_drag(event):
            self.bbox = self.anchor + (event.widget.canvasx(event.x), event.widget.canvasy(event.y))
            self.ROI = self.bbox
            print "self.ROI "
            print self.ROI
            if self.item is None:
                self.item = event.widget.create_rectangle(self.bbox, outline="yellow")
            else:
                event.widget.coords(self.item, *self.bbox)
        def on_mouse_up(event):
            if self.item:
                on_mouse_drag(event)
                box = tuple((int(round(v)) for v in event.widget.coords(self.item)))

            # create cropped image sequence in self.roiseq: 
            xroi = sorted([int(self.ROI[0]),int(self.ROI[2])])
            yroi = sorted([int(self.ROI[1]),int(self.ROI[3])])

            nimgs = self.seqlength # number of images

            x1,x2 = int(xroi[0]), int(xroi[1])
            y1,y2 = int(yroi[0]), int(yroi[1])

            self.roiseq = [self.PILimgs[i].crop(self.ROI) for i in range(nimgs)]

            # crop ROI/resfresh and finally, animate ROI! 
            self.rraw trajectory tkinterefreshing = 1
            self.frame.destroy()
            self.__init__(self.master, self.directory,self.refreshing,self.roiseq,self.seqlength,self.roiobj,self.recordingfps)
            self.animate()
            self.stop = 0
            self.refreshing = 0 # as refreshing ends here  
        """

        if (self.selectroi == 1):

            #print('------------------------------')
            #print('selectroi ', self.selectroi)
            #print('------------------------------')

            def on_mouse_down(event):

                # start or restart tracking 
                self.start_track = 0

                # if (len(self.latesttrajectory) > 1):
                #    self.trajectories.append(self.latesttrajectory) # collect trajectories! 
                #print("len trajectories", len(self.trajectories))

                self.latesttrace = []
                self.smoothtrace = []
                #print "len? ", len(self.latesttrajectory)  
                self.latesttrajectoryfinish = 0
                self.track_cnt = 0
                self.particle_coords = (None,None)

                self.anchor = (self.can.canvasx(event.x)-(self.sboxsize/2), self.can.canvasy(event.y)-(self.sboxsize/2))

                # prevent error of clicking particle 
                # to closely to image borders: 
                self.particle_coords =(self.can.canvasx(event.x),self.can.canvasx(event.y))

                x = int(round(self.particle_coords[0]))
                y = int(round(self.particle_coords[1]))

                #print('x ',x)
                #print('y ',y)

                img=numpy.array(self.currentimg)
                imgh, imgw = img.shape

                # check whether the click has been appropriate 
                # otherwise ignore it 
                if ((int(self.index) < self.seqlength-5) and
                    (not ((x < int(1.1*self.sboxsize)) or (x > (imgw-(int(1.1*self.sboxsize)))) or
                    (y < int(1.1*self.sboxsize)) or (y > (imgh-(int(1.1*self.sboxsize))))))):


                    self.bbox = self.anchor + (self.can.canvasx(event.x)+(self.sboxsize/2), self.can.canvasy(event.y)+(self.sboxsize/2))
                    self.ROI = self.bbox

                    # create rectangle (yellow border)
                    self.item = self.can.create_rectangle(self.bbox, outline="red")
                    self.start_track = int(self.index)

                    # add mouse bindings here
                    #self.can.xview_moveto(0)
                    #self.can.yview_moveto(0)
                    #self.can.bind('<ButtonPress-1>', on_mouse_down)
                else:
                    pass

            # add mouse bindings here
            self.can.xview_moveto(0)
            self.can.yview_moveto(0)
            self.can.bind('<ButtonPress-1>', on_mouse_down)

        try:
            #print (time.time() - t0) * 1000.
            if (self.speed < 100):
                delay = (1./self.speed) - (time.time() - t0)
            if (self.speed > 50):
                delay = 0.02 - (time.time() - t0)
                #print('delay [s]' + str(delay))  

            #print(delay)

            if delay > 0:
                time.sleep(delay)
                #print "delay"
                #print delay
        except:
            pass

        #Remove old image.
        if self.current_image:
            self.can.delete(self.current_image)

        # Create new image!
        t0 = time.time()

        self.currentimg = self.PILimgs[self.index]

        if (self.bscontrast):
            bytescale(self)

        # resize image according to the user's choice 
        ResizeCurrentImage(self)
        GammaScale(self)
        Sharpen(self)
        Brighten(self)
        LeeFilter(self) # Lee-Filter

        if (self.stop == 0):
            if self.anchor is not None:
                # particle has been clicked 
                # --> start or continue tracking 
                self.trackparticle()

        self.current_photo = ImageTk.PhotoImage(self.currentimg)
        self.current_image = self.can.create_image(self.center,image=self.current_photo) # draw image! 

        if (self.selectroi == 1):
            # update rectangle (red rectanlge indicates the tracking process) 
            if ((self.index % 1) == 0):
                if (self.bbox is not None):

                    winsize = self.sboxsize #int(self.sboxsize.get())
                    self.anchor =\
                        (int(round(self.particle_coords[0]))-int(winsize/2),
                        int(round(self.particle_coords[1]))-int(winsize/2))
                    self.bbox = self.anchor +\
                        (int(round(self.particle_coords[0]))+int(winsize/2),
                        int(round(self.particle_coords[1]))+int(winsize/2))
                    self.can.create_rectangle(self.bbox, outline="red",width=2)


        # indicate all already tracked particles!
        if (len(self.alltraces) > 0):

            for i in range(len(self.alltraces)):

                #print('drawing ',i,'-th trace')

                # trace -> array holding x,y,timeindex,sboxsize 
                trace = numpy.array(self.alltracesarray[i])

                # check whether trace holds the current frame number
                frameinds = list(trace[:,2])

                try:
                    ind = frameinds.index(self.index)

                    # draw rectangle of already tracked particle i: 
                    x = int(round(trace[ind,0]))
                    y = int(round(trace[ind,1]))
                    wsize = trace[ind,3] # search box size 
                    bla = int(wsize/2)
                    box = (x-bla,y-bla,x+bla,y+bla)

                    #print('drawing box of ',i,'-th particle') 
                    self.can.create_rectangle(box,outline="yellow", width=2)

                except ValueError:
                    # self.index was not in the list
                    pass


        if (self.stop != 2):
            self.frame.after_idle(self.animate) # recalls self.animate

        else:
            if (not self.ptracking):

                # particle tracking has stopped --> self.stop has been set to 2 
                # particle has reached end of journey --> draw trace + circle 

                # draw particle trace 
                self.can.create_line(self.latesttrace,fill="red",width=2,smooth=True) 

                # draw fitted arc
                #self.can.create_oval(xc-rad,yc-rad,xc+rad,yc+rad,outline="orange",width=2)
                self.can.create_line(self.smoothtrace,fill="orange",width=3)


                # makes sure that gui gets updated properly  
                self.frame.update_idletasks()

            else:
                pass


    def refresh(self):

        """ Destroy current frame. Re-initialize animation. """
        self.refreshing = 1
        self.frame.destroy()

        self.__init__(self.master,self.directory,self.refreshing,self.PILimgs,
            self.seqlength, self.roiobj,self.selectroi, self.recordingfps,
            self.recordedpixsize)
        self.animate()
        self.stop = 0
        self.refreshing = 0 # as refreshing ends here  

    def play(self):
        self.stop = 0
        self.frame.after_idle(self.animate)

    def setbscontrast(self):
        # switch the value for bscontrast, when the checkbox gets actuated 
        if (self.bscontrast):
            self.bscontrast = 0
            #print "bscontrast set to 0"
            #time.sleep(5.0) 

        else:
            self.bscontrast = 1
            #print "bscontrast st to 1"
            #time.sleep(5) 

    def setcontrast(self):
        self.contrast = float(self.contrastB.get()) # get the value (return value -> string!)    

    def setgausswin(self):
        self.gausswin = float(self.gaussB.get())

    def setleewin(self):
        self.leewin = float(self.leeB.get())

    def setsearchbox(self):
        self.sboxsize =  int(self.searchboxB.get())

    def sharpener(self):
        self.sharp = float(self.sharpnessB.get())

    def setbrightness(self):
        self.bright = float(self.brightnessB.get())

    def increase_fps(self):
        """ Decrease time between screen redraws. """
        self.speed = self.speed + 1 if self.speed > 1 else 1
        #self.labeltext.set('playback speed [FPS]: ' + str(float(self.speed)))

    def fps_button(self):

        if (self.fps.get() == '1'): self.speed = 1
        if (self.fps.get() == '2'): self.speed = 10
        if (self.fps.get() == '3'): self.speed = 20
        if (self.fps.get() == '4'): self.speed = 30
        if (self.fps.get() == '5'): self.speed = 40
        if (self.fps.get() == '6'): self.speed = 50

        #self.labeltext.set('playback speed [FPS]: ' + str(float(self.speed)))


    def decrease_fps(self):
        """ Increase time between screen redraws. """
        self.speed -= 1
        self.labeltext.set('playback speed [FPS]: ' + str(float(self.speed)))

    def zero_fps(self):
        """ Increase time between screen redraws. """
        self.stop = 1

    def escape(self):
        self.stop = 2

    def next_image(self):
        self.index = (self.index + 1)%(len(self.PILimgs))

    def previous_image(self):
        self.index = (self.index - 1)%(len(self.PILimgs))

    def extractparticles(self):
        self.leefilter = 1

    def pcolor_func(self):
        #print("test pcolor")
        #print(self.pcolor.get())
        pass

    def export_trajectory(self):
        # export the trajectory to a csv file 
        # first we need to stop animation:
        self.stop = 2
        fname = asksaveasfilename(initialdir = self.directory,title = "Export Trajectory to File",)
        print("fname")
        print(fname)

        l = len(self.latesttrace)
        xpos = numpy.zeros(l)
        ypos = numpy.zeros(l)
        time = numpy.zeros(l)

        for i in range(l):
            yx = self.latesttrace[i]
            ypos[i] = float(yx[0])
            xpos[i] = float(yx[1])
            time[i] = float(i) / self.recordingfps

        xvar = numpy.var(xpos)
        yvar = numpy.var(ypos)

        # save x,y,t as csv 	
        numpy.savetxt('numpy.csv', fmt='%.2f', delimiter=',', header="particle trajectory (x,y,t)")

    def trackparticle(self):

        # current particle coordinates 
        x = int(round(self.particle_coords[0]))
        y = int(round(self.particle_coords[1]))

        img=numpy.array(self.currentimg)
        imgh, imgw = img.shape

        winsize = self.sboxsize

        # track particle until end of movie gets reached
	# OR: until the particle reaches the edge of the images  
        # this gets checked by the following conditions 

        if (((len(self.latesttrace)+self.start_track) < self.seqlength-5) and
            (not ((x < int(1.1*winsize)) or (x > (imgw-(int(1.1*winsize)))) or
                  (y < int(1.1*winsize)) or (y > (imgh-(int(1.1*winsize))))))):

            # the above conditions check, whether the time index is smaller 
            # than T-10 and whether the particle did not yet reach the 
            # images' edges 

            window = img[int(y-winsize/2):int(y+winsize/2),
                         int(x-winsize/2):int(x+winsize/2)]

            # self.pcolor designates the particle color (bright or dark):
            # self.pcolor = 1 -> bright particles -> get max 
            # self.pcolor = 2 -> dark particles -> get min 

            if (int(self.pcolor.get()) == 1):
                yarr, xarr = numpy.where(window == window.max())
            else:
                yarr, xarr = numpy.where(window == window.min())

            if (len(xarr) > 1):
                indx = int(round(numpy.mean(xarr)))
                indy = int(round(numpy.mean(yarr)))
            else:
                indx = xarr[0]
                indy = yarr[0]

            newx = int(-winsize/2 + indx + x)
            newy = int(-winsize/2 + indy + y)

            # update position 
            self.track_cnt = self.track_cnt + 1
            self.particle_coords = (newx,newy) # tuple particle coords

            self.latesttrace.append(self.particle_coords)

            self.trace_array.append([x,y,self.index,self.sboxsize])

        else:

            # particle reached the end of its journey 
            # least square fit and draw the trajectory 

            #print("end reached")

            l = len(self.latesttrace) # l: length of particle trace (timesteps)  

            #print("self.latesttrace")
            #print(self.latesttrace)

            xpos = numpy.zeros(l)
            ypos = numpy.zeros(l)

            for i in range(l):
                yx = self.latesttrace[i]
                xpos[i] = float(yx[0])
                ypos[i] = float(yx[1])

            # smooth the trajectory and fit a spline to the smoothed trajectory  
            import smooth
            from scipy import interpolate

            xs=smooth.running_average(xpos,5)
            ys=smooth.running_average(ypos,5)

            bla=numpy.array(range(len(xs)))

            splx = interpolate.UnivariateSpline(bla,xs)
            sply = interpolate.UnivariateSpline(bla,ys)

            # calculate the particle speed = curvelength / elapsed time  

            xnew=splx(bla)
            ynew=sply(bla)
        
            for i in range(len(bla)):
                self.smoothtrace.append((xnew[i],ynew[i]))


            curvelength=0.
            for i in range(l-1):
                dx=xnew[i+1]-xnew[i]
                dy=ynew[i+1]-ynew[i]
                curvelength=curvelength+math.sqrt(dx**2+dy**2)

            # calculate particle speed 'pspeed' in [μm/s] 
            pspeed = curvelength * self.recordingfps *\
                    (self.pixsize/1000.0) / float(len(self.latesttrace))



            #self.can.create_line((xc,yc),(x1,y1),fill="green",width=5)
            #self.can.create_line((xc,yc),(xpos[30],ypos[30]),fill="blue",width=3)
            #self.master.update()
            #time.sleep(10)


            self.tracenumber = len(self.alltraces)
            # update results data frame
            #if (self.tracenumber == 0):

            self.resultstable.addRow()

            self.pandadf.at[self.tracenumber,'Speed [μm/s]'] = round(pspeed,2)

            self.resultstable.updateModel(pandastable.data.TableModel(self.pandadf))
            self.resultstable.redraw()
            
            
            print(pspeed)

            #print('---------------------- pandatable -------------------------')    
            #print(self.resultstable)
            #print('-----------------------------------------------------------')

            # stop tracking 
            self.stop = 2

            self.ptracking = False

            # append the latest particle trace to alltraces list: 
            self.alltraces.append(self.latesttrace)
            #print("len of alltraces:", len(self.alltraces))

            # 'tracking back in time' 
            # this is just to indicate which particles have already been 
            # tracked (in order to make sure that the user does not choose 
            # the same particle twice)

            # in order to "track the particles back in time", we simply use 
            # the mean speed and the circular fit to 'extrapolate' the 
            # particles' coordinates for all frames t < t' 
            # (where t' denotes the frame in which the particle 
            # has been clicked by the user) 

            # t0: starting time of tracking
            #t0 = numpy.array(self.trace_array)[0,2]

            # now we extrapolate self.trace_array for all t < t0:
            #for t in range(t0):
            #    # determine for all t < t0 -> x(t),y(t)  


            # now we can add trace_array to alltracesarray:
            self.alltracesarray.append(self.trace_array)


            """
            #"straight" transport can be fitted by a polynomial fit! 
            # check whether the particle moves around more vertically
            # or more horizontally (by simply comparing the variances):
            xvar = numpy.var(xpos)
            yvar = numpy.var(ypos)

            if (xvar > yvar):
                # fit y(x) to third order polynomial

                c = numpy.polyfit(xpos,ypos,3)
                p = numpy.poly1d(c)
                fit = p(xpos)
                #print(fit)

                # calculate the mean particel speed along trajectory
                # calculate curve length

                xypos = numpy.concatenate((xpos, fit))
                xypos = numpy.reshape(xypos, (2,l))
                xypos = numpy.transpose(xypos)
                #print(xypos)

                lengths = numpy.sqrt(numpy.sum(numpy.diff(xypos, axis=0)**2, axis=1))
                curvelength = numpy.sum(lengths)
                #print("curvelength: ", curvelength)

            else:

                #print("test")
                dummy = xpos
                xpos = ypos
                ypos = dummy
                c = numpy.polyfit(xpos,ypos,3)
                p = numpy.poly1d(c)
                fit = p(xpos)
                #print(fit)

                xypos = numpy.concatenate((xpos, fit))
                xypos = numpy.reshape(xypos, (2,l))
                xypos = numpy.transpose(xypos)

                lengths = numpy.sqrt(numpy.sum(numpy.diff(xypos, axis=0)**2, axis=1))
                curvelength = numpy.sum(lengths)

            # calculate the particle speed :
            pspeed = curvelength * self.recordingfps * (self.pixsize/1000.0) /
                     float(len(self.latesttrajectory))
            self.pspeed.set("{:.1f}".format(pspeed))
            print(self.pspeed)
            #print("particle speed: ", pspeed)
            #print("curvelength: ", curvelength)
            #print("fps: ", self.recordingfps
            #print("pix size: ", self.pixsize)
            #print("(self.latesttrajectory) :", len(self.latesttrajectory))
            """

    def delParticle(self):

        # delete results from panda table  
        self.pandadf.at[self.tracenumber,'Speed [μm/s]'] = 0.0
        #self.pandadf.at[self.tracenumber,'Radius [μm]'] = 0.0
        #self.pandadf.at[self.tracenumber,'Omega [°/s]'] = 0.0
        self.resultstable.redraw()

        # remove latest trace from all traces 
        self.alltraces.remove(self.latesttrace)

        self.alltracesarray.remove(self.trace_array)
        self.trace_array = []

        # continue tracking
        self.continuetracking()

    def continuetracking(self):
        #print("continuetracking")
        self.stop=0
        self.latesttrace = []
        self.anchor = None
        self.bbox = None
        self.ptracking = True
        self.frame.after_idle(self.animate)
        self.trace_array = []

def lee_filter(img, size):

    img_mean = uniform_filter(img, (size, size))
    img_sqr_mean = uniform_filter(img**2, (size, size))
    img_variance = img_sqr_mean - img_mean**2

    overall_variance = variance(img)

    img_weights = img_variance / (img_variance + overall_variance)
    img_output = img_mean + img_weights * (img - img_mean)
    return img_output

