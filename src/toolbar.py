import tkinter as tk
import avoid_troubles
from PIL import ImageTk
import FlipbookROI
import os
import pathlib
import sys
import os.path
import numpy
import cv2


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

            bla = s[0].split("-")
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

	# TODO comment out next line as soon as safe 
    # print(l)


class Toolbar:
    """
    Creates the toolbarframe with its widgets
    """

    def selectdirectory(self):

        avoid_troubles.stop_animation(self.player, self.roiplayer, self.ptrackplayer)

        # delete displayed content in CBF tab:
        try:
            self.powerspec.delete_content()
        except:
            pass

        # delete displayed content in activity tab:
        self.activitymap.delete_content()

        # ask the user to set a new directory and load the images                 
        self.PIL_ImgSeq.choose_directory()
        self.PIL_ImgSeq.load_imgs(self.nimgscombo) # loads image sequence                             
        # PIL_ImgSeq.sequence[i] now holds the i-th frame (img format: 8 Bits, PIL)

        avoid_troubles.clear_main(self.player, self.roiplayer, self.ptrackplayer)

        self.nbook.select(self.nbook.index(self.roitab))
        refresh = 0
        selectroi = 1

        try:
            # avoid crash
            self.roiplayer.stop = 2
            # as roiplayer was not None -> destroy frame before it gets rebuilt:
            self.roiplayer.frame.destroy()
        except NameError:
            pass

        self.roiplayer.__init__(self.roitab, self.PIL_ImgSeq.directory, refresh,
            self.PIL_ImgSeq.sequence, self.PIL_ImgSeq.seqlength, self.roi,selectroi)

        # make sure that the rotationangle is set to 0: 
        self.roiplayer.rotationangle = 0.0

        #print('****************************************')
        #print('****************************************')
        #print(self.PIL_ImgSeq.seqlength)
        #print('****************************************')

        # print('roiplayer id in Toolbar: ',id(self.roiplayer))
        self.roiplayer.animate()

    def nextdirectory(self):

        avoid_troubles.stop_animation(self.player, self.roiplayer, self.ptrackplayer)

        # delete displayed content in CBF tab: 
        self.powerspec.delete_content()

        # delete displayed content in activity tab:
        self.activitymap.delete_content()

        # get a list of all subdirectories of the parent directory
        directory = os.path.abspath(self.PIL_ImgSeq.directory)

        parent_path = pathlib.Path(directory).parent
        parent_path = os.path.abspath(parent_path)

        contents = os.listdir(parent_path)
        for i in range(len(contents)):
            #contents[i] = os.path.abspath(os.path.join(parent_path, contents[i]))
            contents[i] = os.path.join(parent_path, contents[i])

        dirlist = []
        for item in contents:
            if os.path.isdir(item):
                dirlist.append(item)

        subdirectories = dirlist
        subdirectories.sort()

        # find the next consecutive directory (relative to the cwd):
        ind=subdirectories.index(directory)

        if (ind+1 < len(subdirectories)):
            next_directory = subdirectories[ind+1]
        else:
            tk.messagebox.showwarning(title='warning',\
                message='You have already analyzed all the sequences. '
                        'The first image sequence is now getting loaded again...')
            next_directory = subdirectories[0]

        self.PIL_ImgSeq.directory = next_directory
        # next line updates the label (displayed path to the new directory) 
        self.PIL_ImgSeq.dirname.set(next_directory)
        # update the displayed filename of the first image
        files = os.listdir(next_directory)
        sort_list(files)
        self.PIL_ImgSeq.fname.set(files[0])

        f = open('previous_directory.dat','w')
        f.write(next_directory) # write choosen directory into file 'f'   
        f.close()

        self.PIL_ImgSeq.load_imgs(self.nimgscombo) # loads image sequence                             
        # PIL_ImgSeq.sequence[i] now holds the i-th frame (img format: 8 Bits, PIL)

        avoid_troubles.clear_main(self.player,self.roiplayer,self.ptrackplayer)

        self.nbook.select(self.nbook.index(self.roitab))
        refresh = 0
        selectroi = 1

        self.roiplayer.__init__(self.roitab,self.PIL_ImgSeq.directory,refresh,
        self.PIL_ImgSeq.sequence,self.PIL_ImgSeq.seqlength,self.roi,selectroi)

        # make sure that the rotationangle is set to 0:
        self.roiplayer.rotationangle = 0.0

        # update label in statusbar:
        self.statusbar.update(self.PIL_ImgSeq)

        #print('roiplayer id in Toolbar: ',id(self.roiplayer))
        self.roiplayer.animate()

    def read_video(self):
        """
        This function loads videos in most common video formats (without ffmpeg)
        """

        """"
        #######################################################################
        # ---------------------------------------------------------------------
        # The following lines are obsolete
        # The code has been rewritten so that videos can also be read without
        # the help of ffmpeg
        # ---------------------------------------------------------------------
        try:
            self.PIL_ImgSeq.video_to_sequence(self.fpscombo.get())
            self.PIL_ImgSeq.load_imgs()

            avoid_troubles.clear_main(self.player,self.roiplayer,self.ptrackplayer)

            self.nbook.select(self.nbook.index(self.roitab))
            refresh = 0
            selectroi = 1

            self.roiplayer.__init__(self.roitab,self.PIL_ImgSeq.directory,refresh,
            self.PIL_ImgSeq.sequence,self.PIL_ImgSeq.seqlength,self.roi,selectroi)

            # make sure that the rotationangle is set to 0:
            self.roiplayer.rotationangle = 0.0
            self.roiplayer.animate()

        except:
            # in case ffmpeg is not installed --> use opencv2
            pass
        #######################################################################
        """

        avoid_troubles.stop_animation(self.player, self.roiplayer, self.ptrackplayer)

        # delete displayed content in CBF tab: 
        self.powerspec.delete_content()

        # delete displayed content in activity tab:
        self.activitymap.delete_content()

        self.PIL_ImgSeq.load_video(self.fpscombo.get())

        # display video
        avoid_troubles.clear_main(self.player,self.roiplayer,self.ptrackplayer)

        self.nbook.select(self.nbook.index(self.roitab))
        refresh = 0
        selectroi = 1

        self.roiplayer.__init__(self.roitab,self.PIL_ImgSeq.directory,refresh,
        self.PIL_ImgSeq.sequence,self.PIL_ImgSeq.seqlength,self.roi,selectroi)

        # make sure that the rotationangle is set to 0:
        self.roiplayer.rotationangle = 0.0
        self.roiplayer.animate()


    def __init__(self, parent, player, roiplayer, ptrackplayer, PIL_ImgSeq,
            nbook, roitab, roi, toolbar_h, toolbar_w, statusbar, powerspec,activitymap):

        self.player = player
        self.roiplayer = roiplayer
        self.ptrackplayer = ptrackplayer
        self.PIL_ImgSeq = PIL_ImgSeq
        self.nbook = nbook
        self.roitab = roitab
        self.roi = roi
        self.statusbar = statusbar

        self.activitymap = activitymap

        # Here we bind powerspec referring to Powerspec.powerspec object
        # When opening/jumping new directory or selecting a new video, 
        # its delete_content method will be called to remove displayed content
        self.powerspec = powerspec

        # main frame containing the tools:
        self.toolbarframe = tk.Frame(parent,width=toolbar_w,height=toolbar_h)
        #print(self.toolbarframe.winfo_screenwidth())

        # image-Button to select the directory holding the image sequence  
        self.diricon = ImageTk.PhotoImage(file=r"../images/icons/directory/newdir2.png")

        self.diriconB = tk.Button(self.toolbarframe,height=25,width=33,\
            borderwidth=0,command=self.selectdirectory,image=self.diricon)
        self.diriconB.place(in_=self.toolbarframe, anchor='c', x=30, rely=0.5)

        # --------------------------------------------------------------------- 
        # image-Button 'next directory' to select the next subdirectory 
        self.nextdiricon = ImageTk.PhotoImage(
            file=r"../images/icons/directory/nextdir.png")

        self.nextdiriconB = tk.Button(self.toolbarframe,height=25,width=33,\
            borderwidth=0,command=self.nextdirectory,image=self.nextdiricon)
        self.nextdiriconB.place(in_=self.toolbarframe, anchor='e', x=100, rely=0.5)
        #grid(row=0,column=1,padx=7,pady=3,sticky='e')

        # Label Widget + Entry Widget for setting the recording speed [FPS] 

        fps_label=tk.Label(self.toolbarframe, text="Recording Speed [fps] :",\
            anchor='e', font=("TkDefaultFont",10),width=22)
        fps_label.place(in_=self.toolbarframe, anchor='c', x=300, rely=0.5)
        #grid(row=0,column=3,padx=5,sticky='W')

        # read fps_defaults.txt (if it exists)
        if (os.path.exists('fps_defaults.txt')):
            with open('fps_defaults.txt') as f:
                fps_defaults = f.readlines()
                fps_defaults = [line.rstrip() for line in fps_defaults]
                fps_list = fps_defaults
        else:
            fps_list = []

        if (len(fps_list) < 5):
            fps_list = [300, 200, 120, 100, 30]
            if (os.path.exists('fps_defaults.txt')):
                os.remove('fps_defaults.txt')
            f = open('fps_defaults.txt','a')
            f.write(str(fps_list[0])+"\n")
            f.write(str(fps_list[1])+"\n")
            f.write(str(fps_list[2])+"\n")
            f.write(str(fps_list[3])+"\n")
            f.write(str(fps_list[4])+"\n")
            f.close()

        self.fpscombo = tk.ttk.Combobox(self.toolbarframe,values=fps_list,width=5)
        self.fpscombo.current(0)
        self.fpscombo.place(in_=self.toolbarframe, anchor='c', x=420,rely=0.5)
        #grid(row=0,column=4,sticky='W')
        # --------------------------------------------------------------------- 

        # ---------------------------------------------------------------------
        # Add image Button 'load video' 
        self.loadvideo_icon = ImageTk.PhotoImage(
            file=r"../images/icons/newmovieicon.png")

        self.loadvideoB = tk.Button(self.toolbarframe, height=25, width=30,
            borderwidth=0,command=self.read_video,image=self.loadvideo_icon)
        self.loadvideoB.place(in_=self.toolbarframe, anchor='c', x=130, rely=0.5)
        #grid(row=0, column=2, padx=7,pady=3,sticky='e')

        # ---------------------------------------------------------------------
        # Add Label and Entry Widget for setting the pixel size in [nm]  

        pixsize_label=tk.Label(self.toolbarframe,text="Pixelsize [nm] :",\
            width=22,anchor='e',font=("TkDefaultFont",10))
        pixsize_label.place(in_=self.toolbarframe, anchor='c', x=550, rely=0.5)
        #grid(row=0,column=5,sticky='W')

        # read pixelsize_defaults.txt (if it exists)
        if (os.path.exists('pixelsize_defaults.txt')):
            with open('pixelsize_defaults.txt') as f:
                pixelsize_defaults = f.readlines()
                pixelsize_defaults = [line.rstrip() for line in pixelsize_defaults]
                pixelsize_list = pixelsize_defaults
        else:
            pixelsize_list = []

        if (len(pixelsize_list) < 5):
            pixelsize_list = [1779, 345, 173, 86, 1000]

            if (os.path.exists('pixelsize_defaults.txt')):
                os.remove('pixelsize_defaults.txt')
            f = open('pixelsize_defaults.txt','a')
            f.write(str(pixelsize_list[0])+"\n")
            f.write(str(pixelsize_list[1])+"\n")
            f.write(str(pixelsize_list[2])+"\n")
            f.write(str(pixelsize_list[3])+"\n")
            f.write(str(pixelsize_list[4])+"\n")
            f.close()

        self.pixsizecombo = tk.ttk.Combobox(self.toolbarframe,values=pixelsize_list,width=5)
        self.pixsizecombo.place(in_=self.toolbarframe, anchor='c', x=680, rely=0.5)
        #grid(row=0,column=6,padx=5,sticky='W')
        self.pixsizecombo.current(0)
        # ---------------------------------------------------------------------

        # Add label and entry widget to set the number of images to be read in
        nimgs_label=tk.Label(self.toolbarframe, text=" Read first # images: ",\
            width=18,anchor='c',font=("TkDefaultFont",10))
        nimgs_label.place(in_=self.toolbarframe, anchor='c', x=800, rely=0.5)

        # read nimgs_defaults.txt (if it exists)
        if (os.path.exists('nimgs_defaults.txt')):
            with open('nimgs_defaults.txt') as f:
                nimgs_defaults = f.readlines()
                nimgs_defaults = [line.rstrip() for line in nimgs_defaults]
                nimgs_list = nimgs_defaults
        else:
            nimgs_list = []

        if (len(nimgs_list) < 3):
            nimgs_list = ['all', 300, 600]

            if (os.path.exists('nimgs_defaults.txt')):
                os.remove('nimgs_defaults.txt')
            f = open('nimgs_defaults.txt','a')
            f.write(str(nimgs_list[0])+"\n")
            f.write(str(nimgs_list[1])+"\n")
            f.write(str(nimgs_list[2])+"\n")
            f.close()

        self.nimgscombo = tk.ttk.Combobox(self.toolbarframe,values=nimgs_list,width=4)
        self.nimgscombo.place(in_=self.toolbarframe, anchor='c', x=900, rely=0.5)
        self.nimgscombo.current(0)

        # ---------------------------------------------------------------------
        # Add combobox to indicate whether Reflection or Transmission was used

        mod = ['Transmission', 'Reflection']
        self.modcombo = tk.ttk.Combobox(self.toolbarframe, values=mod, width=11)
        self.modcombo.place(in_=self.toolbarframe, anchor='c', x=1100, rely=0.5)
        self.modcombo.current(0)







