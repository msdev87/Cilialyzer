import tkinter as tk

class Menubar:

    def __init__(self, parent):

        self.menubar = tk.Menu(parent) # creates the menubar of parent tk-window

        self.mfile = tk.Menu(self.menubar) # creates 'File' in menubar 

        # create submenus of File-menu: 
        self.mfile.add_command(label="Open sequence...", font=("Verdana",10))
        self.mfile.add_command(label="Open video...",font=("Verdana",10))

        # add menus to menubar: 
        self.menubar.add_cascade(label="File", menu=self.mfile)


if __name__ == "__main__":

    root = tk.Tk()
    root.geometry('300x200')

    mbar = Menubar(root)

    root.config(menu=mbar.menubar)
    root.mainloop()
