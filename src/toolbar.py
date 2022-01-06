import tkinter as tk
import avoid_troubles
from PIL import ImageTk
import FlipbookROI
import os
import pathlib

class Toolbar:

    # creates the toolbarframe with its widgets

    def selectdirectory(self):

        avoid_troubles.stop_animation(self.player, self.roiplayer, self.ptrackplayer)

        # ask the user to set a new directory and load the images                 
        self.PIL_ImgSeq.choose_directory()
        self.PIL_ImgSeq.load_imgs() # loads image sequence                             
        # PIL_ImgSeq.sequence[i] now holds the i-th frame (img format: 8 Bits, PIL)

        avoid_troubles.clear_main(self.player,self.roiplayer,self.ptrackplayer)

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

        #print('roiplayer id in Toolbar: ',id(self.roiplayer))
        self.roiplayer.animate()

    def nextdirectory(self):

        avoid_troubles.stop_animation(self.player, self.roiplayer, self.ptrackplayer)

        # get a list of all subdirectories of the parent directory
        directory = self.PIL_ImgSeq.directory

        parent_path = pathlib.Path(directory).parent
        parent_path = os.path.abspath(parent_path)
        print('*****************************')
        print(os.path.abspath(os.path.join(directory, os.pardir)))
        print('*****************************')

        contents = os.listdir(parent_path)
        print('parent_path:')
        print(parent_path)
        print('--------')


        for i in range(len(contents)):
            contents[i] = os.path.abspath(os.path.join(parent_path, contents[i]))

        print('contents again:')
        print(contents)

        subdirectories=[]

        for item in contents:
            if os.path.isdir(item):
                subdirectories.append(item)

        subdirectories.sort()

        print('test')
        print(subdirectories)
        print(directory)
        print('--------------------')


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
        self.PIL_ImgSeq.dirname.set(next_directory)

        f = open('user_settings.dat','w')
        f.write(next_directory) # write choosen directory into file 'f'   
        f.close()

        # update the label, which displays the directory name:            
        #self.dirname.set(self.directory)                                  

        # update the name of the first image:                             
        #f = os.listdir(self.directory)                                    

        self.PIL_ImgSeq.load_imgs() # loads image sequence                             
        # PIL_ImgSeq.sequence[i] now holds the i-th frame (img format: 8 Bits, PIL)

        avoid_troubles.clear_main(self.player,self.roiplayer,self.ptrackplayer)

        self.nbook.select(self.nbook.index(self.roitab))
        refresh = 0
        selectroi = 1

        self.roiplayer.__init__(self.roitab,self.PIL_ImgSeq.directory,refresh,
        self.PIL_ImgSeq.sequence,self.PIL_ImgSeq.seqlength,self.roi,selectroi)

        # update label in statusbar:
        self.statusbar.update(self.PIL_ImgSeq)

        #print('roiplayer id in Toolbar: ',id(self.roiplayer))
        self.roiplayer.animate()

    def __init__(self, parent, player, roiplayer, ptrackplayer, PIL_ImgSeq, nbook, roitab, roi, toolbar_h, toolbar_w, statusbar):

        self.player = player
        self.roiplayer = roiplayer
        self.ptrackplayer = ptrackplayer
        self.PIL_ImgSeq = PIL_ImgSeq
        self.nbook = nbook
        self.roitab = roitab
        self.roi = roi
        self.statusbar = statusbar

        self.toolbarframe = tk.Frame(parent,width=toolbar_w,height=toolbar_h) # main frame containing the tools
        print('test')
        print(self.toolbarframe.winfo_screenwidth())

        # image-Button to select the directory holding the image sequence  
        self.diricon = ImageTk.PhotoImage(file=r"../images/icons/directory/newdir2.png")
        self.diriconB = tk.Button(self.toolbarframe,height=23,width=30,\
            borderwidth=0,command=self.selectdirectory,image=self.diricon)
        self.diriconB.grid(row=0,column=0,padx=5,pady=3,sticky='e')

        # --------------------------------------------------------------------- 
        # image-Button 'next directory' to select the next subdirectory 
        self.nextdiricon = ImageTk.PhotoImage(file=r"../images/icons/directory/nextdir.png")

        self.nextdiriconB = tk.Button(self.toolbarframe,height=23,width=30,\
            borderwidth=0,command=self.nextdirectory,image=self.nextdiricon)
        self.nextdiriconB.grid(row=0,column=1,padx=5,pady=3,sticky='e')

        # Label Widget + Entry Widget for setting the recording speed [FPS] 

        fps_label=tk.Label(self.toolbarframe, text="Recording Speed [fps] :",\
            anchor='e', font=("TkDefaultFont",10),width=22)
        fps_label.grid(row=0,column=3,padx=5,sticky='W')

        fps_list = [300,200,120,100,30]
        self.fpscombo = tk.ttk.Combobox(self.toolbarframe,values=fps_list,width=5)
        self.fpscombo.current(0)
        self.fpscombo.grid(row=0,column=4,sticky='W')
        # --------------------------------------------------------------------- 

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


