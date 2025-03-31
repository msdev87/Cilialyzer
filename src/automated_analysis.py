import os
import avoid_troubles
import csv
import matplotlib.pyplot as plt
import time
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

    f=open('config/previous_directory.dat', 'r')
    path=f.read()
    f.close()

    dir_list = list_all_directories(path)
    for i in range(len(dir_list)):
        dir_list[i] = os.path.join(get_parent_directory(dir_list[i]), dir_list[i])

    dirlist = []
    # remove all directories which contain subdirectories:
    for directory in dir_list:
       if not contains_directory(directory): dirlist.append(directory)
    number_videos = len(dirlist)

    # ---------------- Before looping over all videos --------------------------
    # Output table will be written to csv file
    # ouptut_table is a dictionary and will contain the output data
    output_table = []
    # Initialize the dict with only the header/keys:
    header_keys = ["Filename", "CBF", "CBF_SD", "CBF_min", "CBF_max",\
                   "Active percentage", "Frequency correlation", "FPS", "Pixelsize",\
                   "Wavelength", "1D Spatial correlation length", "2D Spatial correlation length", \
                   "Overall CBP elongation", "Mean wave speed", "SD wave speed",\
                   "Wave disorder", "Analysed windows", "Mean wavelength",\
                   "SD wavelength", "Mean CBP elongation", "Error code"]
    header = dict.fromkeys(header_keys, None)

    output_table.append(header)

    counter = 0

    # read output_path from file
    f = open('config/output_directory.dat', 'r')
    output_directory = f.read()
    f.close()
    output_path = os.path.join(output_directory, 'Cilialyzer_output.csv')

    bla = ' Processing data, please wait....'
    main.videos_processed.set(bla)

    print('-------------------------------------------------------------------')
    print('dirlist', dirlist)
    print('-------------------------------------------------------------------')

    # --------------------------------------------------------------------------
    # ---------------------- Loop over all directories -------------------------
    # --------------------------------------------------------------------------
    for dirname in dirlist:

        print('processing: ', dirname)

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
        try:
            files = os.listdir(dirname)
        except:
            files = ''

        if len(files) < 10:
            continue # continue to next video (rest of loop gets skipped)

        main.toolbar.PIL_ImgSeq.fname.set(files[0])

        # write selected directory to file
        f = open('config/previous_directory.dat', 'w')
        f.write(dirname)
        f.close()

        start = time.time()
        # Load the image sequence!
        main.toolbar.PIL_ImgSeq.load_imgs(main.toolbar.nimgscombo, automated=1)
        # PIL_ImgSeq.sequence[i] holds the i-th frame (img format: 8 Bits, PIL)

        #print('time to load images: ', time.time()-start)

        main.roiplayer.roiseq = main.toolbar.PIL_ImgSeq.sequence

        # if the number of loaded images is less than 10 skip folder:
        if len(main.roiplayer.roiseq) < 10:
            continue # continue to next video

        main.error_code = 0

        start = time.time()
        # ------------------------ Image stabilization -------------------------
        if (main.img_stab_autoflag.get()):
            try:
                main.image_stabilization(automated=1)
            except:
                main.error_code = 1
        # ----------------------------------------------------------------------
        #print('image stabilization done after: ', time.time()-start)
        start = time.time()
        # ----------------------- Calculate powerspectrum ----------------------
        if (main.cbf_autoflag.get()):
            try:
                error_code=main.powerspectrum.calc_powerspec(main.PIL_ImgSeq.sequence,
                    main.toolbar.fpscombo.get(),main.pwspec1frame, main.minscale,
                    main.maxscale, automated=1)
                main.powerspectrum.pwspecplot.save_plot(main.PIL_ImgSeq.directory)
                main.error_code = round(error_code)
            except:
                main.error_code = 1
                print('error1')
        # ----------------- calculate activity map -----------------------------
        #print('powerspec: ', time.time()-start)

        start = time.time()
        if main.activity_autoflag.get() and not main.error_code:
            try:
                main.activity_map.calc_activitymap(main.mapframe,
                    main.roiplayer.roiseq, float(main.toolbar.fpscombo.get()), \
                    float(main.minscale.get()), float(main.maxscale.get()), \
                    main.powerspectrum, float(main.toolbar.pixsizecombo.get()), automated=1)
                main.activity_map.save_plot(main.PIL_ImgSeq.directory)
                if float(main.activity_map.active_percentage.get()) < 20:
                    main.error_code = 1
                    print('error2')
            except:
                main.error_code=1
                print('error3')
        # ----------------------------------------------------------------------
        #print('activity map done: ', time.time() - start)
        start = time.time()
        # --------------------- Frequency correlation --------------------------
        if main.fcorr_autoflag.get() and not main.error_code:
            try:
                main.activity_map.frequency_correlogram(main.fcorrframe,
                    float(main.toolbar.pixsizecombo.get()))
            except:
                main.error_code = 1
        # ----------------------------------------------------------------------
        #print('freq corr done: ', time.time()-start)
        start = time.time()
        if main.wl_autoflag.get() and not main.error_code:
            try:
                # Dynamic filtering:
                main.dynfiltering(automated=1)
                # Determine the wavelength and the spatial correlation length
                min_correlation = main.dynseq.mscorr(float(main.toolbar.fpscombo.get()),
                    float(main.minscale.get()), float(main.maxscale.get()),
                    main.mscorrplotframe, main.mscorrprofileframe, float(main.toolbar.pixsizecombo.get()),
                    main.activity_map.validity_mask ,automated=1, output_fname=main.PIL_ImgSeq.directory)
                if min_correlation > -0.03: main.error_code = 1
            except:
                main.error_code = 1
        #print('Dynamic filtering done: ', time.time()-start)
        start = time.time()
        # ---------------------- windowed analysis -----------------------------
        if main.local_analysis_autoflag.get() and not main.error_code:
            try:
                main.winanalysis()
            except:
                main.error_code = 1
        # print('windowed analysis done: ', time.time()-start)

        # append output to dictionary
        output_table.append({
            "Filename": dirname,
            "CBF": main.powerspectrum.pwspecplot.meancbf,
            "CBF_SD": main.powerspectrum.pwspecplot.cbfSD,
            "CBF_min": main.minscale.get(),
            "CBF_max": main.maxscale.get(),
            "Active percentage": main.activity_map.active_percentage.get(),
            "Frequency correlation": main.activity_map.freq_clength,
            "FPS": main.toolbar.fpscombo.get(),
            "Pixelsize": main.toolbar.pixsizecombo.get(),
            "Wavelength": main.dynseq.wavelength if main.wl_autoflag.get() else '',
            "1D Spatial correlation length": main.dynseq.sclength if main.wl_autoflag.get() else '',
            "2D Spatial correlation length": main.dynseq.bidirectional_corrlength if main.wl_autoflag.get() else '',
            "Overall CBP elongation": main.dynseq.cbp_elongation if main.wl_autoflag.get() else '',
            "Mean wave speed": main.winresults.mean_wspeed.get() if main.local_analysis_autoflag.get() else '',
            "SD wave speed": main.winresults.sd_wspeed.get() if main.local_analysis_autoflag.get() else '',
            "Wave disorder": main.winresults.wdisorder.get() if main.local_analysis_autoflag.get() else '',
            "Analysed windows": main.winresults.nwindows.get() if main.local_analysis_autoflag.get() else '',
            "Mean wavelength": main.winresults.avg_wlength.get() if main.local_analysis_autoflag.get() else '',
            "SD wavelength": main.winresults.sd_wlength.get() if main.local_analysis_autoflag.get() else '',
            "Mean CBP elongation": main.winresults.avg_elongation.get() if main.local_analysis_autoflag.get() else '',
            "Error code": main.error_code
        })

        # write the determined values to excel file
        header = output_table[0].keys()

        with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
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

        plt.close('all')

        # print('-------------- end of loop -----------')