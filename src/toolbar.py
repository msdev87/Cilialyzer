import tkinter as tk
import avoid_troubles
from PIL import ImageTk
import FlipbookROI
import os
import pathlib
import sys



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

        # ask the user to set a new directory and load the images                 
        self.PIL_ImgSeq.choose_directory()
        self.PIL_ImgSeq.load_imgs() # loads image sequence                             
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

        # print('roiplayer id in Toolbar: ',id(self.roiplayer))
        self.roiplayer.animate()

    def nextdirectory(self):

        avoid_troubles.stop_animation(self.player, self.roiplayer, self.ptrackplayer)

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

        self.PIL_ImgSeq.load_imgs() # loads image sequence                             
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
            # in case ffmpeg is not installed 
            pass


    def __init__(self, parent, player, roiplayer, ptrackplayer, PIL_ImgSeq,
            nbook, roitab, roi, toolbar_h, toolbar_w, statusbar):

        self.player = player
        self.roiplayer = roiplayer
        self.ptrackplayer = ptrackplayer
        self.PIL_ImgSeq = PIL_ImgSeq
        self.nbook = nbook
        self.roitab = roitab
        self.roi = roi
        self.statusbar = statusbar

        self.toolbarframe = tk.Frame(parent,width=toolbar_w,height=toolbar_h) # main frame containing the tools
        #print('test')
        #print(self.toolbarframe.winfo_screenwidth())

        # image-Button to select the directory holding the image sequence  
        self.diricon = ImageTk.PhotoImage(file=r"../images/icons/directory/newdir2.png")

        self.diriconB = tk.Button(self.toolbarframe,height=25,width=33,\
            borderwidth=0,command=self.selectdirectory,image=self.diricon)
        self.diriconB.grid(row=0,column=0,padx=7,pady=3,sticky='e')

        # --------------------------------------------------------------------- 
        # image-Button 'next directory' to select the next subdirectory 
        self.nextdiricon = ImageTk.PhotoImage(
            file=r"../images/icons/directory/nextdir.png")

        self.nextdiriconB = tk.Button(self.toolbarframe,height=25,width=33,\
            borderwidth=0,command=self.nextdirectory,image=self.nextdiricon)
        self.nextdiriconB.grid(row=0,column=1,padx=7,pady=3,sticky='e')

        # Label Widget + Entry Widget for setting the recording speed [FPS] 

        fps_label=tk.Label(self.toolbarframe, text="Recording Speed [fps] :",\
            anchor='e', font=("TkDefaultFont",10),width=22)
        fps_label.grid(row=0,column=3,padx=5,sticky='W')

        fps_list = [300,200,120,100,30]
        self.fpscombo = tk.ttk.Combobox(self.toolbarframe,values=fps_list,width=5)
        self.fpscombo.current(0)
        self.fpscombo.grid(row=0,column=4,sticky='W')
        # --------------------------------------------------------------------- 


        # ---------------------------------------------------------------------
        # Add image Button 'load video' 
        self.loadvideo_icon = ImageTk.PhotoImage(
            file=r"../images/icons/newmovieicon.png")

        self.loadvideoB = tk.Button(self.toolbarframe, height=25, width=30,
            borderwidth=0,command=self.read_video,image=self.loadvideo_icon)
        self.loadvideoB.grid(row=0, column=2, padx=7,pady=3,sticky='e')




        # ----------------------------------------------------------------------
        # Label and Entry Widget for setting the pixel size in [nm]                    
        pixsize_label=tk.Label(self.toolbarframe,text="Pixelsize [nm] :",\
            width=22,anchor='e',font=("TkDefaultFont",10))
        pixsize_label.grid(row=0,column=5,sticky='W')

        pixsize_list = [1779, 345, 173, 86, 4500,1]
        self.pixsizecombo = tk.ttk.Combobox(self.toolbarframe,values=pixsize_list,width=5)
        self.pixsizecombo.grid(row=0,column=6,padx=5,sticky='W')
        self.pixsizecombo.current(0)
        # ----------------------------------------------------------------------
