import tkinter as tk

from bd import mydb
from gui import mygui

if __name__ == "__main__":
    # объект бд
    db = mydb("database.csv")

    root = tk.Tk()
    gui = mygui(root, db)

    root.mainloop()