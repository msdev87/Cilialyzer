from PIL import ImageTk
import os, io
import Flipbook
import PIL
import PIL.Image

if os.sys.version_info.major > 2:
    from tkinter import *
    from tkinter.filedialog import askdirectory
else:
    from tkinter import *
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog   import asksaveasfilename

class ROI:
    # class for ROI selection
    def __init__(self,root):

        # tuple holding the edges of the ROI selection! 
        self.ROI = (0,0,0,0)
        self.root = root # Tk() root 
        self.roiseq = None # cropped image sequence

        # helper variables
        self.anchor = None
        self.item = None
        self.bbox = None
        self.win = None # Toplevel() toplevel window  

    def get_roi(self,PILSeq):

        # get_roi gets executed when the button 'Get ROI' is getting clicked  

        self.directory = PILSeq.directory
        print("directory argument set to : " + self.directory)

        # mouse event bindings 
        def on_mouse_down(event):
            self.anchor = (event.widget.canvasx(event.x), event.widget.canvasy(event.y))
            self.item = None

        def on_mouse_drag(event):
            self.bbox = self.anchor + (event.widget.canvasx(event.x), event.widget.canvasy(event.y))
            self.ROI = self.bbox
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

            print("xroi", xroi)

            nimgs = len(PILSeq.sequence) # number of images
            print("nr images ", nimgs)
            x1,x2 = int(xroi[0]), int(xroi[1])
            y1,y2 = int(yroi[0]), int(yroi[1])
            #print type(x1)
            #print type(y2)
            #print type(nimgs)
            print("ROI : ", self.ROI)
            self.roiseq = [PILSeq.sequence[i].crop(self.ROI) for i in range(nimgs)]
            self.win.destroy()



        # plot first image of image stack!
        files = list(Flipbook.get_files(self.directory)) # files is a sorted generator

        #nr_files = len(files)

        # get image size!
        first_file = files[0]

        with open(first_file, "rb") as f:
            fh = io.BytesIO(f.read())
            img = PIL.Image.open(fh, mode="r")
            w, h = img.size

        #t0=time.time()
        first_image = img.convert("L") # converts first_image to 8 Bit mono

        # show first image of sequence
        first_photo = ImageTk.PhotoImage(first_image)
        self.win = Toplevel() # canvas shall be placed into roi_win
        frame = Frame(self.win)
        frame.pack(fill=BOTH)
        roi_can = Canvas(frame,width=w,height=h)
        roi_can.pack(fill=BOTH)


        roi_can.xview_moveto(0)
        roi_can.yview_moveto(0)

        roi_can.create_image(0,0,image=first_photo,anchor='nw') # draw first_photo on canvas 
        roi_can.img = first_photo

        roi_can.bind('<ButtonPress-1>', on_mouse_down)
        roi_can.bind('<B1-Motion>', on_mouse_drag)
        roi_can.bind('<ButtonRelease-1>', on_mouse_up)




