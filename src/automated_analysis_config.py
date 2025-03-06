import tkinter as tk
import tkinter.ttk as ttk
import os
import datetime
from pathlib import Path

def build_config(main):

    """
    Here we extend the main-object (Cilialyzer) with the menu to configure
    the analysis pipeline
    """

    style = ttk.Style()
    # Configuring the default TLabelframe style
    style.configure("TLabelframe", background="gray90", padding=10)
    style.configure("TLabelframe.Label")

    main.autoLF = ttk.LabelFrame(main.autotab,
        text=" Configure analysis pipeline ", height=300, width=500, relief='ridge', labelanchor='n')
    main.autoLF.place(in_=main.autotab, anchor="c", relx=0.5, rely=0.5)

    def select_root_directory():
        # let the user choose a directory:
        main.toolbar.PIL_ImgSeq.choose_directory(automated=1)
        # choose_directory writes the chosen directory to file previous_directory.dat
        # goal: find all subdirectories
        # get first the path of the chosen directory:
        f = open('config/previous_directory.dat', 'r')
        path = f.read()
        f.close()

        # update the label indicating which root directory is set for the
        # automated analysis pipeline:
        #main.auto_path_str.set(path)

        contents = os.listdir(path) # returns all directories and files in path

        # contents holds relative paths. Add the base path to content[i]:
        basepath = path

        """
        for i in range(len(contents)):
            contents[i] = os.path.join(basepath, contents[i])

        # goal: dirlist holds the list of all directories within 'base path' directory
        dirlist = []
        for item in contents:
            if os.path.isdir(item):
                dirlist.append(item)

        print('----- test : dirlist ----- ')
        print(dirlist)
        print('---------------------------')
        """

    # Add button 'Select directory'
    main.auto_dirB = tk.Button(main.autotab, text=' Select directory ',
        command=select_root_directory, height=1, width=25)
    main.auto_dirB.place(in_=main.autotab, anchor="c", relx=.5, rely=.05)

    # Print path of selected directory:
    #main.auto_path_str = tk.StringVar()
    text_howto = """With the button above (Select directory), you can select a parent directory. The analysis pipeline assumes that this directory contains at least one subdirectory, and it will search for all subdirectories, which will then be analyzed sequentially. Currently, the automated pipeline can only handle image sequences."""
    main.auto_pathL = tk.Text(main.autotab, wrap="word",
        bg='gray90' ,width=65, height=5, font=("TkDefaultFont", 10) )
    main.auto_pathL.insert(1.0, text_howto)
    #main.auto_pathL.tag_configure("spacing", spacing1=5)
    #main.auto_pathL.tag_add("spacing", "2.0", "end")
    main.auto_pathL.place(in_=main.autotab,anchor='c',relx=0.5, rely=0.17)

    # add checkbutton for the image stabilization
    main.img_stab_autoflag = tk.IntVar()
    main.img_stab_autoflag.set(1)
    main.img_stab_checkB = tk.Checkbutton(main.autoLF, text=" Image stabilization ",
        variable=main.img_stab_autoflag, font=("TkDefaultFont", 10))
    main.img_stab_checkB.place(in_=main.autoLF, anchor='w', relx=0.05, rely=0.1)

    # add checkbutton for CBF analysis
    main.cbf_autoflag = tk.IntVar()
    main.cbf_autoflag.set(1)
    main.cbf_checkB = tk.Checkbutton(main.autoLF, text=" CBF analysis ",
        variable=main.cbf_autoflag, font=("TkDefaultFont", 10))
    main.cbf_checkB.place(in_=main.autoLF, anchor='w', relx=0.05, rely=0.25 )


    # add checkbutton for the active percentage and activity map  
    main.activity_autoflag = tk.IntVar()
    main.activity_autoflag.set(1)
    main.activity_autoflagB = tk.Checkbutton(main.autoLF, text=" Activity analysis ",
        variable=main.activity_autoflag, font=("TkDefaultFont", 10))
    main.activity_autoflagB.place(in_=main.autoLF, anchor='w', relx=0.05, rely=0.4)

    # ------------ add checkbutton for the frequency correlation --------------
    main.fcorr_autoflag = tk.IntVar()
    main.fcorr_autoflag.set(1)
    main.fcorr_autoflagB = tk.Checkbutton(main.autoLF, text=" Frequency correlation ",
        variable=main.fcorr_autoflag, font=("TkDefaultFont", 10))
    main.fcorr_autoflagB.place(in_=main.autoLF, anchor='w', relx=0.05, rely=0.55)
    # --------------------------------------------------------------------------

    # ----- add checkbutton for wavelength and spatial correlation length ------
    main.wl_autoflag = tk.IntVar()
    main.wl_autoflag.set(1)
    main.wl_checkB = tk.Checkbutton(main.autoLF, text=" Spatial analysis ",
        variable=main.wl_autoflag, font=("TkDefaultFont", 10))
    main.wl_checkB.place(in_=main.autoLF, anchor='w', relx=0.05, rely=0.7)


    # ------------- add checkbutton for local wavefield analysis --------------
    main.local_analysis_autoflag = tk.IntVar()
    main.local_analysis_autoflag.set(1)
    main.local_analysis_checkB = tk.Checkbutton(main.autoLF, text=" Local analysis ",
        variable=main.local_analysis_autoflag, font=("TkDefaultFont", 10))
    main.local_analysis_checkB.place(in_=main.autoLF, anchor='w', relx=0.05, rely=0.85)



    # Label 'Results will be saved to: '
    # main.auto_outputL = tk.Label(main.autotab, text=' Results will be saved to: ')
    # main.auto_outputL.place(in_=main.autotab, anchor='c',relx=0.3,rely=0.7)

    # create output_directory and write its path to file
    datetime_string = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dirname = 'Cilialyzer_output_' + datetime_string
    output_path = os.path.join(os.getcwd(), dirname)
    # write output_path to file:
    f = open('config/output_directory.dat', 'w')
    f.write(output_path)
    f.close()
    # Output will be written to current working directory
    main.output_directory = output_path
    # create the output directory, if it does not exist
    if not Path(main.output_directory).is_dir(): os.mkdir(main.output_directory)

    main.auto_outpath = tk.StringVar()
    main.auto_outpath.set(' Results will be saved to:  '+main.output_directory)
    main.auto_outpathL = tk.Label(main.autotab, textvariable=main.auto_outpath,
        font=("TkDefaultFont", 10))
    main.auto_outpathL.place(in_=main.autotab, anchor='c', relx=0.5, rely=0.7)

    main.videos_processed = tk.StringVar()
    main.videos_processed.set('Processing has not started yet')
    main.videos_processed_label =tk.Label(main.autotab,
        textvariable=main.videos_processed, font=("TkDefaultFont", 10))
    main.videos_processed_label.place(in_=main.autotab, anchor='c', relx=0.5,rely=0.9)

    main.main_window.update_idletasks()

