# ==============================================================================
#
# This is the main loop of the "Cilialyzer" software 
#
# Purpose: provides a comfortable tool for clinicians to assess 
# the health status of the mucociliary transport mechanism 
# by quantitatively characterizing the (muco)ciliary motion  
#
# Author: 
# Martin Schneiter, University of Bern, Switzerland  
# Mail: martin.schneiter@gmx.ch 
# Cell phone: +41 78 896 16 10 
# 
# ==============================================================================


# ******************************************************************************
# ******************** Configuration of The main Window ************************
# ******************************************************************************

# Configure which tabs should be made available when launching the application 

# Tab to view the sequence 
AnimateSequence = 1

# Tab to select a ROI 
ROISelection = 1

# Tab to generate the (ROI-based) power spectral density [PSD]  
CBF = 1

# Tab to generate the activity map (ROI-based, PSD-based)  
ActivityMap = 1

# Tab to analyze single pixels 
SinglePixelAnalysis = 0

MotionTracking = 0

ParticleTracking = 1

DynamicFiltering = 0

SpatioTemporalCorrelogram = 0

kSpectrum = 0

# ******************************************************************************
# ******************************************************************************

# ---------------------- import necessary modules ------------------------------
import FlipbookROI
import math
import getline
import io, os
from PIL import ImageTk
import PIL.Image
import webbrowser
import warnings
from tkinter import *
import numpy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import time
import tkinter.messagebox
import pylab as pl
from matplotlib.patches import Rectangle
import Flipbook

import DynamicFilter
import FlipbookPTrack
# ------------------------------------------------------------------------------

# ------------------------------------------ animation -------------------------
def animate_roi():

    win = Toplevel()
    refresh = 0
    player = Flipbook.ImgSeqPlayer(win,PIL_ImgSeq.directory,refresh,
									roiplayer.roiseq,PIL_ImgSeq.seqlength)
    player.animate() # call method animate 



def animation():

    window = animationtab 
    refresh = 0    
    player = Flipbook.ImgSeqPlayer(window,PIL_ImgSeq.directory,refresh,PIL_ImgSeq.sequence,PIL_ImgSeq.seqlength) 




# ------------------------------------------------------------------------------

#def set_fps(event):
#    global FPS
#    FPS = eval(enter_fps.get())

#def set_pixsize(event):
#    global pixsize 
#    pixsize = eval(enter_pixsize.get()) 

def helpbutton():
    webbrowser.open_new(r'./Doc/help.pdf')


def endprogram():

    global player, roiplayer

    try:
        # next line avoids crash 
        player.stop = 2
        player.frame.destroy()
    except NameError:
        pass
    try:
        # avoid crash 
        roiplayer.stop = 2
        roiplayer.frame.destroy()
    except NameError:
        pass
    ctrl_panel.quit()


#def set_peakmin():
#    global peakmin
#    peakmin = sbox_peakmin.get()
#    plot_peak()
#def set_peakmax():
#    global peakmax
#    peakmax = sbox_peakmax.get()
#    plot_peak()



def peak_cbf():
    global powerspec_photo
    powerspectrum.peakselection(powerspecplot)
    #print "peak selected"
    #if powerspectrum.cbf_high is not None:
    powerspectrum.get_cbf(PIL_ImgSeq.seqlength,fpscombo.get())
    # anzeige des Powerspektrums in frontend (nbook) 
    #time.sleep(10) 
    powerspec_photo = ImageTk.PhotoImage(file=r"./powerspec.png") 
    can1.itemconfig(pscan, image=powerspec_photo)  



def spatialacorr():
    global spatialacorr_photo, pixsize  
    poi.GetSpatialAcorr(pixsizecombo.get()) 
    spatialacorr_photo = ImageTk.PhotoImage(file=r"./spatialacorr.png") 
    can2.itemconfig(sacorrcan, image=spatialacorr_photo)  
    nbook.select(sacorr)  


def tempacorr(): 
    global tempacorr_photo 
    poi.GetTempAcorr(fpscombo.get())
    tempacorr_photo = ImageTk.PhotoImage(file=r"./tempacorr.png")
    can3.itemconfig(tacorrcan, image=tempacorr_photo)
    nbook.select(tacorr) 


