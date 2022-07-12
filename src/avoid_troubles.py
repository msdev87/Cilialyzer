
def stop_animation(player,roiplayer, ptrackplayer):

    if (player is not None):
        player.stop = 2

    if (roiplayer is not None):
        roiplayer.stop = 2

    if (ptrackplayer is not None):
        print('-------- TEST-----------')
        ptrackplayer.stop = 2

def clear_main(player, roiplayer, ptrackplayer):

    if (player is not None):
        player.frame.destroy()

    if (roiplayer is not None):
        roiplayer.frame.destroy()
        del roiplayer

    if (ptrackplayer is not None):
        ptrackplayer.frame.destroy()
        del ptrackplayer

