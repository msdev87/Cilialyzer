# ==============================================================================
#
# This is the main loop of the "Cilialyzer" application 
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

# ---------------------- import necessary modules ------------------------------

import FlipbookROI
import math
import getline
import io, os
from PIL import ImageTk
import PIL.Image
import webbrowser
import warnings
import tkinter as tk
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
import LoadSequence
import tkinter.ttk
import RegionOfInterest
import Powerspec
import Plots
import activitymap
import sys
import menubar

# ------------------------------------------------------------------------------


# ******************************************************************************
# ******************** Configuration of the main window ************************
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

ParticleTracking_flag = True

DynamicFiltering_flag = False

SpatioTemporalCorrelogram = 0

kSpectrum = 0

resize_flag = False # indicates whether the user resized the main window

# ******************************************************************************

player = None
ptrackplayer = None

# ******************************************************************************
"""
# -------------------------------- ROI animation -------------------------------
def animate_roi():

    win = roitab
    refresh = 0
    player = Flipbook.ImgSeqPlayer(win,PIL_ImgSeq.directory,refresh,
        roiplayer.roiseq,PIL_ImgSeq.seqlength)
    player.animate() # call method animate 

# ------------------------------------------------------------------------------
"""


#def helpbutton():
#    webbrowser.open_new(r'./Doc/help.pdf')


"""
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
"""


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



"""
def selectdirectory():

    global player,roiplayer, ptrackplayer

    print('********* test ************')


    #import avoid_troubles
    #avoid_troubles.stop_animation(player,roiplayer,ptrackplayer)

 
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

    try:
        ptrackplayer.stop = 2
    except NameError:
        pass


    # ask the user to set a new directory and load the images  
    PIL_ImgSeq.choose_directory(dirname,fname)
    PIL_ImgSeq.load_imgs() # loads image sequence 
    # PIL_ImgSeq.sequence[i] now holds the i-th frame (img format: 8 Bits, PIL) 


    avoid_troubles.clear_main(player,roiplayer,ptrackplayer)


    # if new directory is set -> destroy frames 
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

    # destroy particle tracking application
    try:
        ptrackplayer.frame.destroy()
        del ptrackplayer
    except NameError:
        pass

    # delete content of powerspec tab, before switching to animation
    powerspectrum.tkframe.destroy()



    # finally, switch to the roi selection tab to animate the selected images
    nbook.select(nbook.index(roitab))
    refresh = 0
    selectroi = 1
    roiplayer = FlipbookROI.ImgSeqPlayer(roitab,PIL_ImgSeq.directory,refresh,
        PIL_ImgSeq.sequence,PIL_ImgSeq.seqlength,roi,selectroi)
    roiplayer.animate()
"""



def corrgram():

    # calculate spatio-temporal autocorrelation 

    try:
        dynseq.spatiotempcorr(float(toolbar_object.fpscombo.get()),float(minscale.get()),
            float(maxscale.get()))
    except NameError:
        print("namerror")
        dynseq = DynamicFilter.DynFilter()
        dynseq.dyn_roiseq = roiplayer.roiseq
        dynseq.spatiotempcorr(float(toolbar_object.fpscombo.get()),float(minscale.get()),
            float(maxscale.get()))

    print("spatiotempcorr calculated")
    #print "spatiotempcorr calculated" 
    refresh = 0
    corrplayer = Flipbook.ImgSeqPlayer(correlationtab,PIL_ImgSeq.directory,
        refresh,dynseq.corr_roiseq,len(dynseq.corr_roiseq))
    corrplayer.animate()



def meanscorrgram():
    global dynseq

    # calculate the mean spatial autocorrelation 
    try:
        dynseq.mscorr(float(toolbar_object.fpscombo.get()),float(minscale.get()),
            float(maxscale.get()),mscorrplotframe,mscorrprofileframe,
            float(toolbar_object.pixsizecombo.get()))

    except NameError:
        print('except')
        dynseq = DynamicFilter.DynFilter()
        dynseq.dyn_roiseq = roiplayer.roiseq
        dynseq.mscorr(float(toolbar_object.fpscombo.get()),float(minscale.get()),
            float(maxscale.get()),mscorrplotframe,mscorrprofileframe,
            float(toolbar_object.pixsizecombo.get()))


