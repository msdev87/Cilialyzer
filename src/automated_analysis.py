import os
import avoid_troubles
import tkinter as tk
from tkinter import ttk
import csv
import datetime

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

    """ 
    this has been moved to 'config_automated_analysis.py
    
    # let the user choose a directory:
    main.toolbar.PIL_ImgSeq.choose_directory(automated=1)
    # choose_directory writes the chosen directory to file previous_directory.dat
    # goal: find all subdirectories
    # get first the path of the chosen directory:
    """

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
    # treeframe = tk.Frame(main.autotab, width=500,height=500)
    # treeframe.place(in_=main.autotab,relx=0.3, rely=0.3)

    # columns = ('path', 'cbf_mean')
    # tree = ttk.Treeview(treeframe, columns=columns, show='headings')

    # specify the header, which will be displayed in the frontend
    # tree.heading('path', text='Directory')
    # tree.heading('cbf_mean', text='Average CBF [Hz]')

    # tree_content = []
    # tree.place()





    # Output table will be written to csv file
    # ouptut_table is a dictionary and will contain the data
    output_table = []
    # Initialize the dict with only the header/keys:
    header_keys = ["Filename","CBF","FPS","Pixelsize","Wavelength", "Spatial correlation length"]
    header = dict.fromkeys(header_keys,None)

    output_table.append(header)

    counter = 0
    # --------------------------------------------------------------------------
    # ---------------------- Loop over all directories -------------------------
    # --------------------------------------------------------------------------
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

        main.roiplayer.roiseq = main.toolbar.PIL_ImgSeq.sequence

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

        # ------------------------ Image stabilization -------------------------
        if (main.img_stab_autoflag.get()):
            # 1. Image stabilization
            main.image_stabilization(automated=1)
        # ----------------------------------------------------------------------



        # ----------------------- Calculate powerspectrum ----------------------
        if (main.cbf_autoflag.get()):
            main.powerspectrum.calc_powerspec(main.PIL_ImgSeq.sequence,
                main.toolbar.fpscombo.get(),main.pwspec1frame, main.minscale,
                main.maxscale, automated=1)

            main.powerspectrum.pwspecplot.save_plot(main.PIL_ImgSeq.directory)

        if (main.wl_autoflag):
            # Dynamic filtering:
            main.dynfiltering(automated=1)
            # Determine the wavelength and the spatial correlation length
            main.dynseq.mscorr(float(main.toolbar.fpscombo.get()),
                float(main.minscale.get()), float(main.maxscale.get()),
                main.mscorrplotframe, main.mscorrprofileframe, float(main.toolbar.pixsizecombo.get()))

        # write output to list
        output_table.append({
            "Filename": dirname,
            "CBF": main.powerspectrum.pwspecplot.meancbf,
            "FPS": main.toolbar.fpscombo.get(),
            "Pixelsize": main.toolbar.pixsizecombo.get(),
            "Wavelength": main.dynseq.wavelength if main.wl_autoflag else '',
            "Spatial correlation length": main.dynseq.sclength if main.wl_autoflag else ''
        })


        # also write error code to output file
        #TODO


        # write the determined values to excel file
        header = output_table[0].keys()
        with open('Cilialyzer_output_'+datetime.date.today().strftime("%Y_%m_%d")+'.csv', mode='w', newline='', encoding='utf-8') as csvfile:
        #with open('Cilialyzer_output' + '.csv', mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            # write the header
            writer.writeheader()
            # write the data rows
            writer.writerows(output_table)

        # increase counter
        counter += 1