import tkinter as tk
from tkinter import ttk
import os
import sys
import webbrowser
# import multiprocessing

class Menubar:

    """
    Constructs the menubar on top of parent (main window of the application)
    """

    def about_info(self):
        """
        Displays the 'About Cilialyzer' information in a toplevel window
        """

        self.about_window = tk.Toplevel(self.parent)
        self.about_window.title('About Cilialyzer')

        # open the toplevel window in the middle of the screen
        # get the screen dimensions first:

        sw = self.about_window.winfo_screenwidth()
        sh = self.about_window.winfo_screenheight()

        win_width = 500
        win_height = 500

        posx = int(0.5*sw - 0.5*win_width)
        posy = int(0.5*sh - 0.5*win_height)

        self.about_window.geometry("%dx%d+%d+%d" % (
            win_width, win_height, posx, posy))
        self.about_window.update()

        # display logo in about window



        # text in about window
        self.textbox = tk.Text(self.about_window, height=10, width=win_width-20)

        text = """

        Cilialyzer is a freely available, easy-to-use open-source application 
        specifically designed to support and improve the analysis
        of digital recordings showing the mucociliary activity
        of respiratory epithelial cells captured by high-speed video microscopy.


        Cilialyzer is distributed under the terms of the MIT license.

        """
        self.textbox.pack()
        self.textbox.insert(tk.END, text)

    def launch_website(self):
        webbrowser.open('https://msdev87.github.io/Cilialyzer')

    def link_tutorials(self):
        """
        opens the link to the tutorials in the default webbrowser
        """
        pass

    def open_doc(self):
        """
        Opens the documentation in the webbrowser
        """
        # webbrowser.open_new(r'./Doc/help.pdf')
        pass

    def change_theme(self):
        self.style.theme_use(self.selected_theme.get())

    def write_flags(self):
        print('this is a test, Cilialyzer writes flags now')
        os.remove('config/feature_flags.txt')
        f = open('config/feature_flags.txt', 'a')
        f.write(str(int(self.ROISelection_flag))+"\n")
        f.write(str(int(self.CBF_flag))+"\n")
        f.write(str(int(self.ActivityMap_flag))+"\n")
        f.write(str(int(self.SinglePixelAnalysis_flag))+"\n")
        f.write(str(int(self.MotionTracking_flag))+"\n")
        f.write(str(int(self.ParticleTracking_flag))+"\n")
        f.write(str(int(self.DynamicFiltering_flag))+"\n")
        f.write(str(int(self.SpatioTemporalCorrelogram_flag))+"\n")
        f.write(str(int(self.kSpectrum_flag))+"\n")
        f.write(str(int(self.SpatialAcorr_flag))+"\n")
        f.write(str(int(self.TempAcorr_flag))+"\n")
        f.write(str(int(self.WindowedAnalysis_flag))+"\n")
        f.write(str(int(self.opticalflow_flag))+"\n")
        f.close()

    def change_ptrackflag(self):
        if (self.ParticleTracking_flag):
            self.ParticleTracking_flag = 0
            self.ptrackB['text'] = ' - Particle tracking   '
        else:
            self.ParticleTracking_flag = 1
            self.ptrackB['text'] = ' + Particle tracking   '

    def change_tacorrflag(self):
        if (self.TempAcorr_flag):
            self.TempAcorr_flag = 0
            self.tacorrB['text'] = ' - Temporal autocorrelation   '
        else:
            self.TempAcorr_flag = 1
            self.tacorrB['text'] = ' + Temporal autocorrelation   '

    def change_dfflag(self):
        if (self.DynamicFiltering_flag):
            self.DynamicFiltering_flag = 0
            self.dfB['text'] = ' - Dynamic filtering   '
        else:
            self.DynamicFiltering_flag = 1
            self.dfB['text'] = ' + Dynamic filtering   '

    def change_sacorrflag(self):
        if (self.SpatialAcorr_flag):
            self.SpatialAcorr_flag = 0
            self.sacorrB['text'] = ' - Spatial autocorrelation   '
        else:
            self.SpatialAcorr_flag = 1
            self.sacorrB['text'] = ' + Spatial autocorrelation   '

    def change_stcorrflag(self):
        if (self.SpatioTemporalCorrelogram_flag):
            self.SpatioTemporalCorrelogram_flag = 0
            self.stcorrB['text'] = ' - Space-time correlation   '
        else:
            self.SpatioTemporalCorrelogram_flag = 1
            self.stcorrB['text'] = ' + Space-time correlation   '

    def change_offlag(self):
        if (self.opticalflow_flag):
            self.opticalflow_flag = 0
            self.ofB['text'] = ' - Optical flow   '
        else:
            self.opticalflow_flag = 1
            self.ofB['text'] = ' + Optical flow   '

    def change_waflag(self):
        if (self.WindowedAnalysis_flag):
            self.WindowedAnalysis_flag = 0
            self.waB['text'] = ' - Windowed analysis   '
        else:
            self.WindowedAnalysis_flag = 1
            self.waB['text'] = ' + Windowed analysis   '

    def apply_settings(self):
        """
        Save current settings to file and restart the Cilialyer
        """

        self.write_flags()

        self.save_defaults()

        MsgBox = tk.messagebox.askquestion ('Restart required',
        'A restart of Cilialyzer is required for your changes to take effect. Restart Cilialyzer now?',icon = 'question')

        if (MsgBox == 'yes'):
            self.cfg_win.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            self.cfg_win.destroy()


    def save_defaults(self):
        #print('entering save_defaults')

        # save new defaults fps values
        self.fps_list[0] = int(self.entry_fps0.get())
        self.fps_list[1] = int(self.entry_fps1.get())
        self.fps_list[2] = int(self.entry_fps2.get())
        self.fps_list[3] = int(self.entry_fps3.get())
        self.fps_list[4] = int(self.entry_fps4.get())

        if (os.path.exists('config/fps_defaults.txt')):
            os.remove('config/fps_defaults.txt')
        f = open('config/fps_defaults.txt', 'a')
        f.write(str(self.fps_list[0])+"\n")
        f.write(str(self.fps_list[1])+"\n")
        f.write(str(self.fps_list[2])+"\n")
        f.write(str(self.fps_list[3])+"\n")
        f.write(str(self.fps_list[4])+"\n")
        f.close()

        # save new default pixelsize values
        self.pixelsize_list[0] = int(self.entry_pixelsize0.get())
        self.pixelsize_list[1] = int(self.entry_pixelsize1.get())
        self.pixelsize_list[2] = int(self.entry_pixelsize2.get())
        self.pixelsize_list[3] = int(self.entry_pixelsize3.get())
        self.pixelsize_list[4] = int(self.entry_pixelsize4.get())

        if (os.path.exists('config/pixelsize_defaults.txt')):
            os.remove('config/pixelsize_defaults.txt')
        f = open('config/pixelsize_defaults.txt', 'a')
        f.write(str(self.pixelsize_list[0])+"\n")
        f.write(str(self.pixelsize_list[1])+"\n")
        f.write(str(self.pixelsize_list[2])+"\n")
        f.write(str(self.pixelsize_list[3])+"\n")
        f.write(str(self.pixelsize_list[4])+"\n")
        f.close()

        # save default of number of cores to be used:
        if (os.path.exists('config/cores_default.txt')):
            os.remove('config/cores_default.txt')
        f = open('config/cores_default.txt', 'a')
        f.write(str(self.entry_nc.get()))
        f.close()

        # save self.skipframe 
        if (os.path.exists('config/skipframe_default.txt')):
            os.remove('config/skipframe_default.txt')
        f = open('config/skipframe_default.txt', 'a')
        f.write(str(self.skipframecombo.get()))
        f.close()

        MsgBox = tk.messagebox.askquestion ('Restart required',
            'A restart of the Cilialyzer is required for your changes to take effect. Restart Cilialyzer now?',icon = 'question')

        if (MsgBox == 'yes'):
            self.cfg_win.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            self.cfg_win.destroy()

    def configure(self):
        """
        Opens a toplevel window in which the appearance can be configured
        """

        #print('Entering configure')

        self.cfg_win = tk.Toplevel(self.parent)
        self.cfg_win.title('Configure Cilialyzer')

        # open the toplevel window in the middle of the screen               
        # get the screen dimensions first:                                   

        sw = self.cfg_win.winfo_screenwidth()
        sh = self.cfg_win.winfo_screenheight()

        win_width = 650
        win_height = 600

        posx = int(0.5*sw - 0.5*win_width)
        posy = int(0.5*sh - 0.5*win_height)

        self.cfg_win.geometry("%dx%d+%d+%d" % (win_width,win_height,posx,posy))
        self.cfg_win.update()

        # add cfg_notebook 
        self.cfg_nbook = tk.ttk.Notebook(self.cfg_win, width=win_width-10, height=win_height-70)
        self.cfg_nbook.grid(row=0,column=0,padx=4,pady=4)

        # ---------------------- FPS defaults tab -----------------------------
        # add FPS Defaults tab
        self.FPSdefaults_tab = tk.Frame(self.cfg_win, width=win_width-10, height=win_height-70)
        self.cfg_nbook.add(self.FPSdefaults_tab, text=' FPS defaults ')
        # ---------------------------------------------------------------------

        # -------------------- Pixelsize defaults tab -------------------------
        # add pixelsize defaults tab
        self.psdefaults_tab = tk.Frame(self.cfg_win, width=win_width-10, height=win_height-70)
        self.cfg_nbook.add(self.psdefaults_tab, text=' Pixelsize defaults ')
        # ---------------------------------------------------------------------

        # -------- read defaults FPS list from file
        # read file fps_defaults.txt (if it exists)
        if (os.path.exists('config/fps_defaults.txt')):
            with open('config/fps_defaults.txt') as f:
                fps_defaults = f.readlines()
                fps_defaults = [line.rstrip() for line in fps_defaults]
                self.fps_list = fps_defaults
        else:
            self.fps_list = []

        # if FPS-list is not complete --> create default FPS-list
        if (len(self.fps_list) < 5):
            self.fps_list = [300, 200, 120, 100, 30]
            if (os.path.exists('config/fps_defaults.txt')):
                os.remove('config/fps_defaults.txt')
            f = open('config/fps_defaults.txt', 'a')
            f.write(str(self.fps_list[0])+"\n")
            f.write(str(self.fps_list[1])+"\n")
            f.write(str(self.fps_list[2])+"\n")
            f.write(str(self.fps_list[3])+"\n")
            f.write(str(self.fps_list[4])+"\n")
            f.close()

        # -------------- FPS defaults (label and entry widgets) ---------------
        # create text and entry widget for FPS-list

        self.fps_frame = tk.LabelFrame(self.FPSdefaults_tab, text=' Set list of default FPS values ',\
            labelanchor='nw', borderwidth=2, padx=10, pady=10,relief=tk.RIDGE,font=("Helvetica", 11, "bold"))
        self.fps_frame.grid(row=0,column=0,padx=15,pady=15)

        fps0_label=tk.Label(self.fps_frame, text=" Default FPS :",
            anchor='e', font=("TkDefaultFont",10), width=14)
        fps0_label.grid(row=0,column=0,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.25, rely=.2)

        # add entry widget (to set default fps)
        self.entry_fps0 = tk.Entry(self.fps_frame, width=5)
        #self.entry_fps0.place(in_=self.fps_frame, anchor="c", relx=.6, rely=.2)
        self.entry_fps0.grid(row=0,column=1,padx=10,pady=5)
        # display current default
        self.entry_fps0.insert(0, str(self.fps_list[0]))

        # create text widgets for FPS dropdown list
        fps1_label=tk.Label(self.fps_frame, text=" 1. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=14)
        fps1_label.grid(row=1,column=0,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.25, rely=.3)

        fps2_label=tk.Label(self.fps_frame, text=" 2. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=14)
        fps2_label.grid(row=2,column=0,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.25, rely=.35)

        fps3_label=tk.Label(self.fps_frame, text=" 3. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=14)
        fps3_label.grid(row=3, column=0,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.25, rely=.4)

        fps4_label=tk.Label(self.fps_frame, text=" 4. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=14)
        fps4_label.grid(row=4, column=0,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.25, rely=.45)

        self.entry_fps1 = tk.Entry(self.fps_frame, width=5)
        self.entry_fps1.grid(row=1,column=1,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.6, rely=.3)
        self.entry_fps1.insert(0, str(self.fps_list[1]))

        self.entry_fps2 = tk.Entry(self.fps_frame, width=5)
        self.entry_fps2.grid(row=2, column=1,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.6, rely=.35)
        self.entry_fps2.insert(0, str(self.fps_list[2]))

        self.entry_fps3 = tk.Entry(self.fps_frame, width=5)
        self.entry_fps3.grid(row=3, column=1,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.6, rely=.4)
        self.entry_fps3.insert(0, str(self.fps_list[3]))

        self.entry_fps4 = tk.Entry(self.fps_frame, width=5)
        self.entry_fps4.grid(row=4, column=1,padx=10,pady=5)
        #place(in_=self.fps_frame, anchor="c", relx=.6, rely=.45)
        self.entry_fps4.insert(0, str(self.fps_list[4]))

        # 'Save & Exit' button 
        #self.save_defaultsB = tk.Button(self.FPSdefaults_tab, text=' Apply ',
        #    command=self.save_defaults, height=1, width=15)
        #self.save_defaultsB.place(in_=self.FPSdefaults_tab, anchor="c", relx=.5, rely=.7)

        # ------------------- Pixelsize defaults tab -------------------------- 

        self.ps_frame = tk.LabelFrame(self.psdefaults_tab, text=' Set list of default pixelsizes ',\
            labelanchor='nw', borderwidth=2, padx=10, pady=10,relief=tk.RIDGE,font=("Helvetica", 11, "bold"))
        self.ps_frame.grid(row=0,column=0,padx=15,pady=15)

        pixelsize0_label=tk.Label(self.ps_frame,\
            text=" Default pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize0_label.grid(row=0,column=0,padx=10,pady=5)

        pixelsize1_label=tk.Label(self.ps_frame,\
            text=" 1. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize1_label.grid(row=1,column=0,padx=10,pady=5)

        pixelsize2_label=tk.Label(self.ps_frame,\
            text=" 2. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize2_label.grid(row=2,column=0,padx=10,pady=5)

        pixelsize3_label=tk.Label(self.ps_frame,\
            text=" 3. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize3_label.grid(row=3,column=0,padx=10,pady=5)

        pixelsize4_label=tk.Label(self.ps_frame,\
            text=" 4. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize4_label.grid(row=4,column=0,padx=10,pady=5)

        # read pixelsize_defaults.txt (if it exists)
        if (os.path.exists('config/pixelsize_defaults.txt')):
            with open('config/pixelsize_defaults.txt') as f:
                pixelsize_defaults = f.readlines()
                pixelsize_defaults = [line.rstrip() for line in pixelsize_defaults]
                self.pixelsize_list = pixelsize_defaults
        else:
            self.pixelsize_list = []

        if (len(self.pixelsize_list) < 5):
            self.pixelsize_list = [1779, 345, 173, 86, 1000]

            if (os.path.exists('config/pixelsize_defaults.txt')):
                os.remove('config/pixelsize_defaults.txt')
            f = open('config/pixelsize_defaults.txt', 'a')
            f.write(str(self.pixelsize_list[0])+"\n")
            f.write(str(self.pixelsize_list[1])+"\n")
            f.write(str(self.pixelsize_list[2])+"\n")
            f.write(str(self.pixelsize_list[3])+"\n")
            f.write(str(self.pixelsize_list[4])+"\n")
            f.close()

        # add entry widget (to set default pixelsize)
        self.entry_pixelsize0 = tk.Entry(self.ps_frame, width=5)
        self.entry_pixelsize0.grid(row=0,column=1,padx=10,pady=5)
        self.entry_pixelsize0.insert(0, str(self.pixelsize_list[0]))

        self.entry_pixelsize1 = tk.Entry(self.ps_frame, width=5)
        self.entry_pixelsize1.grid(row=1,column=1,padx=10,pady=5)
        self.entry_pixelsize1.insert(0, str(self.pixelsize_list[1]))

        self.entry_pixelsize2 = tk.Entry(self.ps_frame, width=5)
        self.entry_pixelsize2.grid(row=2,column=1,padx=10,pady=5)
        self.entry_pixelsize2.insert(0, str(self.pixelsize_list[2]))

        self.entry_pixelsize3 = tk.Entry(self.ps_frame, width=5)
        self.entry_pixelsize3.grid(row=3,column=1,padx=10,pady=5)
        self.entry_pixelsize3.insert(0, str(self.pixelsize_list[3]))

        self.entry_pixelsize4 = tk.Entry(self.ps_frame, width=5)
        self.entry_pixelsize4.grid(row=4,column=1,padx=10,pady=5)
        self.entry_pixelsize4.insert(0, str(self.pixelsize_list[4]))

        # 'Save & Exit' button 
        #self.save_defaultpsB = tk.Button(self.psdefaults_tab, text=' Apply ',
        #    command=self.save_defaults, height=1, width=15)
        #self.save_defaultpsB.place(in_=self.psdefaults_tab, anchor="c", relx=.5, rely=.7)
        # ---------------------------------------------------------------------

        # -------------------- Miscellaneous settings tab ----------------------------- 
        self.misc_tab=tk.Frame(self.cfg_win, width=win_width-10, height=win_height-70)
        self.cfg_nbook.add(self.misc_tab, text=' Miscellaneous ')

        # available cores
        ncores = os.cpu_count() # multiprocessing.cpu_count()
        ncores_init = ncores-1

        # check whether 'cores_default.txt' exists: 
        if (os.path.exists('config/cores_default.txt')):
            # if it exists, read value and check whether the value makes sense
            f = open('config/cores_default.txt', 'r')
            nc = int(f.read())
            if ((nc > 0) and (nc <= ncores-1)):
                # value makes sense
                ncores_init = nc
            else:
                # strange value, rewrite default 
                os.remove('config/cores_default.txt')
                f = open('config/cores_default.txt', 'a')
                f.write(str(ncores_init))
            f.close()
        else:
            f = open('config/cores_default.txt', 'a')
            f.write(str(ncores_init))

        self.miscframe1 = tk.LabelFrame(self.misc_tab, text=' Image stabilization settings ',\
            labelanchor='nw', borderwidth=2, padx=0, pady=0,relief=tk.RIDGE,font=("Helvetica", 11, "bold"))
        self.miscframe1.grid(row=0,column=0,padx=15,pady=15)

        # State number of avialable cores in label: 
        self.ncores_label=tk.Label(self.miscframe1,text=\
            'Please specify how many CPU cores (out of '+ str(ncores) +') can be used by Cilialyzer : ',\
            anchor="e",width=60)
        self.ncores_label.grid(row=0, column=0,padx=10,pady=5)
        #place(in_=self.miscframe1,anchor="e",relx=.8,rely=.4)

        self.entry_nc = tk.Entry(self.miscframe1, width=5)
        self.entry_nc.grid(row=0, column=1, padx=10, pady=5)
        #place(in_=self.miscframe1, anchor="c", relx=.85, rely=.4)
        self.entry_nc.insert(0, ncores_init)

        # --------------------------------------------------------------------
        # The user can choose how many frames can be skipped in the image 
        # stabilization process (to speed up the computation)

        skipframe_list = [0,1,2,3]

        # get the default from file for self.skipframe 

        # check whether 'skipframe_default.txt' exists: 
        if (os.path.exists('config/skipframe_default.txt')):
            # if it exists, read value 
            f = open('config/skipframe_default.txt', 'r')
            try:
                self.skipframe = int(f.read())
                f.close()
            except:
                self.skipframe = 1
                f.close()
        else:
            self.skipframe = 1
            f = open('config/skipframe_default.txt', 'a')
            f.write(str(self.skipframe))

        self.skipframe_label=tk.Label(self.miscframe1,text=\
            'Specify how many frames can be skipped during video stabilization: ',\
            anchor="e",width=60)
        self.skipframe_label.grid(row=1, column=0,padx=10,pady=5)

        self.skipframecombo = tk.ttk.Combobox(self.miscframe1,values=skipframe_list,width=4)
        self.skipframecombo.grid(row=1,column=1,padx=10,pady=5)
        self.skipframecombo.current(self.skipframe)

        # ---------------------------------------------------------------------




        # ------------------- available features tab --------------------------
        # add 'Available features'-tab
        self.availfeat_tab = tk.Frame(self.cfg_win, width=win_width-10, height=win_height-70)
        self.cfg_nbook.add(self.availfeat_tab, text=' Select features ')

        # read feature flags
        with open('config/feature_flags.txt') as f:
            fflags = f.readlines()
            fflags = [line.rstrip() for line in fflags]

        self.ROISelection_flag = bool(int(fflags[0]))
        self.CBF_flag = bool(int(fflags[1]))
        self.ActivityMap_flag = bool(int(fflags[2]))
        self.SinglePixelAnalysis_flag = bool(int(fflags[3]))
        self.MotionTracking_flag = bool(int(fflags[4]))
        self.ParticleTracking_flag = bool(int(fflags[5]))
        self.DynamicFiltering_flag = bool(int(fflags[6]))
        self.SpatioTemporalCorrelogram_flag = bool(int(fflags[7]))
        self.kSpectrum_flag = bool(int(fflags[8]))
        self.SpatialAcorr_flag = bool(int(fflags[9]))
        self.TempAcorr_flag = bool(int(fflags[10]))
        self.WindowedAnalysis_flag = bool(int(fflags[11]))
        self.opticalflow_flag = bool(int(fflags[12]))

        # ---------- Button to remove/add particle tracking tab ---------------
        if (self.ParticleTracking_flag):
            self.ptrackB = tk.Button(self.availfeat_tab,
                text=' + Particle tracking   ',
                command=self.change_ptrackflag, height=1, width=23)
        else:
            self.ptrackB = tk.Button(self.availfeat_tab,\
            text=' - Particle tracking   ', command=self.change_ptrackflag,
            height=1, width=23)
        self.ptrackB.place(in_=self.availfeat_tab, anchor='c', relx=.5,rely=.07)
        # ---------------------------------------------------------------------
        # --------- Button to remove/add TempAcorr tab ----------------------- 
        if (self.TempAcorr_flag):
            self.tacorrB = tk.Button(self.availfeat_tab,
                text=' + Temporal autocorrelation   ',
                command=self.change_tacorrflag, height=1, width=23)
        else:
            self.tacorrB = tk.Button(self.availfeat_tab,\
                text=' - Temporal autocorrelation   ',\
                command=self.change_tacorrflag, height=1, width=23)
        self.tacorrB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.14)
        # ---------------------------------------------------------------------
        # ------- Button to remove/add Dyn. filtering tab ---------------------  
        if (self.DynamicFiltering_flag):
            self.dfB = tk.Button(self.availfeat_tab, text=' + Dynamic filtering   ',
            command=self.change_dfflag, height=1, width=23)
        else:
            self.dfB = tk.Button(self.availfeat_tab,\
                text=' - Dynamic filtering   ',\
                command=self.change_dfflag, height=1, width=23)
        self.dfB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.21)
        # ---------------------------------------------------------------------
        # --------------- Button to remove/add spatial acorr tab --------------
        if (self.SpatialAcorr_flag):
            self.sacorrB = tk.Button(self.availfeat_tab,
                text=' + Spatial autocorrelogram   ',
                command=self.change_sacorrflag, height=1, width=23)
        else:
            self.sacorrB = tk.Button(self.availfeat_tab,\
                text=' - Spatial autocorrelogram   ',\
                command=self.change_sacorrflag, height=1, width=23)
        self.sacorrB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.28)
        # ---------------------------------------------------------------------
        # ----------- Button to remove/add Space-time corr tab  ---------------
        if (self.SpatioTemporalCorrelogram_flag):
            self.stcorrB = tk.Button(self.availfeat_tab,
                text=' + Space-time correlation   ',
                command=self.change_stcorrflag, height=1, width=23)
        else:
            self.stcorrB = tk.Button(self.availfeat_tab,\
                text=' - Space-time correlation   ',\
                command=self.change_stcorrflag, height=1, width=23)
        self.stcorrB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.35)
        # ---------------------------------------------------------------------
        # ------------- Button to remove/add optical flow tab  ----------------
        if (self.opticalflow_flag):
            self.ofB = tk.Button(self.availfeat_tab,
                text=' + Optical flow   ',
                command=self.change_offlag, height=1, width=23)
        else:
            self.ofB = tk.Button(self.availfeat_tab,\
                text=' - Optical flow   ',\
                command=self.change_offlag, height=1, width=23)
        self.ofB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.42)
        # ---------------------------------------------------------------------

        # ------------- Button to remove/add windowed analysis ----------------
        if (self.WindowedAnalysis_flag):
            self.waB = tk.Button(self.availfeat_tab,
                text=' + Windowed analysis   ',
                command=self.change_waflag, height=1, width=23)
        else:
            self.waB = tk.Button(self.availfeat_tab,\
                text=' - Windowed analysis   ',\
                command=self.change_waflag, height=1, width=23)
        self.waB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.49)
        # ---------------------------------------------------------------------

        # ------------------------- 'Apply' button ----------------------------
        # The apply button saves all the new settings and restarts Cilialyzer
        self.applyB = tk.Button(self.cfg_win, text=' Apply ',
            command=self.apply_settings, height=1, width=23,bg='gray65')
        self.applyB.grid(row=1,column=0, padx=4,pady=3)
        # ---------------------------------------------------------------------

















        # -------------------- Theme tab --------------------------------------
        # add 'themes' tab 
        self.themestab = tk.Frame(self.cfg_nbook,width=win_width-10,height=win_height-70)
        self.cfg_nbook.add(self.themestab, text=' Theme ')

        self.style = ttk.Style(self.parent)
        # get available themes
        self.themes = self.style.theme_names()
        self.current_theme = self.style.theme_use()

        # create radiobutton to switch between themes 

        self.selected_theme = tk.StringVar()

        for theme in self.themes:
            rb = ttk.Radiobutton(self.themestab, text=theme, value=theme,
                        variable=self.selected_theme, command=self.change_theme)
            rb.grid()


    def __init__(self, parent):

        self.parent = parent
        self.myfont = ("TkDefaultFont", 10)

        # create the menubar of parent tk-window
        self.menubar = tk.Menu(self.parent, bg='gray30', fg='gray95', font=self.myfont)

        # create 'File'-tab in menubar
        self.mfile = tk.Menu(self.menubar)
        # create submenus of File-tab:
        self.mfile.add_command(label="Open sequence...", font=self.myfont)
        self.mfile.add_command(label="Open video...",font=self.myfont)

        # create 'Appearance'-tab 
        self.mapp = tk.Menu(self.menubar)
        # create submenus
        self.mapp.add_command(label="Configure...", command=self.configure,\
                                font=self.myfont)

        # create 'Help'-tab 
        self.mhelp = tk.Menu(self.menubar)

        #self.mhelp.add_command(label='Documentation', command=self.open_doc)
        #self.mhelp.add_command(label='Watch tutorial videos',
        #                       command=self.link_tutorials)
        self.mhelp.add_command(label='Launch Cilialyzer website',
                command=self.launch_website)
        self.mhelp.add_command(label='About',
                               command=self.about_info, font=self.myfont, state=tk.DISABLED)

        # create 'Exit'-tab
        self.mexit = tk.Menu(self.menubar)

        # add menus to menubar: 
        self.menubar.add_cascade(menu=self.mfile,label="File ",font=self.myfont)
        self.menubar.add_cascade(label=" Settings ",font=self.myfont,menu=self.mapp)
        self.menubar.add_cascade(label=" Help ",font=self.myfont,menu=self.mhelp)
        self.menubar.add_cascade(label=" Exit ",font=self.myfont,menu=self.mexit)

if __name__ == "__main__":

    root = tk.Tk()
    root.geometry('300x200')
    mbar = Menubar(root)
    root.config(menu=mbar.menubar)
    root.mainloop()
