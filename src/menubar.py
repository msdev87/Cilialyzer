import tkinter as tk
from tkinter import ttk
import os
import sys
import webbrowser


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
        os.remove('feature_flags.txt')
        f = open('feature_flags.txt','a')
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

        MsgBox = tk.messagebox.askquestion ('Restart required',
        'A restart of Cilialyzer is required for your changes to take effect. Restart Cilialyzer now?',icon = 'question')

        if (MsgBox == 'yes'):
            self.cfg_win.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            self.cfg_win.destroy()


    def save_defaults(self):
        # save new defaults fps values
        self.fps_list[0] = int(self.entry_fps0.get())
        self.fps_list[1] = int(self.entry_fps1.get())
        self.fps_list[2] = int(self.entry_fps2.get())
        self.fps_list[3] = int(self.entry_fps3.get())
        self.fps_list[4] = int(self.entry_fps4.get())

        if (os.path.exists('fps_defaults.txt')):
            os.remove('fps_defaults.txt')
        f = open('fps_defaults.txt','a')
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

        if (os.path.exists('pixelsize_defaults.txt')):
            os.remove('pixelsize_defaults.txt')
        f = open('pixelsize_defaults.txt','a')
        f.write(str(self.pixelsize_list[0])+"\n")
        f.write(str(self.pixelsize_list[1])+"\n")
        f.write(str(self.pixelsize_list[2])+"\n")
        f.write(str(self.pixelsize_list[3])+"\n")
        f.write(str(self.pixelsize_list[4])+"\n")
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
        self.cfg_win = tk.Toplevel(self.parent)
        self.cfg_win.title('Configure Cilialyzer')

        # open the toplevel window in the middle of the screen               
        # get the screen dimensions first:                                   

        sw = self.cfg_win.winfo_screenwidth()
        sh = self.cfg_win.winfo_screenheight()

        win_width = 450
        win_height = 600

        posx = int(0.5*sw - 0.5*win_width)
        posy = int(0.5*sh - 0.5*win_height)

        self.cfg_win.geometry("%dx%d+%d+%d" % (win_width,win_height,posx,posy))
        self.cfg_win.update()

        # add cfg_notebook 
        self.cfg_nbook = tk.ttk.Notebook(self.cfg_win, width=440, height=550)
        self.cfg_nbook.grid(row=0,column=0,padx=4,pady=4)

        # ---------------------- FPS defaults tab -----------------------------
        # add FPS Defaults tab
        self.FPSdefaults_tab = tk.Frame(self.cfg_win, width=430, height=540)
        self.cfg_nbook.add(self.FPSdefaults_tab, text=' FPS defaults ')
        # ---------------------------------------------------------------------

        # -------------------- Pixelsize defaults tab -------------------------
        # add pixelsize defaults tab
        self.psdefaults_tab = tk.Frame(self.cfg_win, width=430, height=540)
        self.cfg_nbook.add(self.psdefaults_tab, text=' Pixelsize defaults ')
        # ---------------------------------------------------------------------

        # -------- read defaults FPS list from file
        # read file fps_defaults.txt (if it exists)
        if (os.path.exists('fps_defaults.txt')):
            with open('fps_defaults.txt') as f:
                fps_defaults = f.readlines()
                fps_defaults = [line.rstrip() for line in fps_defaults]
                self.fps_list = fps_defaults
        else:
            self.fps_list = []

        # if FPS-list is not complete --> create default FPS-list
        if (len(self.fps_list) < 5):
            self.fps_list = [300, 200, 120, 100, 30]
            if (os.path.exists('fps_defaults.txt')):
                os.remove('fps_defaults.txt')
            f = open('fps_defaults.txt','a')
            f.write(str(self.fps_list[0])+"\n")
            f.write(str(self.fps_list[1])+"\n")
            f.write(str(self.fps_list[2])+"\n")
            f.write(str(self.fps_list[3])+"\n")
            f.write(str(self.fps_list[4])+"\n")
            f.close()

        # -------------- FPS defaults (label and entry widgets) ---------------
        # create text and entry widget for FPS-list 
        fps0_label=tk.Label(self.FPSdefaults_tab, text=" Default FPS :",
            anchor='e', font=("TkDefaultFont",10), width=22)
        fps0_label.place(in_=self.FPSdefaults_tab, anchor="c", relx=.25, rely=.2)

        # add entry widget (to set default fps)
        self.entry_fps0 = tk.Entry(self.FPSdefaults_tab, width=10)
        self.entry_fps0.place(in_=self.FPSdefaults_tab, anchor="c", relx=.6, rely=.2)
        # display current default
        self.entry_fps0.insert(0, str(self.fps_list[0]))

        # create text widgets for FPS dropdown list
        fps1_label=tk.Label(self.FPSdefaults_tab, text=" 1. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=22)
        fps1_label.place(in_=self.FPSdefaults_tab, anchor="c", relx=.25, rely=.3)

        fps2_label=tk.Label(self.FPSdefaults_tab, text=" 2. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=22)
        fps2_label.place(in_=self.FPSdefaults_tab, anchor="c", relx=.25, rely=.35)

        fps3_label=tk.Label(self.FPSdefaults_tab, text=" 3. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=22)
        fps3_label.place(in_=self.FPSdefaults_tab, anchor="c", relx=.25, rely=.4)

        fps4_label=tk.Label(self.FPSdefaults_tab, text=" 4. Optional FPS :",
            anchor='e', font=("TkDefaultFont",10), width=22)
        fps4_label.place(in_=self.FPSdefaults_tab, anchor="c", relx=.25, rely=.45)

        self.entry_fps1 = tk.Entry(self.FPSdefaults_tab, width=10)
        self.entry_fps1.place(in_=self.FPSdefaults_tab, anchor="c", relx=.6, rely=.3)
        self.entry_fps1.insert(0, str(self.fps_list[1]))

        self.entry_fps2 = tk.Entry(self.FPSdefaults_tab, width=10)
        self.entry_fps2.place(in_=self.FPSdefaults_tab, anchor="c", relx=.6, rely=.35)
        self.entry_fps2.insert(0, str(self.fps_list[2]))

        self.entry_fps3 = tk.Entry(self.FPSdefaults_tab, width=10)
        self.entry_fps3.place(in_=self.FPSdefaults_tab, anchor="c", relx=.6, rely=.4)
        self.entry_fps3.insert(0, str(self.fps_list[3]))

        self.entry_fps4 = tk.Entry(self.FPSdefaults_tab, width=10)
        self.entry_fps4.place(in_=self.FPSdefaults_tab, anchor="c", relx=.6, rely=.45)
        self.entry_fps4.insert(0, str(self.fps_list[4]))

        # 'Save & Exit' button 
        self.save_defaultsB = tk.Button(self.FPSdefaults_tab, text=' Apply ',
            command=self.save_defaults, height=1, width=15)
        self.save_defaultsB.place(in_=self.FPSdefaults_tab, anchor="c", relx=.5, rely=.7)

        # ------------------- Pixelsize defaults tab -------------------------- 

        pixelsize0_label=tk.Label(self.psdefaults_tab,\
            text=" Default pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize0_label.place(in_=self.psdefaults_tab, anchor="c", relx=.25, rely=.2)

        pixelsize1_label=tk.Label(self.psdefaults_tab,\
            text=" 1. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize1_label.place(in_=self.psdefaults_tab, anchor="c", relx=.25, rely=.3)

        pixelsize2_label=tk.Label(self.psdefaults_tab,\
            text=" 2. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize2_label.place(in_=self.psdefaults_tab, anchor="c", relx=.25, rely=.35)

        pixelsize3_label=tk.Label(self.psdefaults_tab,\
            text=" 3. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize3_label.place(in_=self.psdefaults_tab, anchor="c", relx=.25, rely=.4)

        pixelsize4_label=tk.Label(self.psdefaults_tab,\
            text=" 4. Optional pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize4_label.place(in_=self.psdefaults_tab, anchor="c", relx=.25, rely=.45)

        # read pixelsize_defaults.txt (if it exists)
        if (os.path.exists('pixelsize_defaults.txt')):
            with open('pixelsize_defaults.txt') as f:
                pixelsize_defaults = f.readlines()
                pixelsize_defaults = [line.rstrip() for line in pixelsize_defaults]
                self.pixelsize_list = pixelsize_defaults
        else:
            self.pixelsize_list = []

        if (len(self.pixelsize_list) < 5):
            self.pixelsize_list = [1779, 345, 173, 86, 1000]

            if (os.path.exists('pixelsize_defaults.txt')):
                os.remove('pixelsize_defaults.txt')
            f = open('pixelsize_defaults.txt','a')
            f.write(str(self.pixelsize_list[0])+"\n")
            f.write(str(self.pixelsize_list[1])+"\n")
            f.write(str(self.pixelsize_list[2])+"\n")
            f.write(str(self.pixelsize_list[3])+"\n")
            f.write(str(self.pixelsize_list[4])+"\n")
            f.close()

        # add entry widget (to set default pixelsize)
        self.entry_pixelsize0 = tk.Entry(self.psdefaults_tab, width=10)
        self.entry_pixelsize0.place(in_=self.psdefaults_tab, anchor="c", relx=.6, rely=.2)
        # display current default
        self.entry_pixelsize0.insert(0, str(self.pixelsize_list[0]))

        self.entry_pixelsize1 = tk.Entry(self.psdefaults_tab, width=10)
        self.entry_pixelsize1.place(in_=self.psdefaults_tab, anchor="c", relx=.6, rely=.3)
        self.entry_pixelsize1.insert(0, str(self.pixelsize_list[1]))

        self.entry_pixelsize2 = tk.Entry(self.psdefaults_tab, width=10)
        self.entry_pixelsize2.place(in_=self.psdefaults_tab, anchor="c", relx=.6, rely=.35)
        self.entry_pixelsize2.insert(0, str(self.pixelsize_list[2]))

        self.entry_pixelsize3 = tk.Entry(self.psdefaults_tab, width=10)
        self.entry_pixelsize3.place(in_=self.psdefaults_tab, anchor="c", relx=.6, rely=.4)
        self.entry_pixelsize3.insert(0, str(self.pixelsize_list[3]))

        self.entry_pixelsize4 = tk.Entry(self.psdefaults_tab, width=10)
        self.entry_pixelsize4.place(in_=self.psdefaults_tab, anchor="c", relx=.6, rely=.45)
        self.entry_pixelsize4.insert(0, str(self.pixelsize_list[4]))

        # 'Save & Exit' button 
        self.save_defaultpsB = tk.Button(self.psdefaults_tab, text=' Apply ',
            command=self.save_defaults, height=1, width=15)
        self.save_defaultpsB.place(in_=self.psdefaults_tab, anchor="c", relx=.5, rely=.7)
        # ---------------------------------------------------------------------

        # ------------------- available features tab --------------------------
        # add 'Available features'-tab
        self.availfeat_tab = tk.Frame(self.cfg_win, width=430, height=540)
        self.cfg_nbook.add(self.availfeat_tab, text=' Select features ')

        # read feature flags
        with open('feature_flags.txt') as f:
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

        # ---------- Button to remove/add particle tracking tab ---------------
        if (self.ParticleTracking_flag):
            self.ptrackB = tk.Button(self.availfeat_tab,
                text=' + Particle tracking   ',
                command=self.change_ptrackflag, height=1, width=20)
        else:
            self.ptrackB = tk.Button(self.availfeat_tab,\
            text=' - Particle tracking   ', command=self.change_ptrackflag,
            height=1, width=20)
        self.ptrackB.place(in_=self.availfeat_tab, anchor='c', relx=.5,rely=.2)
        # ---------------------------------------------------------------------
        # --------- Button to remove/add TempAcorr tab ----------------------- 
        if (self.TempAcorr_flag):
            self.tacorrB = tk.Button(self.availfeat_tab,
                text=' + Temporal autocorrelation   ',
                command=self.change_tacorrflag, height=1, width=20)
        else:
            self.tacorrB = tk.Button(self.availfeat_tab,\
                text=' - Temporal autocorrelation   ',\
                command=self.change_tacorrflag, height=1, width=20)
        self.tacorrB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.3)
        # ---------------------------------------------------------------------
        # ------- Button to remove/add Dyn. filtering tab ---------------------  
        if (self.DynamicFiltering_flag):
            self.dfB = tk.Button(self.availfeat_tab, text=' + Dynamic filtering   ',
            command=self.change_dfflag, height=1, width=20)
        else:
            self.dfB = tk.Button(self.availfeat_tab,\
                text=' - Dynamic filtering   ',\
                command=self.change_dfflag, height=1, width=20)
        self.dfB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.4)
        # ---------------------------------------------------------------------
        # --------------- Button to remove/add spatial acorr tab --------------
        if (self.SpatialAcorr_flag):
            self.sacorrB = tk.Button(self.availfeat_tab,
                text=' + Spatial autocorrelogram   ',
                command=self.change_sacorrflag, height=1, width=20)
        else:
            self.sacorrB = tk.Button(self.availfeat_tab,\
                text=' - Spatial autocorrelogram   ',\
                command=self.change_sacorrflag, height=1, width=20)
        self.sacorrB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.5)
        # ---------------------------------------------------------------------
        # ------------- Button to remove/add windowed analysis ----------------
        if (self.WindowedAnalysis_flag):
            self.waB = tk.Button(self.availfeat_tab,
                text=' + Windowed analysis   ',
                command=self.change_waflag, height=1, width=20)
        else:
            self.waB = tk.Button(self.availfeat_tab,\
                text=' - Windowed analysis   ',\
                command=self.change_waflag, height=1, width=20)
        self.waB.place(in_=self.availfeat_tab, anchor='c', relx=0.5, rely=0.6)
        # ---------------------------------------------------------------------
        # ------------------------- 'Apply' button ----------------------------
        self.applyB = tk.Button(self.availfeat_tab, text=' Apply ',
            command=self.apply_settings, height=1, width=20)
        self.applyB.place(in_=self.availfeat_tab, anchor="c", relx=.5, rely=.85)
        # ---------------------------------------------------------------------

















        # -------------------- Theme tab --------------------------------------
        # add 'themes' tab 
        self.themestab = tk.Frame(self.cfg_nbook,width=430,height=540)
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
                               command=self.about_info, font=self.myfont)

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
