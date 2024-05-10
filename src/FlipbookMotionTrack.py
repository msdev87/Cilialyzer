import sys
import io, os
from PIL import Image, ImageTk, ImageEnhance
#import psutil 
import time
import numpy
import ttk
if os.sys.version_info.major > 2:
    from tkinter.filedialog import askdirectory
    import tkinter as tk
    from tkinter import Button
else:
    from tkFileDialog import askdirectory
    import Tkinter as tk
    from Tkinter import Button

VALID_TYPES = (
    "bmp", "dib", "dcx", "gif", "im", "jpg", "jpe", "jpeg", "pcd", "pcx",
    "png", "pbm", "pgm", "ppm", "psd", "tif", "tiff", "xbm", "xpm"
)


def sort_list(l):
    """
    Mutates l, returns None.
    l: list of filenames.

    Sorts l alphabetically. But fixes the fact that, alphabetically, '20' comes before '9'.

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
    for i in xrange(len(numbers)):
        for n in xrange(i, len(numbers)):
            if numbers[i] < numbers[n]:
                numbers[i], numbers[n] = numbers[n], numbers[i]
                extensions[i], extensions[n] = extensions[n], extensions[i]

    for i in xrange(len(numbers)):
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

def GammaScale(self):
    self.currentimg = ImageEnhance.Contrast(self.currentimg).enhance(self.contrast)

def Sharpen(self):
    self.currentimg = ImageEnhance.Sharpness(self.currentimg).enhance(self.sharp)

def Brighten(self):
    self.currentimg = ImageEnhance.Brightness(self.currentimg).enhance(self.bright)

def bytescale(self):

    # lambda function performs the byte-scaling (contrast enhancement)  
    #pixls = self.currentimg      

    self.currentimg = Image.eval(self.currentimg,
            lambda xy: round((abs(xy - self.MinIntensity) / float(self.MaxIntensity-self.MinIntensity)) * 255))


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
    def __init__(self, master, directory,refreshing,PILseq,seqlength,roiobj,selectroi):


        self.roiseq = PILseq 
        self.ROI = None  
        self.anchor = None
        self.item = None
        self.bbox = None
        self.roiobj = roiobj 

        self.selectroi = selectroi


        self.refreshing = refreshing

        self.frame = tk.Frame(master,takefocus=0)
        self.frame.place(in_=master, anchor="c", relx=.5, rely=.5)

        self.seqlength = seqlength 

        w,h = PILseq[0].size
        # create progressbar (indicator for the position of the current image in sequence)
        self.pbvar = tk.IntVar() # progress bar variable
        s = ttk.Style()
        s.theme_use("default")
        s.configure("TProgressbar", thickness=5)
        progbar = ttk.Progressbar(self.frame,mode="determinate",variable=self.pbvar,\
                maximum=seqlength,length=0.5*w,style="TProgressbar")
        progbar.grid(column=1,row=2) 


        self.frame2 = tk.LabelFrame(self.frame,takefocus=1, text='Player Controls', \
                labelanchor='n',borderwidth = 4,padx=3,pady=3,font=("Helvetica", 11, "bold"))
        self.frame2.grid(row=3,column=1)


       

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

        self.zoomframe = tk.LabelFrame(self.frame10,takefocus=1,text='Zoom', \
                labelanchor='n',borderwidth = 4,padx=0,pady=0,font=("Helvetica", 11, "bold"))
        #self.zoomframe.pack(side=tk.LEFT)
        self.zoomframe.grid(row=0,column=0,padx=3,pady=3)

        self.zooom = [(" 75%",1),("100%", 2), ("125%", 3),("150%", 4), ("200%", 5), ("300%",6)]

        if (not self.refreshing):
            if hasattr(self, 'var'):
                pass
            else:
                self.var = tk.StringVar()
                self.var.set(2) # initialize zoom to 100% 

        for text, mode in self.zooom:
            self.zoomB = tk.Radiobutton(self.zoomframe, text=text, variable=self.var,
            value=mode, bd=4, width=6,command=self.refresh)
            self.zoomB.pack(side=tk.BOTTOM)

        # checkbox for contrast bytescaling --------------------------------------------------------

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


        self.frame5 = tk.LabelFrame(self.frame, takefocus=1,text='Contrast Settings', \
                labelanchor='n',borderwidth = 4,padx=3,pady=3,font=("Helvetica", 11, "bold"))
        self.frame5.grid(row=0,column=1) 

        self.bscontrastB = tk.Checkbutton(self.frame5, text="Bytescaling",
        variable=self.bscontrast,command=self.setbscontrast)
        #self.bscontrastB.pack(side=tk.LEFT) 
        self.bscontrastB.grid(row=0,column=0,columnspan=2)

        if (self.bscontrast):
            self.bscontrastB.select()
        else:
            self.bscontrastB.deselect()


        # Gamma Faktor -----------------------------------------------------------------------------  
        if hasattr(self, 'contrast'):
            pass
        else:
            self.contrast = 1.0 # init value  


        #self.frame6 = tk.Frame(self.frame, takefocus=1)
        #self.frame6.pack(side=tk.BOTTOM)

        contrastL=tk.Label(self.frame5, text="Gamma Correction: ", height=2,width=18)
        #contrastL.pack(side=tk.LEFT)
        contrastL.grid(row=1,column=0,columnspan=1) 



        self.contrastB = tk.Spinbox(self.frame5, from_=0.5, to=5.0, increment=0.2,command=self.setcontrast,width=3)
        #self.contrastB.pack(side=tk.LEFT)
        self.contrastB.grid(row=1,column=1,columnspan=1)

        self.contrastB.delete(0, "end")
        self.contrastB.insert(0,1.0)
        # ------------------------------------------------------------------------------------------ 


        # Image Sharpness 
        if hasattr(self, 'sharp'):
            pass
        else:
            self.sharp = 1.0 # init value  


        #self.frame7 = tk.Frame(self.frame, takefocus=1)
        #self.frame7.pack(side=tk.BOTTOM)

        sharpnessL=tk.Label(self.frame5, text="Sharpness: ", height=2,width=18)
        #sharpnessL.pack(side=tk.LEFT)
        sharpnessL.grid(row=0,column=2,columnspan=1)

        self.sharpnessB = tk.Spinbox(self.frame5, from_=0.5, to=5.0, increment=0.5,command=self.sharpener,width=3)
        #self.sharpnessB.pack(side=tk.LEFT)
        self.sharpnessB.grid(row=0,column=3,columnspan=1)

        self.sharpnessB.delete(0, "end")
        self.sharpnessB.insert(0,1.0)
        # --------------





        # Image Brightness 
        if hasattr(self, 'bright'):
            pass
        else:
            self.bright = 1.0 # init value  


        #self.frame8 = tk.Frame(self.frame, takefocus=1)
        #self.frame8.pack(side=tk.BOTTOM)

        brightnessL=tk.Label(self.frame5, text="Brightness: ", height=2,width=18)
        #brightnessL.pack(side=tk.LEFT)
        brightnessL.grid(row=1,column=2,columnspan=1) 


        self.brightnessB = tk.Spinbox(self.frame5, from_=0.5, to=5.0, increment=0.1,command=self.setbrightness,width=3)
        self.brightnessB.grid(row=1,column=3,columnspan=1) 

        self.brightnessB.delete(0, "end")
        self.brightnessB.insert(0,1.0)
        # --------------



        # another radiobutton for comfortably setting FPS  
        self.frame12 = tk.Frame(self.frame,takefocus=1)
        self.frame12.grid(row=1,column=2)

        self.fpsframe = tk.LabelFrame(self.frame12,takefocus=1,text='Replay Speed', \
                labelanchor='n',borderwidth = 4,padx=0,pady=0,font=("Helvetica", 11, "bold"))

        #self.fpsframe.pack(side=tk.LEFT)
        self.fpsframe.grid(row=0,column=1,padx=3,pady=3)

        self.radio_fps = [(" 10 FPS", 1),(" 50 FPS", 2), ("100 FPS", 3),
        ("200 FPS", 4), ("300 FPS", 5)]

        if hasattr(self, 'fps'):
            pass
        else:
            self.fps = tk.StringVar()
            self.fps.set(3) # initialize

        for text, mode in self.radio_fps:
            self.fpsB = tk.Radiobutton(self.fpsframe, text=text, variable=self.fps, value=mode,
            bd=4, width=6,command=self.fps_button)
            self.fpsB.pack(side=tk.BOTTOM)




        # get image size 



        #Scale image to the screen size while keeping aspect ratio.
        #w = self.roi[2] - self.roi[0]
        #h = self.roi[3] - self.roi[1]
        w,h= PILseq[0].size
        print "w,h"
        print w
        print h

        ctrl_height = 0
        add_width = 0

        # Set the canvas size according to the size of the rescaled image


        self.zoomfac = 1.0

        if (self.var.get() == '1'):
            #self.can = tk.Canvas(self.frame, width = int(0.75*w)+add_width, height = int(0.75*h)+ctrl_height)
            self.can = tk.Canvas(self.frame, width = int(0.75*w), height = int(0.75*h))
            self.screen = int(0.75*w), int(0.75*h)
            self.zoomfac = 0.75
        if (self.var.get() == '2'):
            #self.can = tk.Canvas(self.frame, width = int(w)+add_width, height = int(h)+ctrl_height)
            self.can = tk.Canvas(self.frame, width = int(w), height = int(h))
            self.screen = w, h
            self.zoomfac = 1.0 
        if (self.var.get() == '3'):
            self.can = tk.Canvas(self.frame, width = int(1.25*w)+add_width,
            height = int(1.25*h)+ctrl_height)
            self.screen = int(1.25*w), int(1.25*h)
            self.zoomfac = 1.25
        if (self.var.get() == '4'):
            self.can = tk.Canvas(self.frame, width = int(1.5*w)+add_width,
            height = int(1.5*h)+ctrl_height)
            self.screen = int(1.5*w), int(1.5*h)
            self.zoomfac = 1.5
        if (self.var.get() == '5'):
            self.can = tk.Canvas(self.frame, width = int(2*w)+add_width,
            height = int(2*h)+ctrl_height)
            self.screen = int(2*w), int(2*h)
            self.zoomfac = 2.0
        if (self.var.get() == '6'):
            self.can = tk.Canvas(self.frame, width = int(3*w)+add_width,
            height = int(3*h)+ctrl_height)
            self.screen = int(3*w), int(3*h)
            self.zoomfac = 3.0
        # place the canvas in which the images will be shown in the center of the window 
        self.can.grid(row=1,column=1,padx=5,pady=5)

        master.update()




        #if (not self.refreshing):
        #    # generate the array of PIL images 'self.PILimgs'    
        #    self.PILimgs = PILseq

        self.PILimgs = PILseq 



        self.MaxIntensity = 0.0
        self.MinIntensity = 255.0

        GetMinMaxIntensity(self)


        #if not self.photos:  #len(self.photos) must be > 0.
        #    raise FolderError(directory)

        self.index = 0  #Index of next photo to draw in self.photos.
        self.current_image = False  #Start with no image drawn on screen.

        self.current_photo = False
        self.currentimg = False

        #center position of photos on screen.
        self.center = (self.screen[0]+add_width)//2, (self.screen[1]+ctrl_height//3)//2


        # self.speed corresponds to the replayed "frames per second"
        if hasattr(self, 'speed'):
            pass
        else:
            self.speed = 100 # initialize with 100 frames per second  

        self.master, self.directory = master, directory

        self.stop = 0 # variable to stop if spacebar gets hit 

        # Label displaying FPS  
        #self.labeltext = tk.StringVar()
        #self.labeltext.set('playback speed [FPS]: ' + str(self.speed))
        #self.label = tk.Label(self.frame, textvariable=self.labeltext)
        #self.label.pack(side=tk.TOP)



    def animate(self):

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
        #if (self.tabindex):
        #    self.frame.destroy()




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
            self.refreshing = 1
            self.frame.destroy()
            self.__init__(self.master, self.directory,self.refreshing,self.roiseq,self.seqlength,self.roiobj)
            self.animate()
            self.stop = 0
            self.refreshing = 0 # as refreshing ends here  
        """

        if (self.selectroi == 1):
            def on_mouse_down(event):
                self.anchor = (self.can.canvasx(event.x), self.can.canvasy(event.y))
                self.item = None
            def on_mouse_drag(event):
                self.bbox = self.anchor + (self.can.canvasx(event.x), self.can.canvasy(event.y))
                self.ROI = self.bbox
                #print "self.ROI "
                #print self.ROI
                if self.item is None:
                    self.item = self.can.create_rectangle(self.bbox, outline="yellow")
                else:
                    self.can.coords(self.item, *self.bbox)
            def on_mouse_up(event):
                if self.item:
                    on_mouse_drag(event)
                    box = tuple((int(round(v)) for v in self.can.coords(self.item)))

                # create cropped image sequence in self.roiseq: 
                xroi = sorted([int(self.ROI[0]),int(self.ROI[2])])
                yroi = sorted([int(self.ROI[1]),int(self.ROI[3])])

                nimgs = self.seqlength # number of images
            
                x1,x2 = int(xroi[0]), int(xroi[1])
                y1,y2 = int(yroi[0]), int(yroi[1])
              
        
                self.ROI = list(self.ROI)
                # consider the zoomfactor 
                self.ROI[0] = int(round(self.ROI[0]/self.zoomfac))
                self.ROI[1] = int(round(self.ROI[1]/self.zoomfac))
                self.ROI[2] = int(round(self.ROI[2]/self.zoomfac))
                self.ROI[3] = int(round(self.ROI[3]/self.zoomfac))
                self.ROI = tuple(self.ROI) 
                print self.ROI  

                self.roiseq = [self.PILimgs[i].crop(self.ROI) for i in range(nimgs)]
        
                print "TEST self.roiseq" 
                print type(self.roiseq) 

                # crop ROI/resfresh and finally, animate ROI! 
                self.refreshing = 1
                self.frame.destroy()
                self.selectroi=0
                self.__init__(self.master, self.directory,self.refreshing,self.roiseq,self.seqlength,self.roiobj,self.selectroi)
                self.animate()
                self.stop = 0
                self.refreshing = 0 # as refreshing ends here  


            # add mouse bindings here

            self.can.xview_moveto(0)
            self.can.yview_moveto(0)

            self.can.bind('<ButtonPress-1>', on_mouse_down)
            self.can.bind('<B1-Motion>', on_mouse_drag)
            self.can.bind('<ButtonRelease-1>', on_mouse_up)


        #print "type in flipROI"
        #print type(self.roiseq) 






        if (self.selectroi == 2):
            def on_mouse_down(event):
                self.stop = 2 
                self.anchor = (self.can.canvasx(event.x), self.can.canvasy(event.y))
                
                #print "\n"
                #print "anchor"
                #print self.anchor 
                #print "\n"
                
                
                self.item = None
            
                self.bbox = self.anchor + (self.can.canvasx(event.x)+5, self.can.canvasy(event.y)+5)
                self.ROI = self.bbox
    
                
                self.item = self.can.create_rectangle(self.bbox, fill="yellow")
                
                self.can.coords(self.item, *self.bbox)
                
                box = tuple((int(round(v)) for v in self.can.coords(self.item)))


                self.ROI = list(self.ROI)
                # consider the zoomfactor 
                self.ROI[0] = int(round(self.ROI[0]/self.zoomfac))
                self.ROI[1] = int(round(self.ROI[1]/self.zoomfac))
                self.ROI[2] = int(round(self.ROI[2]/self.zoomfac))
                self.ROI[3] = int(round(self.ROI[3]/self.zoomfac))
                self.ROI = tuple(self.ROI) 
               
                self.roiobj.anchor = self.anchor 
                # Pixel got choosen -> plot! 
                self.roiobj.pixelplots(self.roiseq)
    



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

            #print delay

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

        #if (self.contrast):

        #    self.current_image = self.can.create_image(self.center, 
        #                                          image=self.bytescphotos[self.index]) # draw image! 
        #else:




        #if (self.bbox is not None):
        #    self.can.create_rectangle(self.bbox, outline="yellow")




        #img = ImageTk.PhotoImage(self.PILimgs[self.index])

        #self.current_image = self.can.create_image(self.center, 
                                                  #image=self.photos[self.index]) # draw image! 

        #print type(self.PILimgs[self.index])
        #print self.index
        self.currentimg = self.PILimgs[self.index]

        if (self.bscontrast):
            bytescale(self)




        # resize image according to the user's choice 
        ResizeCurrentImage(self)

        GammaScale(self)
        Sharpen(self)
        Brighten(self)

        self.current_photo = ImageTk.PhotoImage(self.currentimg)
        self.current_image = self.can.create_image(self.center,image=self.current_photo) # draw image! 

        if (self.selectroi == 1):
            if (self.bbox is not None):
                self.can.create_rectangle(self.bbox, outline="yellow")

        if (self.selectroi == 2):
            if (self.bbox is not None):
                self.can.create_rectangle(self.bbox, fill="yellow")



        if (self.stop != 2):
            self.frame.after_idle(self.animate) # recalls self.animate  
        else:
            pass


    def refresh(self):
        """ Destroy current frame. Re-initialize animation. """
        self.refreshing = 1
        self.frame.destroy()
        
        self.__init__(self.master, self.directory,self.refreshing,self.PILimgs,self.seqlength,self.roiobj,self.selectroi)
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





    def sharpener(self):
        self.sharp = float(self.sharpnessB.get())

    def setbrightness(self):
        self.bright = float(self.brightnessB.get())
    def increase_fps(self):
        """ Decrease time between screen redraws. """
        self.speed = self.speed + 1 if self.speed > 1 else 1
        #self.labeltext.set('playback speed [FPS]: ' + str(float(self.speed)))


    def fps_button(self):

        if (self.fps.get() == '1'): self.speed = 10
        if (self.fps.get() == '2'): self.speed = 50
        if (self.fps.get() == '3'): self.speed = 100
        if (self.fps.get() == '4'): self.speed = 200
        if (self.fps.get() == '5'): self.speed = 300

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




