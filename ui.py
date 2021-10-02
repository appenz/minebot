#
#
#

import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk
import time
from javascript import require, On, Once, AsyncTask, once, off

from pybot import PyBot

class LogFrame(tk.Frame):

    def __init__(self, master):

        tk.Frame.__init__(self, master)
        self.logObj = tk.scrolledtext.ScrolledText(width=80, height=20, font = ("TkFixedFont", 11))
        self.grid = self.logObj.grid
        self.logObj.configure(state ='disabled')

    def log(self,txt):
        self.logObj.configure(state ='normal')
        self.logObj.insert(tk.INSERT,f'{txt}\n')
        self.logObj.configure(state ='disabled')

class PyBotWithUI(PyBot):

    def perror(self, message):
        self.logFrame.log(f'*** error: {message}')

    def pexception(self, message,e):
        self.logFrame.log(f'*** exception: {message}')
        if self.debug_lvl >= 4:
            self.logFrame.log(str(e))
        else:
            with open("exception.debug", "w") as f:
                f.write("PyBit Minecraft Bot - Exception Dump")
                f.write(str(e))
                f.write("")
        self.lastException = e

    def pinfo(self, message):
        if self.debug_lvl > 0:
            self.logFrame.log(message)

    def pdebug(self,message,lvl=4,end=""):
        if self.debug_lvl >= lvl:
            self.logFrame.log(message)

    def do_command(self):
        print(self.botCmd)

    def initUI(self):
        win = tk.Tk()
        self.win = win
        win.title("PyBot - The friendly Minecraft Bot")
        #win.eval('tk::PlaceWindow . center')

        frame = ttk.Frame(win, padding="3 3 12 12")
        self.frame = frame
        self.frame.grid(column=0, row=0, sticky="NSEW")
        win.columnconfigure(0, weight=1)
        win.rowconfigure(0, weight=1)

        self.botCmd = tk.StringVar()
        ttk.Label(frame, text="Command:").grid(column=0, row=1, sticky="W")
        self.cmdEntry = ttk.Entry(frame, width=20, textvariable=self.botCmd)
        self.cmdEntry.grid(column=1, row=1, sticky="EW")
        ttk.Button(frame, text="Go!", command=self.do_command).grid(column=2, row=1, sticky="W")
        
        for child in frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        #root.bind("<Return>", calculate)

        ttk.Label(frame, text="Activity Log").grid(column=0, row=2, sticky="SW")
        self.logFrame = LogFrame(self.frame)
        self.logFrame.grid(column=0, row=2, columnspan=3, sticky="EW")

    def mainloop(self):
        self.win.mainloop()

    def __init__(self, account):
        super().__init__(account)
        self.initUI()