def loadvideo():

    global player,roiplayer

    try:
        # avoid crash 
        player.stop = 2
    except NameError:
        pass

    try:
        # avoid crash 
        roiplayer.stop = 2
    except NameError:
        pass

    PIL_ImgSeq.load_video(dirname,fpscombo.get())
    PIL_ImgSeq.load_imgs()

    try:
        player.frame.destroy()
    except NameError:
        pass

    try:
        roiplayer.frame.destroy()
    except NameError:
        pass

    # delete 'roiplayer' object
    try:
        del roiplayer
    except NameError:
        pass

    # delete content of powerspec tab, before switching to animation 
    powerspectrum.tkframe.destroy()

    # switch to animation tab
    nbook.select(0)
    refresh = 0
    player = Flipbook.ImgSeqPlayer(animationtab, PIL_ImgSeq.directory,\
                                   refresh,PIL_ImgSeq.sequence,\
                                   PIL_ImgSeq.seqlength)
    player.animate() # call method animate 

def selectdirectory():

    global player,roiplayer

    try:
        # avoid crash 
        player.stop = 2
    except NameError:
        pass

    try:
        # avoid crash 
        roiplayer.stop = 2
    except NameError:
        pass

    # ask the user to set a new directory 
    PIL_ImgSeq.choose_directory(dirname,fname)
    PIL_ImgSeq.load_imgs()

    # new directory is set -> destroy frames 
    try:
        player.frame.destroy()
    except NameError:
        pass

    try:
        roiplayer.frame.destroy()
    except NameError:
        pass

    # delete 'roiplayer' object
    try:
        del roiplayer
    except NameError:
        pass

    # delete content of powerspec tab, before switching to animation 
    powerspectrum.tkframe.destroy()

    # switch to animation tab
    nbook.select(0)
    refresh = 0
    player = Flipbook.ImgSeqPlayer(animationtab, PIL_ImgSeq.directory,\
                                   refresh,PIL_ImgSeq.sequence,\
                                   PIL_ImgSeq.seqlength)
    player.animate() # call method animate 


def corrgram():

    # calculate spatio-temporal autocorrelation 

    try: 
        dynseq.spatiotempcorr(float(fpscombo.get()),float(minscale.get()),float(maxscale.get()))
    except NameError:
        print("namerror") 
        dynseq = DynamicFilter.DynFilter() 
        dynseq.dyn_roiseq = roiplayer.roiseq
        dynseq.spatiotempcorr(float(fpscombo.get()),float(minscale.get()),float(maxscale.get()))

    print("spatiotempcorr calculated")        
    #print "spatiotempcorr calculated" 
    refresh = 0    
    corrplayer = Flipbook.ImgSeqPlayer(correlationtab,PIL_ImgSeq.directory, refresh,dynseq.corr_roiseq,len(dynseq.corr_roiseq)) 
    corrplayer.animate() 



def meanscorrgram():
    global dynseq

    # calculate the mean spatial autocorrelation 
    try: 
        dynseq.mscorr(float(fpscombo.get()),float(minscale.get()),float(maxscale.get()),mscorrplotframe,mscorrprofileframe,float(pixsizecombo.get()))

    except NameError:
        print('except')
        dynseq = DynamicFilter.DynFilter() 
        dynseq.dyn_roiseq = roiplayer.roiseq
        dynseq.mscorr(float(fpscombo.get()),float(minscale.get()),float(maxscale.get()),mscorrplotframe,mscorrprofileframe,float(pixsizecombo.get()))





def kspec():
    # calculate the spatial power spectral density
    global dynseq 
    try:
        dynseq.kspec(float(fpscombo.get()),float(minscale.get()),float(maxscale.get()),kplotframe)
    except NameError:
        print("namerror") 
        dynseq = DynamicFilter.DynFilter() 
        dynseq.dyn_roiseq = roiplayer.roiseq  
        dynseq.kspec(float(fpscombo.get()),float(minscale.get()),float(maxscale.get()),kplotframe)



def select_roi():
 
    global roiplayer
    try: 
        # avoid crash 
        roiplayer.stop = 2
        # as roiplayer was not None -> destroy frame before it gets rebuilt:
        roiplayer.frame.destroy() 
    except NameError:
        pass

    refresh = 0
    selectroi = 1
    roiplayer = FlipbookROI.ImgSeqPlayer(roitab,PIL_ImgSeq.directory,refresh,PIL_ImgSeq.sequence,PIL_ImgSeq.seqlength,roi,selectroi) 
    roiplayer.animate()

    
def select_pixel():
    global roiplayer 
    
    #print "this is a test" 
    
    try: 
        # avoid crash 
        pixplayer.stop = 2
#        # as roiplayer was not None -> destroy frame before it gets rebuilt:
        pixplayer.frame.destroy() 
    except NameError:
        pass

    refresh = 0
    selectroi = 2 # selectroi = 2 -> pixel selection
    pixplayer = FlipbookROI.ImgSeqPlayer(pixelchoiceframe,PIL_ImgSeq.directory,refresh,roiplayer.roiseq,PIL_ImgSeq.seqlength,pixoi,selectroi) 
    pixplayer.animate()
    
    #print " second test " 
    


