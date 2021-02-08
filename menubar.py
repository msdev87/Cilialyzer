import tkinter as tk

class Menubar:

    def __init__(self, parent):

        myfont = ("Verdana",10,)

        self.menubar = tk.Menu(parent,bg='gray30',fg='gray95') # creates the menubar of parent tk-window

        # create 'File'-tab in menubar
        self.mfile = tk.Menu(self.menubar)
        # create submenus of File-tab: 
        self.mfile.add_command(label="Open sequence...", font=myfont)
        self.mfile.add_command(label="Open video...",font=myfont)


        # create 'Appearance'-tab 
        self.mapp = tk.Menu(self.menubar)
        # create submenus
        self.mapp.add_command(label="Configure...",font=myfont)


        # create 'Help'-tab 

        # create 'Exit'-tab

        # add menus to menubar: 
        self.menubar.add_cascade(label="File",font=myfont,menu=self.mfile)
        self.menubar.add_cascade(label="Appearance",font=myfont,menu=self.mapp)

if __name__ == "__main__":

    root = tk.Tk()
    root.geometry('300x200')

    mbar = Menubar(root)

    root.config(menu=mbar.menubar)
    root.mainloop()
