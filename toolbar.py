import tkinter as tk
import avoid_troubles
from PIL import ImageTk
import FlipbookROI

class Toolbar:

    # creates the toolbarframe with its widgets

    def selectdirectory(self):

        avoid_troubles.stop_animation(self.player,self.roiplayer,self.ptrackplayer)

        # ask the user to set a new directory and load the images                 
        self.PIL_ImgSeq.choose_directory()
        self.PIL_ImgSeq.load_imgs() # loads image sequence                             
        # PIL_ImgSeq.sequence[i] now holds the i-th frame (img format: 8 Bits, PIL)

        avoid_troubles.clear_main(self.player,self.roiplayer,self.ptrackplayer)

        self.nbook.select(self.nbook.index(self.roitab))
        refresh = 0
        selectroi = 1

        self.roiplayer.__init__(self.roitab,self.PIL_ImgSeq.directory,refresh,
        self.PIL_ImgSeq.sequence,self.PIL_ImgSeq.seqlength,self.roi,selectroi)

        #print('roiplayer id in Toolbar: ',id(self.roiplayer))
        self.roiplayer.animate()


    def __init__(self,parent,player,roiplayer,ptrackplayer,PIL_ImgSeq,nbook,roitab,roi):

        self.player = player
        self.roiplayer = roiplayer
        self.ptrackplayer = ptrackplayer
        self.PIL_ImgSeq = PIL_ImgSeq
        self.nbook = nbook
        self.roitab = roitab
        self.roi = roi

        self.toolbarframe = tk.Frame(parent) # main frame containing the tools

        # image-Button to select the directory holding the image sequence  
        self.diricon = ImageTk.PhotoImage(file=r"./icons/directory/newdir_small.png")

        self.diriconB = tk.Button(self.toolbarframe,height=16,width=160,\
            text='Open Sequence ',command=self.selectdirectory,\
            image=self.diricon,compound=tk.RIGHT)

        self.diriconB.grid(row=0,column=0)

        # --------------------------------------------------------------------- 
        # Label Widget + Entry Widget for setting the recording speed [FPS] 

        fps_label=tk.Label(self.toolbarframe, text="Recording Speed [FPS] :",\
            anchor='e', font=("Verdana",10),width=22)
        fps_label.grid(row=0,column=3)

        fps_list = [300,200,120,100,30]
        self.fpscombo = tk.ttk.Combobox(self.toolbarframe,values=fps_list,width=5)
        self.fpscombo.current(0)
        self.fpscombo.grid(row=0,column=4)
        # --------------------------------------------------------------------- 

        # ----------------------------------------------------------------------
        # Label and Entry Widget for setting the pixel size in [nm]                    
        pixsize_label=tk.Label(self.toolbarframe,text="Pixelsize [nm] :",\
            width=22,anchor='e',font=("Verdana",10))
        pixsize_label.grid(row=0,column=5)

        pixsize_list = [345, 173, 86, 4500,1]
        self.pixsizecombo = tk.ttk.Combobox(self.toolbarframe,values=pixsize_list,width=5)
        self.pixsizecombo.grid(row=0,column=6)
        self.pixsizecombo.current(0)
        # ----------------------------------------------------------------------


