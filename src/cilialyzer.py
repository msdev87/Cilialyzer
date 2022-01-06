import tkinter as tk
import menubar
from PIL import ImageTk,Image
import LoadSequence
import os
import tkinter.ttk
import RegionOfInterest
import FlipbookROI
import statusbar
import toolbar
import numpy
import Powerspec
import activitymap
import DynamicFilter
import Flipbook
import FlipbookPTrack
import multiprocessing


class Cilialyzer():

    """
    This class establishes the tkinter root window with all its content
    """

    """
    def resize(self, event):

        print('window changed its size')

        # as soon as the window size is getting changed,
        # wait for some time before the mainframe gets destroyed and re-created

        self.main_window.update()
        self.mainframe.update()

        winresize_delay = 1.0
        self.winresize_cnt += 1

        if ((self.winresize_init == True) and (self.winresize_cnt)):
            self.winresize_init = time.time()

        if ((time.time() - self.winresize_init) > winresize_delay):

            print('-----------------------')
            print('event.width: ', event.width)
            print('event.height: ', event.height)
            print('-----------------------')

            print('-----------------------')
            print('main_window width: ', self.main_window.winfo_width())
            print('main_window height: ',self.main_window.winfo_height())
            print('-----------------------')

            self.winresize_init = True

            # destroy mainframe
            try:
                self.mainframe.destroy()
            except:
                pass
            
            self.__init__(True)

        else:
            pass
        """

    def switchtab(self, event):
        # if tab is pressed (and pressed tab != active tab) then take precautions...

        clicked_tab = self.nbook.tk.call(self.nbook._w, "identify", "tab", event.x, event.y)
        active_tab = self.nbook.index(self.nbook.select())

        if ((active_tab == self.nbook.index(self.roitab)) and (clicked_tab != active_tab)):
            try:
                self.roiplayer.stop = 2
            except NameError:
                pass

        if ((active_tab == self.nbook.index(self.ptracktab)) and (clicked_tab != active_tab)):
            # stop the player to prevent a crash
            try:
                self.ptrackplayer.stop = 2
            except NameError:
                pass

        if (clicked_tab == self.nbook.index(self.roitab)):

            # ROI Selection tab got activated

            # if dynamically filtered sequence available -> substitue roiseq with
            # dynamically filtered sequence
            try:
                if (len(self.dynseq.dyn_roiseq) > 0):
                    self.PIL_ImgSeq.sequence = self.dynseq.dyn_roiseq
            except:
                pass

            try:
                self.roiplayer.stop = 0
            except:
                try:
                    self.nbook.select(self.nbook.index(self.roitab))
                    refresh = 0
                    selectroi = 1
                    self.roiplayer = FlipbookROI.ImgSeqPlayer(self.roitab,
                        self.PIL_ImgSeq.directory, refresh, self.PIL_ImgSeq.sequence,
                        self.PIL_ImgSeq.seqlength, self.roi, selectroi)
                    self.roiplayer.animate()
                except:
                    pass

        if (clicked_tab == self.nbook.index(self.ptracktab)):
            # particle tracking tab got selected
            self.nbook.select(self.nbook.index(self.ptracktab))
            # create player object
            refresh = 0
            selectroi = 1
            self.ptrackplayer = FlipbookPTrack.ImgSeqPlayer(self.ptracktab,
                self.PIL_ImgSeq.directory, refresh, self.roiplayer.roiseq,
                self.PIL_ImgSeq.seqlength, self.roi, selectroi,
                float(self.toolbar.fpscombo.get()), float(self.toolbar.pixsizecombo.get()))
            self.ptrackplayer.animate()

        if (self.DynamicFiltering_flag):
            if (clicked_tab == self.nbook.index(self.dynfiltertab)):
                # dynamic filtering tab got selected
                self.nbook.select(self.nbook.index(self.dynfiltertab))
                # 1. apply band-pass filter
                self.dynseq.bandpass(self.roiplayer.roiseq,
                    float(self.toolbar.fpscombo.get()), float(self.minscale.get()),
                    float(self.maxscale.get()), int(self.nrharmscombo.get()))
                refresh = 0
                self.dynplayer = Flipbook.ImgSeqPlayer(self.dynfiltertab,
                    self.PIL_ImgSeq.directory, refresh, self.dynseq.dyn_roiseq,
                    self.PIL_ImgSeq.seqlength)
                self.dynplayer.animate() # call meth

    def select_roi(self):

        try:
            # avoid crash
            self.roiplayer.stop = 2
            # as roiplayer was not None -> destroy frame before it gets rebuilt:
            self.roiplayer.frame.destroy()
        except NameError:
            pass

        refresh = 0
        selectroi = 1
        self.roiplayer = FlipbookROI.ImgSeqPlayer(self.roitab,
            self.PIL_ImgSeq.directory, refresh, self.PIL_ImgSeq.sequence,
            self.PIL_ImgSeq.seqlength, self.roi, selectroi)
        self.roiplayer.animate()

    # ------------------------- peakselector -----------------------------------
    def peakselector(self, event):
        """"
        this command gets executed if the user shifts the scrollbars,
        which define the min and max freq of the considered freq band,
        which is necessary for the determination of the CBF and the activity map
        """

        minf = float(self.minscale.get())
        maxf = float(self.maxscale.get())

        # fill whole area white (to delete prior selections!)
        self.powerspectrum.pwspecplot.axes.fill_between(self.powerspectrum.freqs,
            self.powerspectrum.spec, facecolor='white', alpha=1.0)

        # shade first harmonic (selection)
        maxind = numpy.sum((numpy.array(self.powerspectrum.freqs) <= maxf).astype(int))
        minind = numpy.sum((numpy.array(self.powerspectrum.freqs) <= minf).astype(int))
        self.powerspectrum.pwspecplot.axes.fill_between(
            self.powerspectrum.freqs[minind:maxind + 1],
            self.powerspectrum.spec[minind:maxind + 1], facecolor='gray', alpha=0.8)

        self.powerspectrum.pwspecplot.canvas.draw()

        # --------- shade the second and third harmonic (if selected) ----------
        if (int(self.nrharmscombo.get()) > 1):
            fpeakw = maxf - minf
            fpeak = minf + 0.5 * fpeakw
            secondpeakf = 2.0 * fpeak
            secondminf = secondpeakf - 0.5 * fpeakw
            secondmaxf = secondpeakf + 0.5 * fpeakw

            maxind = numpy.sum(
                (numpy.array(self.powerspectrum.freqs) <= secondmaxf).astype(int))
            minind = numpy.sum(
                (numpy.array(self.powerspectrum.freqs) <= secondminf).astype(int))
            self.powerspectrum.pwspecplot.axes.fill_between(
                self.powerspectrum.freqs[minind:maxind + 1],
                self.powerspectrum.spec[minind:maxind + 1], facecolor='gray', alpha=0.4)

            self.powerspectrum.pwspecplot.canvas.draw()

        if (int(self.nrharmscombo.get()) > 2):
            thrdpeakf = 3.0 * fpeak
            thrdminf = thrdpeakf - 0.5 * fpeakw
            thrdmaxf = thrdpeakf + 0.5 * fpeakw

            maxind = numpy.sum(
                (numpy.array(self.powerspectrum.freqs) <= thrdmaxf).astype(int))
            minind = numpy.sum(
                (numpy.array(self.powerspectrum.freqs) <= thrdminf).astype(int))
            self.powerspectrum.pwspecplot.axes.fill_between(
                self.powerspectrum.freqs[minind:maxind + 1],
                self.powerspectrum.spec[minind:maxind + 1], facecolor='gray',
                alpha=0.4)

            self.powerspectrum.pwspecplot.canvas.draw()
    # ----------------------- end of peakselector ------------------------------


    def image_stabilization(self):

        import stabilize_proc
        from pystackreg import StackReg
        import multiprocessing

        ################### new #############################################
        sr = StackReg(StackReg.RIGID_BODY)

        firstimg = self.roiplayer.roiseq[0]  # first image of roi sequence
        width, height = firstimg.size  # dimension of images
        nimgs = len(self.roiplayer.roiseq)  # number of images

        # initialize numpy float array, which will hold the image sequence
        array = numpy.zeros((int(nimgs), int(height), int(width)))
        array_stabilized = numpy.copy(array)

        # PIL images -> numpy array
        for i in range(nimgs):
            array[i, :, :] = numpy.array(self.roiplayer.roiseq[i])

        # compute mean image:
        meanimg = numpy.mean(array[0:int(nimgs / 10), :, :], axis=0)

        """
        # loop over all images
        for i in range(nimgs):
            #note that only every second image is registered (perf
            if ((i % 2) == 0):
                sr.register(meanimg,array[i,:,:])
                # therefore, every second image is transformed as its 
            array_stabilized[i,:,:] = sr.transform(array[i,:,:])

            roiplayer.roiseq[i] = Image.fromarray(numpy.uint8(array_stabilized[i,:,:]))
        """

        num_procs = multiprocessing.cpu_count()
        subarrays = []
        arrayslice = round(nimgs / num_procs)

        # careful: remember python's array slicing:
        # array[start:stop] delivers all elements from start to stop-1!
        for i in range(num_procs):
            if (i < num_procs - 1):
                subarrays.append(
                    (meanimg, array[i * arrayslice:(i + 1) * arrayslice, :, :]))
        else:
            subarrays.append((meanimg, array[i * arrayslice:nimgs, :, :]))

        result = self.pool.map(stabilize_proc.subproc,
                          [subarrays[i] for i in range(num_procs)])

        #self.pool.close()

        # print(type(result))
        # print('length of list',len(result))
        # print('type of first element: ',type(result[0]))
        # print(result)

        # join the array slices together again
        # there are now 'num_procs' array slices, which have to be put together
        # -> fill 'array_stabilized'

        for i in range(num_procs):
            if (i < num_procs - 1):
                array_stabilized[i * arrayslice:(i + 1) * arrayslice, :, :] = \
                result[i]
            else:
                array_stabilized[i * arrayslice:nimgs, :, :] = result[
                    num_procs - 1]

        for i in range(nimgs):
            self.roiplayer.roiseq[i] = Image.fromarray(
                numpy.uint8(array_stabilized[i,:,:]))


    """
    def loadvideo():
        # TODO : videos should be loadable as well (not only image sequences) 
        global player, roiplayer

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

        PIL_ImgSeq.load_video(dirname, fpscombo.get())
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
        player = Flipbook.ImgSeqPlayer(animationtab, PIL_ImgSeq.directory, \
                                       refresh, PIL_ImgSeq.sequence, \
                                       PIL_ImgSeq.seqlength)
        player.animate()  # call method animate 
    """

    # --------------------------------------------------------------------------
    def meanscorrgram(self):
        """
        Computes the mean spatial autocorrelation
        """

        if (len(self.dynseq.dyn_roiseq) > 1):
            self.dynseq.mscorr(float(self.toolbar.fpscombo.get()), float(self.minscale.get()),
                float(self.maxscale.get()), self.mscorrplotframe, self.mscorrprofileframe,
                float(self.toolbar.pixsizecombo.get()))
        else:
            self.dynseq.dyn_roiseq = self.PIL_ImgSeq.sequence
            self.dynseq.mscorr(float(self.toolbar.fpscombo.get()), float(self.minscale.get()),
                float(self.maxscale.get()), self.mscorrplotframe, self.mscorrprofileframe,
                float(self.toolbar.pixsizecombo.get()))
    # --------------------------------------------------------------------------

    def corrgram():

        # calculate spatio-temporal autocorrelation

        try:
            dynseq.spatiotempcorr(float(toolbar_object.fpscombo.get()), float(minscale.get()),
                                  float(maxscale.get()))
        except NameError:
            print("namerror")
            dynseq = DynamicFilter.DynFilter()
            dynseq.dyn_roiseq = roiplayer.roiseq
            dynseq.spatiotempcorr(float(toolbar_object.fpscombo.get()), float(minscale.get()),
                                  float(maxscale.get()))

        print("spatiotempcorr calculated")
        # print "spatiotempcorr calculated"
        refresh = 0
        corrplayer = Flipbook.ImgSeqPlayer(correlationtab, PIL_ImgSeq.directory,
                                           refresh, dynseq.corr_roiseq, len(dynseq.corr_roiseq))
        corrplayer.animate()

    def kspec():
        # calculate the spatial power spectral density
        global dynseq
        try:
            dynseq.kspec(float(toolbar_object.fpscombo.get()), float(minscale.get()), float(maxscale.get()), kplotframe)
        except NameError:
            print("namerror")
            dynseq = DynamicFilter.DynFilter()
            dynseq.dyn_roiseq = roiplayer.roiseq
            dynseq.kspec(float(toolbar_object.fpscombo.get()), float(minscale.get()), float(maxscale.get()), kplotframe)



    def select_pixel():
        global roiplayer

        # print "this is a test"

        try:
            # avoid crash
            pixplayer.stop = 2
            # as roiplayer was not None -> destroy frame before it gets rebuilt:
            pixplayer.frame.destroy()
        except NameError:
            pass

        refresh = 0
        selectroi = 2  # selectroi = 2 -> pixel selection
        pixplayer = FlipbookROI.ImgSeqPlayer(pixelchoiceframe, PIL_ImgSeq.directory,
                                             refresh, roiplayer.roiseq, PIL_ImgSeq.seqlength, pixoi, selectroi)
        pixplayer.animate()

    # button for loading videos
    # load_vidB = tk.Button(GeneralF, height=16, width=160, text='  Open Video',
    #            font=("Helvetica",11),command=loadvideo,image=fakepixel,
    #            compound=tk.RIGHT)
    # load_vidB.grid(row=2,column=0)

    def frequency_correlation(self):
        pass

    def tacorr(self):
        # calls temporal_autocorrelation
        self.dynseq.temporal_autocorrelation(self.tacorr_plotframe,
            self.activity_map.freqmap)

    def __init__(self):

        """
        constructor for the tkinter root window (main_window) with all its content
        """

        """
         ______________________________________________________________________
        ¦                                                                      ¦
        ¦                              menubar                                 ¦
        ¦______________________________________________________________________¦
        ¦                                                                      ¦
        ¦                      toolbar in toolbarframe                         ¦
        ¦______________________________________________________________________¦
        ¦                                                                      ¦
        ¦                                                                      ¦
        ¦                             mainframe                                ¦ 
        ¦                                                                      ¦ 
        ¦______________________________________________________________________¦
        ¦                                                                      ¦
        ¦                       statusbar in statusframe                       ¦
        ¦______________________________________________________________________¦
        """

        # ******************************************************************************
        # ******************** Configuration of the main window ************************
        # ******************************************************************************

        # Configure which tabs should be made available when launching the application

        # Tab to view the sequence
        # AnimateSequence = True

        # Tab to select a ROI
        self.ROISelection_flag = True

        # Tab to generate the (ROI-based) power spectral density [PSD]
        self.CBF_flag = True

        # Tab to generate the activity map (ROI-based, PSD-based)
        self.ActivityMap_flag = True

        # Tab to analyze single pixels
        self.SinglePixelAnalysis_flag = False

        self.MotionTracking_flag = False

        self.ParticleTracking_flag = True

        self.DynamicFiltering_flag = True

        self.SpatioTemporalCorrelogram_flag = False

        self.kSpectrum_flag = False

        self.SpatialAcorr_flag = True

        resize_flag = False  # indicates whether the user resized the main window

        # ******************************************************************************

        multiprocessing.freeze_support()
        ncpus = multiprocessing.cpu_count()
        if (ncpus > 1):
            self.pool = multiprocessing.Pool(ncpus-1)
        else:
            self.pool = multiprocessing.Pool(ncpus)

        self.player = None
        self.ptrackplayer = None

        # We need a Tkinter root window (named as "main_window"):
        self.main_window = tk.Tk()

        # set the cilialyzer icon
        self.main_window.iconphoto(False, tk.PhotoImage(file='../images/logo/logo.png'))

        # Set the window title
        self.main_window.title("Cilialyzer")
        self.main_window.minsize(width=200, height=200)

        # set the font
        self.font = ("TkDefaultFont", 10)

        # winfo_screenheight and _screenwidth deliver the display's pixel-resolution
        self.main_window.geometry("%dx%d+%d+%d"%(
            self.main_window.winfo_screenwidth(),
            self.main_window.winfo_screenheight(), 0, 0))
        self.main_window.update()

        self.main_window_h1 = self.main_window.winfo_height()

        # add the menubar (mbar) to the root window ('main_window'):
        mbar = menubar.Menubar(self.main_window)
        self.main_window.config(menu=mbar.menubar)

        # make sure that the main window is resizable
        self.main_window.resizable(True, True)
        self.main_window.update()

        self.main_window_h2 = self.main_window.winfo_height()
        self.mbar_height = self.main_window_h1 - self.main_window_h2

        # note that the upper left edge of the screen has the coordinates (0,0)
        # the upper left edge of the main window gets created at the coordinates
        # (offset,offset) [in pixels], where the upper left edge of the screen = (0,0)
        offset = 0

        # since there is usually a taskbar -> the main_window will be somewhat smaller
        # than [ screenwidth x screenheight ]
        # its actually generated dimensions (width x height) can be queried as:
        # main_window.winfo_height() and main_window.winfo_width()

        # create the main frame (container for all the widgets) in main_window:
        self.mainframe = tk.Frame(self.main_window, takefocus=0)
        self.mainframe.grid(row=0, column=0, padx=0, pady=0, sticky='nswe')
        #self.mainframe.place(in_=self.main_window, anchor="c", relx=0.5, rely=0.5)

        self.main_window.update()

        # set button size and alignment
        bh = 1  # button height
        bw = 23 # button width
        px = 4  # pad x
        py = 4  # pad y

        imgbh = 28   # button height for buttons containing images
        imgbw = 182  # button width for buttons containing images

        # In order to have more flexibility: add a "fakepixel" (transparent photo image)
        self.fakepixel = ImageTk.PhotoImage(file=r"../images/icons/fakepixel.png")

        self.PIL_ImgSeq = LoadSequence.ImageSequence()
        # PIL_ImgSeq.directory -> contains path to selected image sequence
        # PIL_ImgSeq.sequence  -> holds the PIL img sequence

        self.toolbar_height = 35
        self.statusbar_height = 55

        #**********************************************************************#
        # the main features are provided by notebook-tabs
        # available notebook tabs: animation, ROI selection, powerspec, ...

        # set zoomed state
        if (os.name == 'nt'):
            self.main_window.state('zoomed')
        else:
            self.main_window.attributes('-zoomed', True)

        self.main_window.update()

        # get taskbar height in windows
        if (os.name == 'nt'):
            from win32api import GetMonitorInfo, MonitorFromPoint
            monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
            monitor_area = monitor_info.get("Monitor")
            work_area = monitor_info.get("Work")
            self.windows_taskbar_h = monitor_area[3] - work_area[3]

        # determine the height and the width of the notebook
        self.nbookw = self.main_window.winfo_width()-14
        if (os.name == 'nt'):
            self.nbookh = self.main_window.winfo_height()\
                      - self.windows_taskbar_h - self.toolbar_height \
                      - self.statusbar_height # - self.mbar_height
        else:
            self.nbookh = self.main_window.winfo_height()\
                      - self.mbar_height - self.toolbar_height \
                      - self.statusbar_height

        # create the notebook
        self.nbook = tkinter.ttk.Notebook(self.mainframe, width=self.nbookw,
            height=self.nbookh)

        self.nbook.grid(row=1,column=0,columnspan=1,rowspan=1,padx=4,pady=4)

        # if the clicked tab is not the current tab
        # we need to stop all animations to avoid crashes of the frontend!
        self.nbook.bind('<ButtonPress-1>', self.switchtab)

        # ROI selection tab
        self.roitab = tk.Frame(self.nbook, width=int(round(0.9*self.nbookw)),
            height=int(round(0.95*self.nbookh)))
        self.nbook.add(self.roitab, text='  ROI Selection  ')

        # ROI selection Button
        self.roi = RegionOfInterest.ROI(self.mainframe) # instantiate roi object
        self.roiB = tk.Button(self.roitab, text='Reset ROI', command=self.select_roi,
                          height=bh, width=16)
        self.roiB.place(in_=self.roitab, anchor="c", relx=.07, rely=.17)
        # roi sequence (cropped PIL image sequence) available by attribute: "roi.roiseq"

        # initialize roiplayer
        self.roiplayer = FlipbookROI.ImgSeqPlayer(self.roitab,self.PIL_ImgSeq.directory,0,
        self.PIL_ImgSeq.sequence,self.PIL_ImgSeq.seqlength,self.roi,1)
        self.roiplayer.animate()
        self.roiplayer.stop=2

        # ----------------------- create the statusbar ------------------------

        self.statusbar_width = self.main_window.winfo_width()

        self.statusbar = statusbar.StatusBar(self.mainframe, self.statusbar_width,
                                     self.statusbar_height,
                                     self.main_window, self.PIL_ImgSeq)
        self.statusF = self.statusbar.statusbarframe
        self.statusF.grid(row=2, column=0, sticky='NESW')
        #statusF.grid_columnconfigure(0,weight=1)
        #print('width statusbar frame: ',statusF.winfo_width())
        #----------------------------------------------------------------------#


        # ---------------------- create the toolbar ---------------------------#
        self.toolbar = toolbar.Toolbar(self.mainframe, self.player,
                                   self.roiplayer, self.ptrackplayer,
                                   self.PIL_ImgSeq, self.nbook, self.roitab,
                                   self.roi, self.toolbar_height,
                                   self.nbookw, self.statusbar)
        self.toolbarF = self.toolbar.toolbarframe
        self.toolbarF.grid(row=0, column=0, columnspan=1, rowspan=1, sticky='ew')
        # -------------------------------------------------------------------- #


        # add 'Image Stabilization'-button
        self.imageregB = tk.Button(self.roitab, text='Image Stabilization',
                               command=self.image_stabilization, height=bh, width=16)
        self.imageregB.place(in_=self.roitab, anchor="c", relx=.07, rely=.07)


        # motion extraction (see Puybareau et al. 2016) i.e. subtract the mean image
        self.motionextractB = tk.Button(self.roitab, text='Subtract Mean',
            command=lambda: self.PIL_ImgSeq.extractmotion(), height=bh, width=16)
        self.motionextractB.place(in_=self.roitab, anchor="c", relx=.07, rely=0.12)


        # crop margins
        self.cropB = tk.Button(self.roitab, text='Crop Margins',
                           command=lambda: self.roiplayer.crop_margins(), height=bh, width=16)
        self.cropB.place(in_=self.roitab, anchor="c", relx=.07, rely=.22)



        # *****************************************************************************#
        #                           CBF notebook-tab                                   #
        # *****************************************************************************#

        self.cbftab = tk.Frame(self.nbook,width=int(round(0.9*self.nbookw)),
                           height=int(round(0.95*self.nbookh)))
        self.nbook.add(self.cbftab, text='  CBF  ')

        self.pwspec1frame = tk.Frame(self.cbftab, width=int(round(0.65*self.nbookw)),
                                 height=int(round(0.65*self.nbookh)))
        self.pwspec1frame.place(in_=self.cbftab, anchor='c', relx=0.5, rely=0.4)

        # Get Powerspec Button
        self.powerspectrum = Powerspec.powerspec(self.pwspec1frame, int(round(0.6*self.nbookw)),\
            int(round(0.6*self.nbookh)))

        # minfreq and maxfreq represent the lower and the upper limit
        # of the selected frequency bandwidth when determining the CBF
        self.minfreq = tk.IntVar()
        self.maxfreq = tk.IntVar()
        self.minfreq.set(5)
        self.maxfreq.set(15)

        # minscale and maxscale represent the sliders for the bandwith selection
        self.minscale = tk.Scale(self.cbftab, from_=0.5, to=50,
                             orient=tk.HORIZONTAL, length=400,
                             resolution=0.2, variable=self.minfreq, command=self.peakselector)
        self.minscale.place(in_=self.cbftab, anchor='c', relx=0.5, rely=0.8)
        self.maxscale = tk.Scale(self.cbftab, from_=0.5, to=50,
                             orient=tk.HORIZONTAL, length=400,
                             resolution=0.2, variable=self.maxfreq, command=self.peakselector)
        self.maxscale.place(in_=self.cbftab, anchor='c', relx=0.5, rely=0.85)

        self.powerspecB=tk.Button(self.cbftab, text='Powerspectrum',\
            command=lambda: self.powerspectrum.calc_powerspec(self.roiplayer.roiseq,\
        self.toolbar.fpscombo.get(),self.pwspec1frame), height=bh, width=bw)
        self.powerspecB.place(in_=self.cbftab, anchor='c', relx=0.5, rely=0.05)

        # get_cbf is defined in 'TkPowerspecPlot.py'

        self.cbfB = tk.Button(self.cbftab,text='Determine CBF',command=lambda: \
            self.powerspectrum.pwspecplot.get_cbf(float(self.minscale.get()),\
            float(self.maxscale.get()),self.toolbar.fpscombo.get()), height=bh, width=bw)
        self.cbfB.place(in_=self.cbftab, anchor='c', relx=0.5, rely=0.92)

        # self.powerspectrum.spec : holds the spectrum
        # selfpowerspectrum.freqs : holds the corresponding frequencies

        # ------------------------------------------------------------------------------
        # add a combobox in which the user is supposed to specify the
        # number of harmonics, the default is 2
        # Label and Entry Widget for specifying the number of visible harmonics
        if (self.DynamicFiltering_flag):
            self.nrharms_label=tk.Label(self.cbftab, text="Number of Harmonics :",width=22,anchor='e',\
            font=("Helvetica",11))
            self.nrharms_label.place(in_=self.cbftab, anchor='c', relx=0.75, rely=0.15)

            self.nrharms_list = [1,2,3]
            self.nrharmscombo = tkinter.ttk.Combobox(self.cbftab,values=self.nrharms_list,width=5)
            self.nrharmscombo.place(in_=self.cbftab, anchor='c', relx=0.85, rely=0.15)
            self.nrharmscombo.current(0)
        # ----------------------------------------------------------------------


        #**********************************************************************#
        #************************** activity map tab **************************#

        self.activitytab = tk.Frame(self.nbook, width=int(round(0.9*self.nbookw)),\
            height=int(round(0.95*self.nbookh)))
        self.nbook.add(self.activitytab, text='Activity Map')

        self.mapframe = tk.Frame(self.activitytab, \
            width=int(round(0.8*self.nbookh)), height=int(round(0.8*self.nbookh)))
        self.mapframe.place(in_=self.activitytab, anchor='c', relx=0.5, rely=0.55)

        self.mapframe.update()

        self.activity_map = activitymap.activitymap(self.mapframe, \
            int(round(0.8*self.nbookh)), int(round(0.8*self.nbookh))) # activity map object

        self.activityB = tk.Button(self.activitytab, text='Activtiy Map',\
            command=lambda: self.activity_map.calc_activitymap(self.mapframe,\
            self.roiplayer.roiseq,float(self.toolbar.fpscombo.get()),\
            float(self.minscale.get()), float(self.maxscale.get()),\
            self.powerspectrum), height=bh, width=bw)
        self.activityB.place(in_=self.activitytab, anchor='c', relx=0.5, rely=0.05)

        #**********************************************************************#


        # ******************** Frequency correlation tab ***********************
        # notebook tab to compute the correlation length in the activity map
        self.freqcorrtab = tk.Frame(self.nbook)
        self.nbook.add(self.freqcorrtab, text='Frequency Correlation')

        self.freqcorrB = tk.Button(self.freqcorrtab, text='Frequency Correlation',
            command=self.frequency_correlation(), height=bh, width=bw)
        self.freqcorrB.place(in_=self.freqcorrtab, anchor='c', relx=0.5, rely=0.05)
        # **********************************************************************


        # ****************** Temporal autocorrelation tab **********************
        self.tacorrtab = tk.Frame(self.nbook)
        self.nbook.add(self.tacorrtab, text='Temporal Autocorrelation')

        self.tacorr_plotframe = tk.Frame(self.tacorrtab,
            width=int(round(0.8*self.nbookh)), height=int(round(0.8*self.nbookh)))
        self.tacorr_plotframe.place(in_=self.tacorrtab, anchor='c', relx=0.5, rely=0.55)

        self.tacorrB = tk.Button(self.tacorrtab, text='Temporal Autocorrelation',
            command=lambda: self.tacorr(), height=bh, width=bw)
        self.tacorrB.place(in_=self.tacorrtab, anchor='c', relx=0.5, rely=0.05)
        # **********************************************************************


        #*****************************************************************************#
        # *************************** Single Pixel Analysis **************************# 
        if (self.SinglePixelAnalysis_flag):

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
        

        # ************************* Particle Tracking ************************ #
        if (self.ParticleTracking_flag):
            self.ptracktab = tk.Frame(self.nbook, width=int(round(0.6*self.nbookw)),
                height=int(round(0.6*self.nbookh)))
            self.nbook.add(self.ptracktab, text='Particle Tracking')

            #print('ptracktab ',nbook.index(ptracktab))

            # top left -> 'controls'
            self.trackcframe = tk.Frame(self.ptracktab, takefocus=0)
            self.trackcframe.place(in_=self.ptracktab, anchor="c")
        #**********************************************************************#


        # ********************** Dynamic Filtering *************************** #
        if (self.DynamicFiltering_flag):
            self.dynseq = DynamicFilter.DynFilter()
            self.dynfiltertab = tk.Frame(self.nbook, width=int(round(0.75*self.nbookw)),
                height=int(round(0.8*self.nbookh)))
            self.nbook.add(self.dynfiltertab, text='Dynamic Filtering')
        #**********************************************************************#


        # ****************** Spatio-Temporal Correlation ********************* #
        if (self.SpatioTemporalCorrelogram_flag):
            correlationtab = tk.Frame(nbook,width=int(round(0.75*screenw)),height=int(round(0.8*screenh)))
            nbook.add(correlationtab, text='Saptio-Temporal Correlation')

            corrB = tk.Button(correlationtab,text='Spatio-Temp. Correlogram',command=corrgram, height=bh, width=bw)
            corrB.place(in_=correlationtab, anchor="c", relx=.5, rely=.05)
        #*****************************************************************************#
        


        #**********************************************************************#
        
        if (self.kSpectrum_flag):
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
        #**********************************************************************#
        


        # ******************************************************************** #
        #                    Spatial autocorrelation tab
        # *********************************************************************#

        if (self.SpatialAcorr_flag):
            self.mcorrtab = tk.Frame(self.nbook, width=int(round(0.9*self.nbookw)),
                height=int(round(0.95*self.nbookh)))
            self.nbook.add(self.mcorrtab, text=' Spatial Autocorrelation ')

        self.mcorrB = tk.Button(self.mcorrtab, text='Mean Spatial Autocorrelation',
            command=self.meanscorrgram, height=bh, width=bw)
        self.mcorrB.place(in_=self.mcorrtab, anchor="c", relx=.5, rely=.05)

        # here we plot the mean spatial autocorrelation ('mscorr' = mean spatial correlation)  
        self.mscorrplotframe = tk.Frame(self.mcorrtab, width=int(round(0.45*self.nbookw)),
            height=int(round(0.6*self.nbookh)))
        self.mscorrplotframe.place(in_=self.mcorrtab, anchor='c', relx=0.25, rely=0.5)

        # plot a profile along a selected line going through the center of the mean spatial acorr
        self.mscorrprofileframe = tk.Frame(self.mcorrtab,
            width=int(round(0.45*self.nbookw)),height=int(round(0.6*self.nbookh)))
        self.mscorrprofileframe.place(in_=self.mcorrtab, anchor='c', relx=0.75, rely=0.5)

        # ----------------------------------------------------------------------






        # each time the application's window size gets changed -> call 'resize'
        # self.main_window.bind( "<Configure>", self.resize)

if __name__ == "__main__":

    import multiprocessing

    App = Cilialyzer()

    # -------------------------------------------------------------------------
    App.main_window.mainloop()  # loop and wait for events
    # -------------------------------------------------------------------------
