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

    def contains_directory(directory):
        # this function checks whether the provided directory contains
        # at least one subdirectory
        # List all contents in the directory:
        contents = os.listdir(directory)
        # Iterate through contents and check if any is a directory
        for item in contents:
            if os.path.isdir(os.path.join(directory, item)):
                return True
        return False




    def get_parent_directory(path):
        parent_directory = os.path.dirname(path)
        return parent_directory


    def list_all_directories(base_path):
        all_dirs = []
        for root, dirs, files in os.walk(base_path):
            for dir in dirs:
                all_dirs.append(os.path.join(root, dir))
        return all_dirs

    f=open('previous_directory.dat','r')
    path=f.read()
    f.close()

    dir_list = list_all_directories(path)
    for i in range(len(dir_list)):
        dir_list[i] = os.path.join(get_parent_directory(dir_list[i]), dir_list[i])


    #contents = os.listdir(path) # listdir returns all directories and files in path

    # contents holds relative paths, we need to add the base path to content[i]:
    #basepath = path
    #for i in range(len(contents)):
    #    contents[i] = os.path.join(basepath, contents[i])



    # goal: dirlist holds the list of all directories within 'base path' directory
    #dirlist = []
    #for item in contents:
    #    if os.path.isdir(item):
    #        dirlist.append(item)

    dirlist = []
    # remove all directories which contain subdirectories:
    for directory in dir_list:
       if not contains_directory(directory): dirlist.append(directory)
    number_videos = len(dirlist)

    #print('----- test : dirlist ----- ')
    #print(dirlist)
    #print('---------------------------')


    # ---------------- Before looping over all videos --------------------------

    # Output table will be written to csv file
    # ouptut_table is a dictionary and will contain the data
    output_table = []
    # Initialize the dict with only the header/keys:
    header_keys = ["Filename","CBF","CBF_SD","CBF_min","CBF_max","FPS","Pixelsize","Wavelength", "Spatial correlation length"]
    header = dict.fromkeys(header_keys,None)

    output_table.append(header)

    counter = 0

    # read output_path from file
    f = open('output_directory.dat','r')
    output_directory = f.read()
    f.close()
    output_path = os.path.join(output_directory, 'Cilialyzer_output.csv')


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
        print(files)
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
        main.error_code = 0
        # ------------------------ Image stabilization -------------------------
        if (main.img_stab_autoflag.get()):
            try:
                # 1. Image stabilization
                main.image_stabilization(automated=1)
            except:
                main.error_code = 1
        # ----------------------------------------------------------------------

        # ----------------------- Calculate powerspectrum ----------------------
        if (main.cbf_autoflag.get()):
            try:
                avg_rel_dev=main.powerspectrum.calc_powerspec(main.PIL_ImgSeq.sequence,
                    main.toolbar.fpscombo.get(),main.pwspec1frame, main.minscale,
                    main.maxscale, automated=1)
                main.powerspectrum.pwspecplot.save_plot(main.PIL_ImgSeq.directory)
                main.error_code = round(avg_rel_dev)
            except:
                main.error_code = 1


        if (main.wl_autoflag.get()):
            try:
                # Dynamic filtering:
                main.dynfiltering(automated=1)
                # Determine the wavelength and the spatial correlation length
                min_correlation = main.dynseq.mscorr(float(main.toolbar.fpscombo.get()),
                    float(main.minscale.get()), float(main.maxscale.get()),
                    main.mscorrplotframe, main.mscorrprofileframe, float(main.toolbar.pixsizecombo.get()), automated=1, output_fname=main.PIL_ImgSeq.directory)

                if min_correlation > -0.03: error_code = 1
            except:
                main.error_code = 1

        # write output to list
        output_table.append({
            "Filename": dirname,
            "CBF": main.powerspectrum.pwspecplot.meancbf,
            "CBF_SD": main.powerspectrum.pwspecplot.cbfSD,
            "CBF_min": main.minscale.get(),
            "CBF_max": main.maxscale.get(),
            "FPS": main.toolbar.fpscombo.get(),
            "Pixelsize": main.toolbar.pixsizecombo.get(),
            "Wavelength": main.dynseq.wavelength if main.wl_autoflag.get() else '',
            "Spatial correlation length": main.dynseq.sclength if main.wl_autoflag.get() else '',
        })

        # write the determined values to excel file
        header = output_table[0].keys()


        with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        #with open('Cilialyzer_output' + '.csv', mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            # write the header
            writer.writeheader()
            # write the data rows
            writer.writerows(output_table)


        # increase counter
        counter += 1

        bla = ' Processed ' + str(counter) + ' of ' + str(number_videos) + ' videos '
        main.videos_processed.set(bla)

        main.main_window.update_idletasks()