def kspec():
    # calculate the spatial power spectral density
    global dynseq
    try:
        dynseq.kspec(float(toolbar_object.fpscombo.get()),float(minscale.get()),float(maxscale.get()),kplotframe)
    except NameError:
        print("namerror")
        dynseq = DynamicFilter.DynFilter()
        dynseq.dyn_roiseq = roiplayer.roiseq
        dynseq.kspec(float(toolbar_object.fpscombo.get()),float(minscale.get()),float(maxscale.get()),kplotframe)


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
    roiplayer = FlipbookROI.ImgSeqPlayer(roitab,PIL_ImgSeq.directory,refresh,
        PIL_ImgSeq.sequence,PIL_ImgSeq.seqlength,roi,selectroi) 
    roiplayer.animate()


def select_pixel():
    global roiplayer

    #print "this is a test" 

    try:
        # avoid crash 
        pixplayer.stop = 2
        # as roiplayer was not None -> destroy frame before it gets rebuilt:
        pixplayer.frame.destroy()
    except NameError:
        pass

    refresh = 0
    selectroi = 2 # selectroi = 2 -> pixel selection
    pixplayer = FlipbookROI.ImgSeqPlayer(pixelchoiceframe,PIL_ImgSeq.directory,
        refresh,roiplayer.roiseq,PIL_ImgSeq.seqlength,pixoi,selectroi) 
    pixplayer.animate()

def pcolor_func():
	pass

