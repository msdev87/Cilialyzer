import tkinter as tk
from tkinter import ttk
import os
import sys

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

        win_width = 600
        win_height = 450

        posx = int(0.5*sw - 0.5*win_width)
        posy = int(0.5*sh - 0.5*win_height)

        self.about_window.geometry("%dx%d+%d+%d" % (
            win_width, win_height, posx, posy))
        self.about_window.update()

        # text in about window
        self.textbox = tk.Text(self.about_window, height=5, width=400)

        text = """
        The Cilialyzer software is an easy-to-use, open source application
        mainly intended for the clinical  assessment of the effectivity of the
        mucociliary clearance mechanism inferred from recordings taken by
        high-speed video microscopy
        """

        self.textbox.pack()
        self.textbox.insert(tk.END, text)


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
            self.ptrackB['text'] = ' + Particle tracking   '
        else:
            self.ParticleTracking_flag = 1
            self.ptrackB['text'] = ' - Particle tracking   ' 


    def apply_settings(self):
        """
        Save current settings to file and restart the Cilialyer
        """
        self.write_flags()
        #self.parent.__init__()
        #self.cfg_win.destroy()
        #self.cfg_win.update()

        os.execl(sys.executable, os.path.abspath(__file__))


    def save_defaults(self):
        # save new defaults fps values
        self.fps_list[0] = int(self.entry_fps.get())

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
        self.pixelsize_list[0] = int(self.entry_pixelsize.get())

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

        # ---------- Button to remove/add particle tracking flag --------------
        if (self.ParticleTracking_flag):
            self.ptrackB = tk.Button(self.availfeat_tab, text=' - Particle tracking   ', command=self.change_ptrackflag, height=2, width=15)
        else:
            self.ptrackB = tk.Button(self.availfeat_tab,\
            text=' + Particle tracking   ', command=self.change_ptrackflag,
            height=1, width=15)
        self.ptrackB.place(in_=self.availfeat_tab, anchor='c', relx=.5,rely=.2)

        # 'Apply' button 
        self.applyB = tk.Button(self.availfeat_tab, text=' Apply ',
            command=self.apply_settings, height=1, width=15)
        self.applyB.place(in_=self.availfeat_tab, anchor="c", relx=.5, rely=.27)

        # ------------------------ Defaults tab ----------------------------
        # add Defaults tab
        self.defaults_tab = tk.Frame(self.cfg_win, width=430, height=540)
        self.cfg_nbook.add(self.defaults_tab, text=' Defaults ')

        # read fps_defaults.txt (if it exists)
        if (os.path.exists('fps_defaults.txt')):
            with open('fps_defaults.txt') as f:
                fps_defaults = f.readlines()
                fps_defaults = [line.rstrip() for line in fps_defaults]
                self.fps_list = fps_defaults
        else:
            self.fps_list = []

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

        fps_label=tk.Label(self.defaults_tab, text=" Default FPS :",
            anchor='e', font=("TkDefaultFont",10), width=22)
        fps_label.place(in_=self.defaults_tab, anchor="c", relx=.25, rely=.1)

        # add entry widget (to set default fps)
        self.entry_fps = tk.Entry(self.defaults_tab, width=10)
        self.entry_fps.place(in_=self.defaults_tab, anchor="c", relx=.6, rely=.1)
        # display current default
        self.entry_fps.insert(0, str(self.fps_list[0]))

        # ------------- add label and entry to set new pixelsize -------------- 

        pixelsize_label=tk.Label(self.defaults_tab,\
            text=" Default Pixelsize [nm] :", anchor='e', font=("TkDefaultFont",10), width=22)
        pixelsize_label.place(in_=self.defaults_tab, anchor="c", relx=.25, rely=.2)

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
        self.entry_pixelsize = tk.Entry(self.defaults_tab, width=10)
        self.entry_pixelsize.place(in_=self.defaults_tab, anchor="c", relx=.6, rely=.2)
        # display current default
        self.entry_pixelsize.insert(0, str(self.pixelsize_list[0]))


        # 'Save & Exit' button 
        self.save_defaultsB = tk.Button(self.defaults_tab, text=' Save & Exit ',
            command=self.save_defaults, height=1, width=15)
        self.save_defaultsB.place(in_=self.defaults_tab, anchor="c", relx=.5, rely=.7)



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

        self.mhelp.add_command(label='Documentation', command=self.open_doc)
        self.mhelp.add_command(label='Watch tutorial videos',
                               command=self.link_tutorials)
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