def pcolor_func():
	pass 



def switchtab(event):

    global player, roiplayer   
    
    # if tab is pressed (and pressed tab != active tab) then take precautions...  

    clicked_tab = nbook.tk.call(nbook._w, "identify", "tab", event.x, event.y)
    active_tab = nbook.index(nbook.select())

    #print("clicked tab: ", clicked_tab) 

    if ((active_tab == nbook.index(animationtab)) and (clicked_tab != active_tab)):    
        try:
            # stop the player to prevent a crash 
            player.stop = 2  
        except NameError:
            pass
        
    if ((active_tab == nbook.index(roitab)) and (clicked_tab != active_tab)): 
        try:
            # stop the player to prevent a crash 
            roiplayer.stop = 2  
        except NameError:
            pass
        
    if ((active_tab == nbook.index(ptracktab)) and (clicked_tab != active_tab)):
        # stop the player to prevent a crash  
        try: 
            ptrackplayer.stop = 2 
        except NameError:
            pass


    # if ((active_tab == 7) and (clicked_tab != active_tab)):
    #    try: 
    #        dynplayer.stop = 2 
    #    except NameError:
    #        pass
           

    if (clicked_tab == nbook.index(roitab)):

        # ROI Selection tab got activated



        # if dynamically filtered sequence available -> substitue roiseq with 
        # dyn. filtered seq 
        try: 
            if (len(dynseq.dyn_roiseq) > 0):
                PIL_ImgSeq.sequence = dynseq.dyn_roiseq 
        except: 
            pass 


        try:
            roiplayer.stop = 0 
        except:
            try:         
                nbook.select(nbook.index(roitab))
                refresh = 0
                selectroi = 1
                roiplayer = FlipbookROI.ImgSeqPlayer(roitab,PIL_ImgSeq.directory,\
                                                 refresh,PIL_ImgSeq.sequence,\
                                                 PIL_ImgSeq.seqlength,roi,selectroi) 
                roiplayer.animate()
            except: 
                pass 


    if (clicked_tab == nbook.index(ptracktab)):
        # particle tracking tab got selected  
        nbook.select(nbook.index(ptracktab))  
        # create player object 
        refresh = 0 
        selectroi = 1 
        ptrackplayer = FlipbookPTrack.ImgSeqPlayer(ptracktab,PIL_ImgSeq.directory,\
                                                 refresh,roiplayer.roiseq,\
                                                 PIL_ImgSeq.seqlength,roi,selectroi,float(fpscombo.get()),float(pixsizecombo.get())) 
        ptrackplayer.animate()
    
    
    
    
    if (clicked_tab == nbook.index(dynfiltertab)): 
        # dynamic filtering tab 
        nbook.select(nbook.index(dynfiltertab))
        # 1. apply band-pass filter 
        dynseq.bandpass(roiplayer.roiseq,float(fpscombo.get()),float(minscale.get()),float(maxscale.get()),int(nrharmscombo.get()))
    
        refresh = 0    
        dynplayer = Flipbook.ImgSeqPlayer(dynfiltertab, PIL_ImgSeq.directory,\
                                   refresh,dynseq.dyn_roiseq,\
                                   PIL_ImgSeq.seqlength) 
        dynplayer.animate() # call meth
    
    
    
    
 
    

#def calcplot_powerspec(pwspec,roiseq,fps,specplot,frame):
#    pwspec.calc_powerspec(roiseq,fps,specplot,frame)

def splitkspec(self):
    
    global dynseq  
    # draw the line 
    # according to splitangle 
    #global splitangle 
    #angle = splitlinescale.get() 
    #dynseq.kxkyplotax.plot([3,3],[8,8],color='r',linewidth=4)  
    print('ok')  
    









