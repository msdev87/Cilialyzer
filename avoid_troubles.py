
def stop_animation(player,roiplayer, ptrackplayer):

    if (player is not None):
        player.stop = 2

    if (roiplayer is not None):
        roiplayer.stop = 2

    if (ptrackplayer is not None):
        ptrackplayer.stop = 2

    """
    try:
        # avoid crash 
        player.stop = 2
    except NameError:
        pass

    try:
        # avoid crash 
        roiplayer.stop = 2
    except NameError:
        pass

    try:
        ptrackplayer.stop = 2
    except NameError:
        pass
    """


def clear_main(player, roiplayer, ptrackplayer):
    
    if (player is not None):
        player.frame.destroy()

    if (roiplayer is not None):
        roiplayer.frame.destroy()
        del roiplayer

    if (ptrackplayer is not None):
        ptrackplayer.frame.destroy()
        del ptrackplayer

    
    
    """
    try:
     player.frame.destroy()
 except NameError:
     pass

 try:
     roiplayer.frame.destroy()
 except NameError:
     pass

 # delete 'roiplayer' object
 try:
     del roiplayer
 except NameError:
     pass

 # destroy particle tracking application
 try:
     ptrackplayer.frame.destroy()
     del ptrackplayer
 except NameError:
     pass

 # delete content of powerspec tab, before switching to animation     
 powerspectrum.tkframe.destroy()
    """






