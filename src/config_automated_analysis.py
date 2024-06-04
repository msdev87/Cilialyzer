import tkinter as tk
import tkinter.ttk as ttk
import os


def build_config(main):

    """
    Here we extend the main-object (cilialyzer) with the menu to configure
    the analysis pipeline
    """

    style = ttk.Style()
    # Configuring the default TLabelframe style
    style.configure("TLabelframe", background="lightgray", padding=10)
    style.configure("TLabelframe.Label", font=("Helvetica", 12))

    main.autoLF = ttk.LabelFrame(main.autotab,
        text="Configure analysis pipeline", heigh=300, width=700, relief='sunken', labelanchor='n')
    main.autoLF.place(in_=main.autotab, anchor="c", relx=0.5, rely=0.5)

    def select_root_directory():
        # let the user choose a directory:
        main.toolbar.PIL_ImgSeq.choose_directory(automated=1)
        # choose_directory writes the chosen directory to file previous_directory.dat
        # goal: find all subdirectories
        # get first the path of the chosen directory:
        f = open('previous_directory.dat', 'r')
        path = f.read()
        f.close()

        # update the label indicating which root directory is set for the
        # automated analysis pipeline:
        main.auto_path_str.set(path)

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
    main.auto_dirB.place(in_=main.autotab, anchor="c", relx=.5, rely=.07)

    # Print path of selected directory:
    main.auto_path_str = tk.StringVar()
    main.auto_path_str.set("")
    main.auto_pathL = tk.Label(main.autotab, textvariable=main.auto_path_str)
    main.auto_pathL.place(in_=main.autotab,anchor='c',relx=0.5, rely=0.14)

    # add checkbutton for the image stabilizaiton
    main.img_stab_autoflag = tk.IntVar()
    main.img_stab_checkB = ttk.Checkbutton(main.autoLF, text=" Image stabilization ", variable=main.img_stab_autoflag)
    main.img_stab_checkB.place(in_=main.autoLF, anchor='w', relx=0.1, rely=0.1)

    # add checkbutton for CBF analysis
    main.cbf_autoflag = tk.IntVar()
    main.cbf_checkB = ttk.Checkbutton(main.autoLF, text=" CBF analysis ", variable=main.cbf_autoflag)
    main.cbf_checkB.place(in_=main.autoLF, anchor='w', relx=0.1, rely=0.2)

    # add checkbutton for wavelength and spatial correlation length
    main.wl_autoflag = tk.IntVar()
    main.wl_checkB = ttk.Checkbutton(main.autoLF, text=" Wavelength & Correlation length", variable=main.wl_autoflag)
    main.wl_checkB.place(in_=main.autoLF, anchor='w', relx=0.1, rely=0.3)

    # Label 'Results will be saved to: '
    main.auto_outputL = tk.Label(main.autotab, text='Results will be saved to:')
    main.auto_outputL.place(in_=main.autotab, anchor='c',relx=0.5,rely=0.7)

    main.auto_outpath = tk.StringVar()
    main.auto_outpath.set("")
    main.auto_outpathL = tk.Label(main.autotab, textvariable=main.auto_outpath)
    main.auto_outpathL.place(in_=main.autotab, anchor='c', relx=0.5, rely=0.77)