def switchtab(event):

    global player, roiplayer, ptrackplayer

    # if tab is pressed (and pressed tab != active tab) then take precautions...  

    clicked_tab = nbook.tk.call(nbook._w, "identify", "tab", event.x, event.y)
    active_tab = nbook.index(nbook.select())

    #print("clicked tab: ", clicked_tab) 

    #if ((active_tab == nbook.index(animationtab)) and (clicked_tab != active_tab)):
    #    try:
    #        # stop the player to prevent a crash 
    #        player.stop = 2
    #    except NameError:
    #        pass

    if ((active_tab == nbook.index(roitab)) and (clicked_tab != active_tab)):
        print('****************************')
        print('test')
        print('****************************')

        try:
            print('test2')
            # stop the player to prevent a crash 

            print('roiplayer id: ',id(roiplayer))
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
        # dynamically filtered sequence 
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
                roiplayer = FlipbookROI.ImgSeqPlayer(roitab,
                            PIL_ImgSeq.directory,refresh,PIL_ImgSeq.sequence,
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
        ptrackplayer = FlipbookPTrack.ImgSeqPlayer(ptracktab,
                                                PIL_ImgSeq.directory,\
                                                refresh,roiplayer.roiseq,\
                                                PIL_ImgSeq.seqlength,roi,\
                                                selectroi,\
                                                float(toolbar_object.fpscombo.get()),\
                                                float(toolbar_object.pixsizecombo.get()))
        ptrackplayer.animate()

    if (DynamicFiltering_flag):

        if (clicked_tab == nbook.index(dynfiltertab)):
            # dynamic filtering tab 
            nbook.select(nbook.index(dynfiltertab))
            # 1. apply band-pass filter 
            dynseq.bandpass(roiplayer.roiseq,float(toolbar_object.fpscombo.get()),float(minscale.get()),float(maxscale.get()),int(nrharmscombo.get()))

            refresh = 0
            dynplayer = Flipbook.ImgSeqPlayer(dynfiltertab, PIL_ImgSeq.directory,\
                                   refresh,dynseq.dyn_roiseq,\
                                   PIL_ImgSeq.seqlength) 
        dynplayer.animate() # call meth

#   def calcplot_powerspec(pwspec,roiseq,fps,specplot,frame):
#   pwspec.calc_powerspec(roiseq,fps,specplot,frame)

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


def resize(event):
    global winresize_init, winresize_cnt, ctrl_panel, mainframe

    #global exitphoto

    print('window is changing size')

    # as soon as the window size is getting changed, 
    # wait for some time before the mainframe gets destroyed and re-created

    winresize_delay = 0.5
    winresize_cnt += 1

    if ((winresize_init == True) and (winresize_cnt)):
        winresize_init = time.time()

    if ((time.time() - winresize_init) > winresize_delay):

        print('-----------------------')
        print('width: ',event.width)
        print('height: ',event.height)
        print('-----------------------')
        winresize_init = True

        # destroy mainframe 
        mainframe.destroy()

        # the following should be done in self.__init__
        ctrl_panel.update()

        mainframe = tk.Frame(ctrl_panel,takefocus=0)
        mainframe.grid(row=0,column=0,sticky='n,s,w,e')

        #helpB = Button(mainframe,height=15,width=30,text='   Help',command=helpbutton,
        #image=fakepixel,compound=tk.RIGHT)
        #helpB.grid(row=0,column=0,padx=2,pady=2,sticky='n')

        # Quit Button (placed in the bottom right edge of the root window)  
        #exitphoto = ImageTk.PhotoImage(file=r"./icons/exit/exit_small.png")
        #quitB=Button(mainframe,image=exitphoto,command=endprogram,height=32,width=64)
        #quitB.grid(row=1,column=1,columnspan=1,sticky='s',padx=2,pady=2)

        ctrl_panel.update()

    else:
        pass


    #ctrl_panel.update()
    #print(ctrl_panel.winfo_screenwidth())
    #print(ctrl_panel.winfo_screenheight())
    #print("---")



#def update_winsize():
#    print('update: ',ctrl_panel.winfo_width())
#    pass

# ==============================================================================
# ==============================================================================
# ------- Below the root window and its buttons get created & arranged ---------
# ==============================================================================
# ==============================================================================

myfont = ("Verdana", 10)

# First, we need a Tkinter root window (named as "ctrl_panel"):  
ctrl_panel = tk.Tk()

# set cilialyzer icon
ctrl_panel.iconphoto(False, tk.PhotoImage(file='./logo/logo.png'))

# Set the window title
ctrl_panel.title("Cilialyzer")
ctrl_panel.minsize(width=20,height=20)

# add the menubar (mbar) to the root window ('ctrl_panel'):
mbar = menubar.Menubar(ctrl_panel)
ctrl_panel.config(menu=mbar.menubar)
ctrl_panel.update()

# height of menubar (in pixels) 
mbar_height = mbar.menubar.winfo_reqheight()


#print('-----------------------------------------------------------------------')
#print('ctrl_panel dimensions')
#print(ctrl_panel.winfo_screenwidth(),ctrl_panel.winfo_screenheight())
#print('frame dimensions:')
#print(mainframe.winfo_screenwidth(),mainframe.winfo_screenheight())
#print('-----------------------------------------------------------------------')

# note that the upper left edge of the screen has the coordinates (0,0)

# the upper left edge of the main window gets created at the coordinates 
# (offset,offset) [in pixels], where the upper left edge of the screen = (0,0)
offset=10

# print("test")
# print(ctrl_panel.winfo_screenwidth())
# print(ctrl_panel.winfo_screenheight())
# print("---")

# winfo_screenheight and _screenwidth deliver the display's pixel-resolution 
ctrl_panel.geometry("%dx%d+%d+%d"%(
    ctrl_panel.winfo_screenwidth(),ctrl_panel.winfo_screenheight(),0,0))
ctrl_panel.update()

# since there is always a taskbar -> the ctrl_panel will be somewhat smaller 
# than [ screenwidth x screenheight ] 
# its actually generated dimensions (width x height) can be queried as:
# ctrl_panel.winfo_height() x ctrl_panel.winfo_width()

# create the main frame (container for all the widgets) in ctrl_panel:
mainframe = tk.Frame(ctrl_panel,takefocus=0)
mainframe.grid(row=0,column=0,sticky='n,s,w,e')

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

# In order to have more flexibility: add a "fakepixel" (transparent photo image) 
fakepixel= ImageTk.PhotoImage(file=r"./fakepixel.png")

# Help Button
#helpB = tk.Button(mainframe,height=15,width=30,text='   Help',command=helpbutton,
#    image=fakepixel,compound=tk.RIGHT)
#helpB.grid(row=0,column=0,padx=2,pady=2,sticky='n')

# Quit Button (placed in the bottom right edge of the root window)  
#exitphoto = ImageTk.PhotoImage(file=r"./icons/exit/exit_small.png")
#quitB=tk.Button(mainframe,image=exitphoto,command=endprogram,height=32,width=64)
#quitB.grid(row=1,column=2,columnspan=1,sticky='s',padx=2,pady=2)

# upadate button 
#updatephoto = ImageTk.PhotoImage(file=r"./icons/update_small.png")
#updateB=Button(ctrl_panel,image=updatephoto,command=update_winsize,height=50,width=50)
#updateB.grid(row=0,column=2,columnspan=1,padx=2,pady=2)


#******************** Determine the width of the Notebook *********************# 
ctrl_panel.update() # update to determine the notebook size in pixels 
emptyspace = 4

#nbookw = ctrl_panel.winfo_width() -\
#        emptyspace - 2*(offset + 5)
#******************************************************************************#

#******************************************************************************#
# ***************** GeneralF (Current Settings - Frame) ********************** #
# the frame at the top of the main window 
# In which we display the current settings (directory, filename, FPS, etc.)
#******************************************************************************#

# Feb 2021: we chage the GeneralF to a toolbar frame

# GeneralF = tk.LabelFrame(mainframe, text=' Current Settings ',labelanchor='n',
# borderwidth=2, padx=3,pady=3,font=("Helvetica",11,"bold"),relief=tk.GROOVE)
# GeneralF.grid(row=0,column=1,columnspan=1,rowspan=1)


PIL_ImgSeq = LoadSequence.ImageSequence()
# PIL_ImgSeq.directory -> contains path to choosen image sequence 
# PIL_ImgSeq.sequence  -> holds the PIL img sequence 



toolbar_height = 60
statusbar_height = 50



#******************************************************************************#
# the main features are provided by notebook-tabs
# available notebook tabs: animation, ROI selection, powerspec, activity map 

# TODO: determine nbookw,nbookh correctly
#nbook = tkinter.ttk.Notebook(mainframe,width=nbookw,height=nbookh)
nbookw = mainframe.winfo_screenwidth()-100
nbookh = mainframe.winfo_screenheight()-mbar_height-toolbar_height-statusbar_height
nbook = tkinter.ttk.Notebook(mainframe,width=nbookw,height=nbookh)
nbook.grid(row=1,column=1,columnspan=1,rowspan=1,sticky='NESW',padx=10,pady=10)

# if the clicked tab is not the current tab 
# we need to stop animations to avoid to cash the frontend!  
nbook.bind('<ButtonPress-1>',switchtab)



# ROI selection tab 
roitab = tk.Frame(nbook,width=int(round(0.9*nbookw)),height=int(round(0.95*nbookh)))
nbook.add(roitab, text='ROI Selection')

# ROI selection Button
roi = RegionOfInterest.ROI(mainframe) # instantiate roi object 
roiB = tk.Button(roitab,text='Reset ROI', command=select_roi, height=bh, width=16)
roiB.place(in_=roitab, anchor="c", relx=.07, rely=.12)
# roi sequence (cropped PIL image sequence) available by attribute: "roi.roiseq"  


# initialize the roiplayer
roiplayer = FlipbookROI.ImgSeqPlayer(roitab,PIL_ImgSeq.directory,0,
PIL_ImgSeq.sequence,PIL_ImgSeq.seqlength,roi,1)
#print('roiplayer id after init: ',id(roiplayer)) 



# ------------------------- create the toolbar --------------------------------#
import toolbar
toolbar_object = toolbar.Toolbar(mainframe,player,roiplayer,ptrackplayer,PIL_ImgSeq,nbook,roitab,roi)
toolbarF = toolbar_object.toolbarframe
toolbarF.grid(row=0,column=1,columnspan=1,rowspan=1)
# ---------------------------------------------------------------------------- #




"""
dirphoto = ImageTk.PhotoImage(file=r"./icons/directory/newdir_small.png")
set_dirB = tk.Button(toolbarF,height=16,width=160,text='Open Sequence ',\
    font=myfont,command=selectdirectory,image=dirphoto,compound=tk.RIGHT)
set_dirB.grid(row=0,column=0)
"""


# display the name of an image of the selected sequence 
#fl = tk.Label(GeneralF,text="First Image :",anchor='e',font=("Helvetica", 11),\
#           width=22)
#fl.grid(row=1, column=0)


# button for loading videos
#load_vidB = tk.Button(GeneralF, height=16, width=160, text='  Open Video',
#            font=("Helvetica",11),command=loadvideo,image=fakepixel,
#            compound=tk.RIGHT)
#load_vidB.grid(row=2,column=0)


"""
# Label and Entry Widget for setting recording speed [FPS]
fps_label=tk.Label(toolbarF, text="Recording Speed [FPS] :",anchor='e',\
                font=("Verdana",10),width=22)
fps_label.grid(row=0,column=3)

fps_list = [300,200,120,100,30]
fpscombo = tkinter.ttk.Combobox(toolbarF,values=fps_list,width=5)
#enter_fps.bind("<Return>", set_fps)
#enter_fps.insert(END, '300') # set default
fpscombo.current(0)
fpscombo.grid(row=0,column=4)
"""


"""
# Label and Entry Widget for setting the pixel size in [nm] 
pixsize_label=tk.Label(toolbarF, text="Pixelsize [nm] :",width=22,anchor='e',\
	font=("Helvetica",11))
pixsize_label.grid(row=0,column=5)

pixsize_list = [345, 173, 86, 4500,1]
pixsizecombo = tkinter.ttk.Combobox(toolbarF,values=pixsize_list,width=5)
pixsizecombo.grid(row=0,column=6)
pixsizecombo.current(0)
"""



# add a 'Next Sequence' button 
# TODO 

#toolbarF.grid_columnconfigure(0,minsize=200)
#toolboxF.grid_columnconfigure(2,minsize=200)
#toolboxF.grid_columnconfigure(3,minsize=50)

# now we calculate the size for column=1 in GeneralF, in order that it matches 
# the width of the nbook 

ctrl_panel.update()
# calc the width of column 1: 
# dirnamew = nbookw - 200 - 200 - 50 - 50
# toolboxF.grid_columnconfigure(1,minsize=dirnamew)

#dirname=tk.StringVar()
#dirname.set("No Directory Selected") # initial value of dirname 
#dirname_label = tk.Label(GeneralF,textvariable=dirname,anchor='center',\
#                      font=("Helvetica",11))
#dirname_label.grid(row=0,column=1)

#fname=tk.StringVar()
#fname.set("No Directory Selected")
#fname_label = tk.Label(GeneralF,textvariable=fname,font=("Helvetica",11))
#fname_label.grid(row=1,column=1)

#******************************************************************************#

# *****************************************************************************#
# *************** Determine the height of the Notebook widget *****************#

# the 'current settings'-frame, the help button and the quit button have been 
# generated -> based on the size of these containers we can now determine the 
# 'optimal' size of the 'notebook'! 
toolbarF.update()
ctrl_panel.update() # update to determine the button size in pixels 

emptyspace = 20

#nbookh = ctrl_panel.winfo_height() - toolbarF.winfo_height() -\
#         emptyspace - 2*(offset + 5)

#******************************************************************************#


"""
################################################################################
# this was a straigth-forward attempt to remove vibrations
# Wackel Dackel
wackelB = Button(CapSeqF,text='  WackelDackel  ', command=lambda: PIL_ImgSeq.wackeldackel(),\
        height=bh,width=bw)
wackelB.grid(row=4,column=0,columnspan=2)
################################################################################
"""





# remove sensor pattern (Puybareau 2016) 
# removepatternB = Button(animationtab,text='Pattern Removal',\
#                   command=lambda: PIL_ImgSeq.removepattern(), height=bh, width=16)
# removepatternB.place(in_=animationtab, anchor="c", relx=.07, rely=0.07)


# add an 'Image Registration'-button in the animation tab 
#imageregB = Button(animationtab,text='Image Registration',\
#                   command=lambda: PIL_ImgSeq.imagereg(), height=bh, width=16)
#imageregB.place(in_=animationtab, anchor="c", relx=.07, rely=.14)




# motion extraction (see Puybareau et al. 2016) i.e. subtract the mean image  
motionextractB = tk.Button(roitab,text='Subtract Mean',\
    command=lambda: PIL_ImgSeq.extractmotion(),height=bh,width=16)
motionextractB.place(in_=roitab, anchor="c", relx=.07, rely=0.07)


# *****************************************************************************#
cbftab = tk.Frame(nbook,width=int(round(0.9*nbookw)),\
            height=int(round(0.95*nbookh)))
nbook.add(cbftab, text='Ciliary Beat Frequency')

pwspec1frame = tk.Frame(cbftab,width=int(round(0.65*nbookw)),\
                height=int(round(0.65*nbookh)))
pwspec1frame.place(in_=cbftab, anchor='c', relx=0.5,rely=0.4)


# Get Powerspec Button 
powerspectrum = Powerspec.powerspec(pwspec1frame,int(round(0.6*nbookw)),\
                int(round(0.6*nbookh)))

minfreq = tk.IntVar()
maxfreq = tk.IntVar()
minfreq.set(5)
maxfreq.set(15)

minscale = tk.Scale(cbftab, from_=1, to=50, orient=tk.HORIZONTAL,length=400,\
                 resolution=0.2,variable=minfreq,command=peakselector)
minscale.place(in_=cbftab,anchor='c', relx=0.5,rely=0.8)

maxscale = tk.Scale(cbftab, from_=1, to=50, orient=tk.HORIZONTAL,length=400,\
                 resolution=0.2,variable=maxfreq,command=peakselector)
maxscale.place(in_=cbftab,anchor='c', relx=0.5,rely=0.85)

powerspecB=tk.Button(cbftab,text='Powerspectrum',\
    command=lambda: powerspectrum.calc_powerspec(roiplayer.roiseq,\
    toolbar_object.fpscombo.get(),pwspec1frame),height=bh,width=bw)
powerspecB.place(in_=cbftab, anchor='c', relx=0.5, rely=0.05)

# get_cbf is defined in 'TkPowerspecPlot.py' 

cbfB = tk.Button(cbftab,text='Determine CBF',command=lambda: \
              powerspectrum.pwspecplot.get_cbf(float(minscale.get()),\
              float(maxscale.get()),toolbar_object.fpscombo.get()), height=bh, width=bw) 
cbfB.place(in_=cbftab, anchor='c', relx=0.5, rely=0.92) 

# powerspectrum.spec : holds the spectrum 
# powerspectrum.freqs : holds the corresponding frequencies 


# ------------------------------------------------------------------------------
# add a combobox in which the user is supposed to specify the 
# number of harmonics, the default is 2 

# Label and Entry Widget for specifying the number of visible harmonics  
nrharms_label=tk.Label(cbftab, text="Number of Harmonics :",width=22,anchor='e',\
                    font=("Helvetica",11))
nrharms_label.place(in_=cbftab, anchor='c', relx=0.75, rely=0.15) 

nrharms_list = [1,2,3] 
nrharmscombo = tkinter.ttk.Combobox(cbftab,values=nrharms_list,width=5)
nrharmscombo.place(in_=cbftab, anchor='c', relx=0.85, rely=0.15) 
nrharmscombo.current(0)
# ------------------------------------------------------------------------------


#******************************************************************************#
#*************************** activity map tab *********************************#

activitytab = tk.Frame(nbook,width=int(round(0.9*nbookw)),\
                    height=int(round(0.95*nbookh)))
nbook.add(activitytab, text='Activity Map') 

mapframe = tk.Frame(activitytab,width=int(round(0.8*nbookh)),height=int(round(0.8*nbookh)))
mapframe.place(in_=activitytab, anchor='c', relx=0.5,rely=0.55)  

mapframe.update()

activity_map = activitymap.activitymap(mapframe,int(round(0.8*nbookh)),\
        int(round(0.8*nbookh))) # activity map object  

activityB = tk.Button(activitytab,text='Activtiy Map',\
                   command=lambda: activity_map.calc_activitymap(mapframe,\
                   roiplayer.roiseq,float(toolbar_object.fpscombo.get()),float(minscale.get()),\
                   float(maxscale.get()), powerspectrum), height=bh, width=bw) 
activityB.place(in_=activitytab, anchor='c', relx=0.5, rely=0.05) 

#*****************************************************************************#


#*****************************************************************************#
# *************************** Single Pixel Analysis **************************#
if (SinglePixelAnalysis):

	pixeltab = tk.Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
	nbook.add(pixeltab, text='Single Pixel Analysis') 

	# ROI selection Button
	import PixelOfInterest

	pixelplotframe = tk.Frame(pixeltab,width=int(round(0.45*screenw)),height=int(round(0.7*screenh)))
	pixelplotframe.place(in_=pixeltab, anchor='c', relx=0.8,rely=0.5)  

	pixoi = PixelOfInterest.PixOI(ctrl_panel,pixelplotframe,toolbar_object.fpscombo.get()) # instantiate roi object 

	pixoiB = tk.Button(pixeltab,text='Select Pixel', command=select_pixel, height=bh, width=bw)
	pixoiB.place(in_=pixeltab, anchor="c", relx=.25, rely=.05)

	pixelchoiceframe = tk.Frame(pixeltab,width=int(round(0.5*screenw)),height=int(round(0.7*screenh)))
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


#******************************************************************************#
# ************************* Particle Tracking ******************************** #
if (ParticleTracking_flag):
    ptracktab = tk.Frame(nbook,width=int(round(0.6*screenw)),height=int(round(0.6*screenh)))
    nbook.add(ptracktab, text='Particle Tracking')

    #print('ptracktab ',nbook.index(ptracktab))

    # top left -> 'controls' 

    trackcframe = tk.Frame(ptracktab,takefocus=0)
    trackcframe.place(in_=ptracktab, anchor="c")#relx=.1, rely=.2)

    #trackclframe = LabelFrame(trackcframe,takefocus=1, text='Controls',
    #					labelanchor='n',borderwidth = 4,padx=3,pady=3,font=("Helvetica", 11, "bold"))
    #trackclframe.grid(row=0,column=0)
#******************************************************************************#


#**************************************************************************** #
# ************************** Dynamic Filtering ****************************** #
if (DynamicFiltering_flag):
	dynseq = DynamicFilter.DynFilter()

	dynfiltertab = tk.Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
	nbook.add(dynfiltertab, text='Dynamic Filtering') 
#*****************************************************************************#


#******************************************************************************#
# ******************* Spatio-Temporal Correlation **************************** #
if (SpatioTemporalCorrelogram):
	#import SpatioTempCorr  

	correlationtab = tk.Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
	nbook.add(correlationtab, text='Saptio-Temporal Correlation') 

	corrB = tk.Button(correlationtab,text='Spatio-Temp. Correlogram',command=corrgram, height=bh, width=bw)
	corrB.place(in_=correlationtab, anchor="c", relx=.5, rely=.05)
#*****************************************************************************#


#******************************************************************************#
if (kSpectrum):
    kspectab = tk.Frame(nbook,width=int(round(0.75*screenw)),\
            height=int(round(0.8*screenh)))
    nbook.add(kspectab, text='kSpec') 

    kplotframe = tk.Frame(kspectab,width=int(round(0.6*screenw)),height=int(round(0.6*screenh)))
    kplotframe.place(in_=kspectab, anchor='c', relx=0.5,rely=0.5)  

    kspecB = tk.Button(kspectab,text='k spectrum',command=kspec, height=bh, width=bw)
    kspecB.place(in_=kspectab, anchor="c", relx=.5, rely=.05)

    splitangle = tk.IntVar()
    splitangle.set(0)

    splitlinescale = tk.Scale(kspectab, from_=0, to=180, orient=tk.HORIZONTAL,length=400,\
            resolution=1.0,variable=splitangle,command=splitkspec)
    splitlinescale.place(in_=kspectab,anchor='c', relx=0.5,rely=0.9)
#******************************************************************************#

# **************************************************************************** # 
# mean spatial autocorrelation tab 

mcorrtab = tk.Frame(nbook, width=int(round(0.9*nbookw)),height=int(round(0.95*nbookh)))
nbook.add(mcorrtab, text='MeanCorr')

mcorrB = tk.Button(mcorrtab, text='Mean Spatial Autocorrelation', command=meanscorrgram, height=bh, width=bw) 
mcorrB.place(in_=mcorrtab, anchor="c", relx=.5, rely=.05)

# here we plot the mean spatial autocorrelation ('mscorr' = mean spatial correlation)  
mscorrplotframe = tk.Frame(mcorrtab,width=int(round(0.45*screenw)),height=int(round(0.6*screenh)))
mscorrplotframe.place(in_=mcorrtab, anchor='c', relx=0.25, rely=0.5)


# plot a profile along a selected line going through the center of the mean spatial acorr
mscorrprofileframe = tk.Frame(mcorrtab, width=int(round(0.45*screenw)),height=int(round(0.6*screenh)))
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

#ctrl_panel.resizable(True, True)




# we want the ctrl_panel to be resizable!
#ctrl_panel.bind( "<Configure>", resize)

winresize_init = True
winresize_cnt = 0 # window-resize-counter; to ignore the change in window size 
# at startup 

# --------------------------------------------------------------------------------------------------
ctrl_panel.mainloop() # loop and wait for events 
# --------------------------------------------------------------------------------------------------
sys.exit()
