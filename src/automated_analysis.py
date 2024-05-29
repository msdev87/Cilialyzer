import os
import avoid_troubles
import tkinter as tk
from tkinter import ttk

import csv

def process(main):

    # select a directory
    # find all subdirectories
    # loop over all subdirectories (and their content)
    #   image stabilization
    #   mean subtraction
    #   powerspec
    #   activitymap
    #   write results to csv file

    # avoid troubles
    try:
        avoid_troubles.stop_animation(
            main.toolbar.player, main.toolbar.roiplayer, main.toolbar.ptrackplayer)
    except:
        pass

    # let the user choose a directory:
    main.toolbar.PIL_ImgSeq.choose_directory(automated=1)
    # choose_directory writes the chosen directory to file previous_directory.dat
    # goal: find all subdirectories
    # get first the path of the chosen directory:
    f=open('previous_directory.dat','r')
    path=f.read()
    f.close()

    contents = os.listdir(path) # listdir returns all directories and files in path

    # contents holds relative paths, we need to add the base path to content[i]:
    basepath = path
    for i in range(len(contents)):
        contents[i] = os.path.join(basepath, contents[i])

    #contents.sort()

    # goal: dirlist holds the list of all directories within 'base path' directory
    dirlist = []
    for item in contents:
        if os.path.isdir(item):
            dirlist.append(item)

    print('----- test : dirlist ----- ')
    print(dirlist)
    print('---------------------------')


    # ---------------- Before looping over all videos --------------------------
    # Create the a treeview widget in which we display the results

    # resultate auflisten in frontend
    # columns: directory, powerspectrum plot (file link), cbf, ..

    # Create a frame in which we place the treeview
    treeframe = tk.Frame(main.autotab, width=500,height=500)
    treeframe.place(in_=main.autotab,relx=0.3, rely=0.3)

    columns = ('path', 'cbf_mean')
    tree = ttk.Treeview(treeframe, columns=columns, show='headings')

    # specify the header, which will be displayed in the frontend
    tree.heading('path', text='Directory')
    tree.heading('cbf_mean', text='Average CBF [Hz]')

    tree_content = []
    tree.place()



    # -------------------- Loop over all directories -----------------------
    for dirname in dirlist:

        try:
            # delete displayed content in CBF tab: 
            self.powerspec.delete_content()
        except:
            pass
        try:
            # delete displayed content in activity tab:
            self.activitymap.delete_content()
        except:
            pass

        try:
            avoid_troubles.clear_main(main.player,main.roiplayer,main.ptrackplayer)
        except:
            pass

        main.toolbar.PIL_ImgSeq.directory = dirname
        # next line updates the label (displayed path to the new directory) 
        main.PIL_ImgSeq.dirname.set(dirname)
        # update the displayed filename of the first image
        files = os.listdir(dirname)
        main.toolbar.PIL_ImgSeq.fname.set(files[0])

        # write selected directory to file
        f = open('previous_directory.dat','w')
        f.write(dirname)
        f.close()

        # Load the image sequence!
        main.toolbar.PIL_ImgSeq.load_imgs(main.toolbar.nimgscombo, automated=1)
        # PIL_ImgSeq.sequence[i] holds the i-th frame (img format: 8 Bits, PIL)

        """
        main.toolbar.nbook.select(main.nbook.index(main.roitab))
        refresh = 0
        selectroi = 1
        main.roiplayer.__init__(main.roitab, main.PIL_ImgSeq.directory,refresh,
        main.PIL_ImgSeq.sequence, main.PIL_ImgSeq.seqlength, main.roi, selectroi)
        """

        """
        # make sure that the rotationangle is set to 0:
        main.roiplayer.rotationangle = 0.0

        # update label in statusbar:
        main.statusbar.update(main.PIL_ImgSeq)

        # print('roiplayer id in Toolbar: ',id(self.roiplayer))
        # main.roiplayer.animate()
        """

        # switch tab to cbf tab
        # main.nbook.select(main.nbook.index(main.cbftab))

        # Calculate powerspectrum
        main.powerspectrum.calc_powerspec(main.PIL_ImgSeq.sequence,
        main.toolbar.fpscombo.get(),main.pwspec1frame, main.minscale,
        main.maxscale, automated=1)

        main.powerspectrum.pwspecplot.save_plot(main.PIL_ImgSeq.directory)

        # switch back to automated analysis tab
        # main.nbook.select(main.nbook.index(main.autotab))

        new_values = (dirname, main.powerspectrum.pwspecplot.meancbf)
        tree_content.append(new_values)
        # tree.insert('', tk.END, values=new_values)

    # write the determined values to excel file

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(tree_content)

