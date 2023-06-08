import tkinter as tk
from tkinter import ttk

class LoadBar:  # class

    def Loading(self):
        main_window = tk.Tk()
        main_window.title("Loading files")
        #progressbar = ttk.Progressbar(mode="indeterminate")
        progressbar = ttk.Progressbar(main_window)
        progressbar.place(x=30, y=60, width=200)
        main_window.geometry("300x200")
        progressbar.start(100)
        main_window.mainloop()