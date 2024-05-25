import os
import avoid_troubles

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
    main.toolbar.PIL_ImgSeq.choose_directory(manual=0)
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




        """
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
        """

        # Load the image sequence!
        main.toolbar.PIL_ImgSeq.load_imgs(main.toolbar.nimgscombo)
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

        # Calculate powerspectrum
        main.powerspectrum.calc_powerspec(main.roiplayer.roiseq,
        main.toolbar.fpscombo.get(),main.pwspec1frame, main.minscale,
        main.maxscale, manual=0)

        # resultate auflisten in frontend
        # columns: directory, powerspectrum plot (file link), cbf, ..