def peakselector(self):

    # this command gets executed if the user shifts the scrollbars, 
    # which define the min and max freq of the considered freq band, 
    # which is necessary for the determination of the CBF and the activity map 
    
    global powerspectrum, minscale, maxscale, nrharmscombo 
   
    minf = float(minscale.get())
    maxf = float(maxscale.get())

    print(minf) 
    print(maxf) 


    # fill whole area white (to delete prior selections!) 
    powerspectrum.pwspecplot.axes.fill_between(powerspectrum.freqs, powerspectrum.spec,facecolor='white',alpha=1.0)

    
    # shade first harmonic (selection)  
    maxind = numpy.sum((numpy.array(powerspectrum.freqs) <= maxf).astype(int))
    minind = numpy.sum((numpy.array(powerspectrum.freqs) <= minf).astype(int))
    powerspectrum.pwspecplot.axes.fill_between(powerspectrum.freqs[minind:maxind+1], powerspectrum.spec[minind:maxind+1],facecolor='gray',alpha=0.8)   
   
    powerspectrum.pwspecplot.canvas.draw()



    # ------- shade the second and third harmonic (if selected) --------
    
    if (int(nrharmscombo.get()) > 1): 
        
        fpeakw = maxf - minf
        fpeak = minf + 0.5 * fpeakw  
        secondpeakf = 2.0 * fpeak  
        secondminf = secondpeakf - 0.5 * fpeakw  
        secondmaxf = secondpeakf + 0.5 * fpeakw 

        maxind = numpy.sum((numpy.array(powerspectrum.freqs) <= secondmaxf).astype(int))
        minind = numpy.sum((numpy.array(powerspectrum.freqs) <= secondminf).astype(int))
        powerspectrum.pwspecplot.axes.fill_between(powerspectrum.freqs[minind:maxind+1], powerspectrum.spec[minind:maxind+1],facecolor='gray',alpha=0.4)
    
        powerspectrum.pwspecplot.canvas.draw()

    if (int(nrharmscombo.get()) > 2): 
             
        thrdpeakf = 3.0 * fpeak  
        thrdminf = thrdpeakf - 0.5 * fpeakw  
        thrdmaxf = thrdpeakf + 0.5 * fpeakw 

        maxind = numpy.sum((numpy.array(powerspectrum.freqs) <= thrdmaxf).astype(int))
        minind = numpy.sum((numpy.array(powerspectrum.freqs) <= thrdminf).astype(int))
        powerspectrum.pwspecplot.axes.fill_between(powerspectrum.freqs[minind:maxind+1], powerspectrum.spec[minind:maxind+1],facecolor='gray',alpha=0.4)
    
        powerspectrum.pwspecplot.canvas.draw()





# ==============================================================================
# ==============================================================================
# ------- Below the root window and its buttons get created & arranged ---------
# ==============================================================================
# ==============================================================================

# First, we need a Tkinter root window (named as "ctrl_panel"):  
ctrl_panel = Tk()

# set cilialyzer icon
ctrl_panel.iconphoto(False, PhotoImage(file='./logo/logo.png'))


# TODO : menu (for setting/confiuring notebook tabs) 

#menubar = Menu(ctrl_panel)
#show_all = BooleanVar()
#show_all.set(True)
#view_menu = Menu(menubar)
#view_menu.add_checkbutton(label="Show All", onvalue=1, offvalue=0, variable=show_all)
#menubar.add_cascade(label='Configure', menu=view_menu)
#ctrl_panel.config(menu=menubar)



# Set the window title, default size, bg color 
ctrl_panel.title("Cilialyzer")
ctrl_panel.minsize(width=20,height=20)

# the upper left edge of the main window gets created at the coordinates 
# (offset,offset) [in pixels], where the upper left edge of the screen = (0,0)
offset=40

print("test")
print(ctrl_panel.winfo_screenwidth())
print(ctrl_panel.winfo_screenheight())
print("---")

ctrl_panel.geometry("%dx%d+%d+%d"%(
	ctrl_panel.winfo_screenwidth(),ctrl_panel.winfo_screenheight(),0,0))
ctrl_panel.update()
# winfo_screenheight and _screenwidth deliver the display's pixel resolution 



print("ctrl_panel height:")
print(ctrl_panel.winfo_height())
print("ctrl_panel width:")
print(ctrl_panel.winfo_width())



#sys.exit()


ctrl_panel.geometry("%dx%d+%d+%d"%(ctrl_panel.winfo_screenwidth()\
-2*(offset + 5),ctrl_panel.winfo_screenheight()-2*(offset + 5),offset,offset))



# 'screenw, screenh' denote the width, height of the main window  
screenw = ctrl_panel.winfo_screenwidth() - 2*(offset + 5)
screenh = ctrl_panel.winfo_screenheight() - 2*(offset + 5)


# set button size and alignment 
bh = 1  # button height 
bw = 23 # button width  
px = 4  # pad x 
py = 4  # pad y

imgbh = 28 # button height for buttons containing images 
imgbw = 182 # button width for buttons containing images 

# Help Button 
helpB = Button(text='Help',command=helpbutton,height=bh,width=7)
helpB.grid(row=0,column=0,padx=px,pady=py,sticky='n')

