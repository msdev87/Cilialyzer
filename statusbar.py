import avoid_troubles
import tkinter as tk
from PIL import ImageTk
import pathlib

class StatusBar:

    def endprogram(self):
        self.ctrl_panel.quit()

    def update(self,PIL_ImgSeq):
        self.dirname.set(PIL_ImgSeq.dirname.get())

    def __init__(self,parent,bar_w,bar_h,ctrl_panel,PIL_ImgSeq):

        self.statusbarframe = tk.Frame(parent,width=bar_w,height=bar_h,bg='gray92')
        self.ctrl_panel = ctrl_panel
        self.dirname = PIL_ImgSeq.dirname


        # Quit Button (placed in the bottom right edge of the root window)              
        self.exitphoto = ImageTk.PhotoImage(file=r"./icons/exit/exit_small.png")
        self.quitB=tk.Button(self.statusbarframe,image=self.exitphoto,command=self.endprogram,height=26,width=53,borderwidth=0)
        self.quitB.grid(row=0,column=1,columnspan=1,sticky='e',padx=3,pady=3)


        dirname_label = tk.Label(self.statusbarframe,textvariable=self.dirname,anchor='center',\
            font=("Verdana",10))
        dirname_label.grid(row=0,column=0)
        self.statusbarframe.grid_columnconfigure(0,weight=1) 