# Quit Button (placed in the bottom right edge of the root window)  
exitphoto = ImageTk.PhotoImage(file=r"./icons/exitalpha.png")
quitB=Button(ctrl_panel,image=exitphoto,command=endprogram,height=40,width=78)
quitB.grid(row=1,column=2,columnspan=1,sticky='s',padx=4,pady=4)

#******************** Determine the width of the Notebook *********************# 
ctrl_panel.update() # update to determine the button size in pixels 
emptyspace = 15
nbookw = ctrl_panel.winfo_screenwidth() - helpB.winfo_width() -\
         quitB.winfo_width() - emptyspace - 2*(offset + 5)
#******************************************************************************#

#******************************************************************************#
# ***************** GeneralF (Current Settings - Frame) ********************** #
# the frame at the top of the main window 
# In which we display the current settings (directory, filename, FPS, etc.)
#******************************************************************************#

GeneralF = LabelFrame(text=' Current Settings ',labelanchor='n',borderwidth=2,\
                      padx=5,pady=5,font=("Helvetica",11,"bold"),relief=GROOVE)
GeneralF.grid(row=0,column=1,columnspan=1,rowspan=1)


import LoadSequence
PIL_ImgSeq = LoadSequence.ImageSequence()
# PIL_ImgSeq.directory -> contains path to choosen image sequence 
# PIL_ImgSeq.sequence  -> holds the PIL img sequence 

dirphoto = ImageTk.PhotoImage(file=r"./icons/newdir2.png")
set_dirB = Button(GeneralF,height=25,width=180,text='Select Directory ',\
				font=("Helvetica",11),command=selectdirectory,\
				image=dirphoto,compound=RIGHT)
set_dirB.grid(row=0,column=0)


# display the name of an image of the selected sequence 
fl = Label(GeneralF,text="First Image :",anchor='e',font=("Helvetica", 11),\
           width=22)
fl.grid(row=1, column=0)


# button for loading videos
load_vidB = Button(GeneralF, height=1, width=22, text='Load Video',\
            font=("Helvetica",11),command=loadvideo) 
load_vidB.grid(row=2,column=0)




# Label and Entry Widget for setting recording speed [FPS]
fps_label=Label(GeneralF, text="Recording Speed [FPS] :",anchor='e',\
                font=("Helvetica",11),width=22)
fps_label.grid(row=0,column=2)

fps_list = [300,200,120,100,30]
fpscombo = tkinter.ttk.Combobox(GeneralF,values=fps_list,width=5)
#enter_fps.bind("<Return>", set_fps)
#enter_fps.insert(END, '300') # set default 
fpscombo.current(0) 
fpscombo.grid(row=0,column=3)

# Label and Entry Widget for setting the pixel size in [nm] 
pixsize_label=Label(GeneralF, text="Pixelsize [nm] :",width=22,anchor='e',\
                    font=("Helvetica",11))
pixsize_label.grid(row=1,column=2)


pixsize_list = [345, 173, 86] 
pixsizecombo = tkinter.ttk.Combobox(GeneralF,values=pixsize_list,width=5)
pixsizecombo.grid(row=1,column=3)
pixsizecombo.current(0)

GeneralF.grid_columnconfigure(0,minsize=200) 
GeneralF.grid_columnconfigure(2,minsize=200)
GeneralF.grid_columnconfigure(3,minsize=50)


# now we calculate the size for column=1 in GeneralF, in order that it matches 
# the width of the nbook 

ctrl_panel.update() 
# calc the width of column 1: 
dirnamew = nbookw - 200 - 200 - 50 - 50
GeneralF.grid_columnconfigure(1,minsize=dirnamew)

dirname=StringVar()
dirname.set("No Directory Selected") # initial value of dirname 
dirname_label = Label(GeneralF,textvariable=dirname,anchor='center',\
                      font=("Helvetica",11))
dirname_label.grid(row=0,column=1)

fname=StringVar()
fname.set("No Directory Selected")
fname_label = Label(GeneralF,textvariable=fname,font=("Helvetica",11))
fname_label.grid(row=1,column=1)

#******************************************************************************#



# *****************************************************************************#
# *************** Determine the height of the Notebook widget *****************#
 
# the 'current settings'-frame, the help button and the quit button have been 
# generated -> based on the size of these containers we can now determine the 
# 'optimal' size of the 'notebook'! 
GeneralF.update() 
ctrl_panel.update() # update to determine the button size in pixels 

emptyspace = 20

nbookh = ctrl_panel.winfo_screenheight() - GeneralF.winfo_height() -\
         emptyspace - 2*(offset + 5) 
#print('quitB width', quitB.winfo_width())
#******************************************************************************#





#******************************************************************************#








"""
###################################################################################################
# this was a straigth-forward attempt to remove vibrations 
# Wackel Dackel 
wackelB = Button(CapSeqF,text='  WackelDackel  ', command=lambda: PIL_ImgSeq.wackeldackel(),\
        height=bh,width=bw)   
wackelB.grid(row=4,column=0,columnspan=2)
####################################################################################################
"""




# ROI selection Button
#import RegionOfInterest
#roi = RegionOfInterest.ROI(ctrl_panel) # instantiate roi object 
#roiB = Button(ROIF,text='Select ROI', command=lambda: roi.get_roi(PIL_ImgSeq), height=bh, width=bw)
#roiB.grid(row=0,column=1,columnspan=10) 
# roi sequence (cropped PIL image sequence) available by attribute: "roi.roiseq"  


# Animate ROI Button
#animateROIB = Button(ROIF,text='Animate ROI', command=animate_roi,\
#        height=imgbh,width=imgbw,image=moviephoto,compound=RIGHT) 
#animateROIB.grid(row=1, column=1,columnspan=10,padx=px,pady=py)
#*************************************************************************************************#





#*****************************************************************************#
# the main window is organized in notebook-tabs
# available notebook tabs: animation, ROI selection, powerspec, activity map 

import tkinter.ttk
nbook = tkinter.ttk.Notebook(ctrl_panel,width=nbookw,height=nbookh)
nbook.grid(row=1,column=1,columnspan=1,rowspan=1,sticky='NESW',padx=10,pady=10)

# if the clicked tab is not the current tab -> stop dyn. display (avoids crash!) 
nbook.bind('<ButtonPress-1>',switchtab)

# animate the original sequence in 'animationtab' 
animationtab = Frame(nbook,width=int(round(0.9*nbookw)),height=int(round(0.95*nbookh)))
nbook.add(animationtab, text='Animate Sequence')




# remove sensor pattern (Puybareau 2016) 
#removepatternB = Button(animationtab,text='Pattern Removal',\
#                   command=lambda: PIL_ImgSeq.removepattern(), height=bh, width=16)
#removepatternB.place(in_=animationtab, anchor="c", relx=.07, rely=0.07)



# add an 'Image Registration'-button in the animation tab 
#imageregB = Button(animationtab,text='Image Registration',\
#                   command=lambda: PIL_ImgSeq.imagereg(), height=bh, width=16)
#imageregB.place(in_=animationtab, anchor="c", relx=.07, rely=.14)



# motion extraction (Puybareau 2016) 
motionextractB = Button(animationtab,text='Subtract Mean',\
                   command=lambda: PIL_ImgSeq.extractmotion(), height=bh, width=16)
motionextractB.place(in_=animationtab, anchor="c", relx=.07, rely=0.07)




# ROI selection tab 
roitab = Frame(nbook,width=int(round(0.9*nbookw)),height=int(round(0.95*nbookh)))
nbook.add(roitab, text='ROI Selection') 



# ROI selection Button
import RegionOfInterest
roi = RegionOfInterest.ROI(ctrl_panel) # instantiate roi object 
roiB = Button(roitab,text='Reset ROI', command=select_roi, height=bh, width=10)
roiB.place(in_=roitab, anchor="c", relx=.07, rely=.07)
# roi sequence (cropped PIL image sequence) available by attribute: "roi.roiseq"  


# *****************************************************************************#
cbftab = Frame(nbook,width=int(round(0.9*nbookw)),\
               height=int(round(0.95*nbookh)))
nbook.add(cbftab, text='Ciliary Beat Frequency') 

pwspec1frame = Frame(cbftab,width=int(round(0.65*nbookw)),\
                     height=int(round(0.65*nbookh)))
pwspec1frame.place(in_=cbftab, anchor='c', relx=0.5,rely=0.4)  


# Get Powerspec Button 
import Powerspec 
import Plots 

powerspectrum = Powerspec.powerspec(pwspec1frame,int(round(0.6*nbookw)),\
                int(round(0.6*nbookh)))

minfreq = IntVar()
maxfreq = IntVar()
minfreq.set(5)
maxfreq.set(15) 

minscale = Scale(cbftab, from_=1, to=50, orient=HORIZONTAL,length=400,\
                 resolution=0.2,variable=minfreq,command=peakselector)
minscale.place(in_=cbftab,anchor='c', relx=0.5,rely=0.8) 

maxscale = Scale(cbftab, from_=1, to=50, orient=HORIZONTAL,length=400,\
                 resolution=0.2,variable=maxfreq,command=peakselector)
maxscale.place(in_=cbftab,anchor='c', relx=0.5,rely=0.85) 

powerspecB=Button(cbftab,text='Powerspectrum', \
        command=lambda: powerspectrum.calc_powerspec(roiplayer.roiseq,fpscombo.get(),\
                        pwspec1frame),height=bh,width=bw)
powerspecB.place(in_=cbftab, anchor='c', relx=0.5, rely=0.05) 

# get_cbf is defined in 'TkPowerspecPlot.py' 

cbfB = Button(cbftab,text='Determine CBF',command=lambda: \
              powerspectrum.pwspecplot.get_cbf(float(minscale.get()),\
              float(maxscale.get()),fpscombo.get()), height=bh, width=bw) 
cbfB.place(in_=cbftab, anchor='c', relx=0.5, rely=0.92) 

# powerspectrum.spec : holds the spectrum 
# powerspectrum.freqs : holds the corresponding frequencies 


# ------------------------------------------------------------------------------
# add a combobox in which the user is supposed to specify the 
# number of harmonics, the default is 2 

# Label and Entry Widget for specifying the number of visible harmonics  
nrharms_label=Label(cbftab, text="Number of Harmonics :",width=22,anchor='e',\
                    font=("Helvetica",11))
nrharms_label.place(in_=cbftab, anchor='c', relx=0.75, rely=0.15) 

nrharms_list = [1,2,3] 
nrharmscombo = tkinter.ttk.Combobox(cbftab,values=nrharms_list,width=5)
nrharmscombo.place(in_=cbftab, anchor='c', relx=0.85, rely=0.15) 
nrharmscombo.current(0)
# ------------------------------------------------------------------------------












#*****************************************************************************#




#******************************************************************************#
#*************************** activity map tab *********************************#

activitytab = Frame(nbook,width=int(round(0.9*nbookw)),\
                    height=int(round(0.95*nbookh)))
nbook.add(activitytab, text='Activity Map') 

mapframe = Frame(activitytab,width=int(round(0.8*nbookh)),height=int(round(0.8*nbookh)))
mapframe.place(in_=activitytab, anchor='c', relx=0.5,rely=0.55)  

mapframe.update()

import activitymap
activity_map = activitymap.activitymap(mapframe,int(round(0.8*nbookh)),\
        int(round(0.8*nbookh))) # activity map object  

activityB = Button(activitytab,text='Activtiy Map',\
                   command=lambda: activity_map.calc_activitymap(mapframe,\
                   roiplayer.roiseq,float(fpscombo.get()),float(minscale.get()),\
                   float(maxscale.get()), powerspectrum), height=bh, width=bw) 
activityB.place(in_=activitytab, anchor='c', relx=0.5, rely=0.05) 

#*****************************************************************************#


#*****************************************************************************#
# *************************** Single Pixel Analysis **************************#
if (SinglePixelAnalysis):

	pixeltab = Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
	nbook.add(pixeltab, text='Single Pixel Analysis') 

	# ROI selection Button
	import PixelOfInterest

	pixelplotframe = Frame(pixeltab,width=int(round(0.45*screenw)),height=int(round(0.7*screenh)))
	pixelplotframe.place(in_=pixeltab, anchor='c', relx=0.8,rely=0.5)  

	pixoi = PixelOfInterest.PixOI(ctrl_panel,pixelplotframe,fpscombo.get()) # instantiate roi object 

	pixoiB = Button(pixeltab,text='Select Pixel', command=select_pixel, height=bh, width=bw)
	pixoiB.place(in_=pixeltab, anchor="c", relx=.25, rely=.05)

	pixelchoiceframe = Frame(pixeltab,width=int(round(0.5*screenw)),height=int(round(0.7*screenh)))
	pixelchoiceframe.place(in_=pixeltab, anchor='c', relx=0.25,rely=0.55)  
#**************************************************************************** #





# *************************************************************************** #
# ************************** Correlate frame ******************************** #

# purpose : find the power stroke duration / recovery stroke duration 
# we might use the ciliary trajectory to determine the ciliary amplitude 

#mtracktab = Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
#nbook.add(mtracktab, text='Motion Tracking') 

#mtrackB = Button(pixeltab,text='Track a ROI', command=motion_track, height=bh, width=bw)
#pixoiB.place(in_=pixeltab, anchor="c", relx=.25, rely=.05)











#**************************************************************************************************#
#pathtab = Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
#nbook.add(pathtab, text=' Path of Interest (POI) ') 


# Get the Path of Interest (POI)
#import PathOfInterest
#poi = PathOfInterest.POI() # poi.poi holds the path of interest  
#POIB = Button(POIF,text='Select a POI', command=lambda: poi.GetPOI(PIL_ImgSeq), height=bh,width=bw)
#POIB.grid(row=0, column=1, columnspan=2, padx=px, pady=py)
#



#**************************************************************************************************#






#******************************************************************************#
# ************************* Particle Tracking ******************************** #
if (ParticleTracking): 
	ptracktab = Frame(nbook,width=int(round(0.6*screenw)),height=int(round(0.6*screenh)))
	nbook.add(ptracktab, text='Particle Tracking') 

	# top left -> 'controls' 

	trackcframe = Frame(ptracktab,takefocus=0)
	trackcframe.place(in_=ptracktab, anchor="c", relx=.1, rely=.2)

	#trackclframe = LabelFrame(trackcframe,takefocus=1, text='Controls',
	#					labelanchor='n',borderwidth = 4,padx=3,pady=3,font=("Helvetica", 11, "bold"))
	#trackclframe.grid(row=0,column=0)
#******************************************************************************#
  










#****************************************************************************#


#**************************************************************************** #
# ************************** Dynamic Filtering ****************************** #
if (DynamicFiltering):
	dynseq = DynamicFilter.DynFilter() 

	dynfiltertab = Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
	nbook.add(dynfiltertab, text='Dynamic Filtering') 
#*****************************************************************************#



#******************************************************************************#
# ******************* Spatio-Temporal Correlation **************************** #
if (SpatioTemporalCorrelogram):
	#import SpatioTempCorr  

	correlationtab = Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
	nbook.add(correlationtab, text='Saptio-Temporal Correlation') 

	corrB = Button(correlationtab,text='Spatio-Temp. Correlogram',command=corrgram, height=bh, width=bw)
	corrB.place(in_=correlationtab, anchor="c", relx=.5, rely=.05)
#*****************************************************************************#



#******************************************************************************#
if (kSpectrum):
    kspectab = Frame(nbook,width=int(round(0.75*screenw)),\
            height=int(round(0.8*screenh)))
    nbook.add(kspectab, text='kSpec') 

    kplotframe = Frame(kspectab,width=int(round(0.6*screenw)),height=int(round(0.6*screenh)))
    kplotframe.place(in_=kspectab, anchor='c', relx=0.5,rely=0.5)  

    kspecB = Button(kspectab,text='k spectrum',command=kspec, height=bh, width=bw)
    kspecB.place(in_=kspectab, anchor="c", relx=.5, rely=.05)

    splitangle = IntVar()
    splitangle.set(0) 

    splitlinescale = Scale(kspectab, from_=0, to=180, orient=HORIZONTAL,length=400,\
            resolution=1.0,variable=splitangle,command=splitkspec)
    splitlinescale.place(in_=kspectab,anchor='c', relx=0.5,rely=0.9) 
#******************************************************************************#



# **************************************************************************** # 
# mean spatial autocorrelation tab 

mcorrtab = Frame(nbook, width=int(round(0.9*nbookw)),height=int(round(0.95*nbookh)))
nbook.add(mcorrtab, text='MeanCorr') 

mcorrB = Button(mcorrtab, text='Mean Spatial Autocorrelation', command=meanscorrgram, height=bh, width=bw) 
mcorrB.place(in_=mcorrtab, anchor="c", relx=.5, rely=.05) 

# here we plot the mean spatial autocorrelation ('mscorr' = mean spatial correlation)  
mscorrplotframe = Frame(mcorrtab,width=int(round(0.45*screenw)),height=int(round(0.6*screenh)))
mscorrplotframe.place(in_=mcorrtab, anchor='c', relx=0.25, rely=0.5) 


# plot a profile along a selected line going through the center of the mean spatial acorr
mscorrprofileframe = Frame(mcorrtab, width=int(round(0.45*screenw)),height=int(round(0.6*screenh)))
mscorrprofileframe.place(in_=mcorrtab, anchor='c', relx=0.75, rely=0.5) 












#placeholder_photo = ImageTk.PhotoImage(file=r"./icons/placeholder.png")
# Adds tab 2 of the notebook
#sacorr = Frame(nbook,width=int(round(0.7*screenw)),height=int(round(0.7*screenh)))
#nbook.add(sacorr, text=' Spatial Acorr ')#,image=placeholder_photo,compound=BOTTOM)
#if (spatialacorr_photo is None):
#    can2 = Canvas(sacorr, width = 500, height = 400) 
#    can2.pack()
#    sacorrcan = can2.create_image(10,10, anchor=NW, image=placeholder_photo)  
#**************************************************************************************************#









# --------------------------------------------------------------------------------------------------
ctrl_panel.mainloop() # loop and wait for events 
# --------------------------------------------------------------------------------------------------
sys.exit() 
