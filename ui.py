#
#
#

import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk
import time
from javascript import require, On, Once, AsyncTask, once, off

from pybot import PyBot
from mine import MineBot
import botlib


#            10             20
# 0  Status  |   MicroMap   |    Inventory
# 
#10 --------------------------------------
#
#    Commands
#
#20 --------------------------------------
#
#    Log
#


class LogFrame(tk.Frame):

    max_log_lines = 200

    def __init__(self, master):

        tk.Frame.__init__(self, master)
        self.logObj = tk.scrolledtext.ScrolledText(width=60, height=20, font = ("TkFixedFont", 11))
        self.place = self.logObj.place
        self.logObj.configure(state ='disabled')

    def log(self,txt):
        self.logObj.configure(state ='normal')
        l = int(self.logObj.index('end').split('.')[0])
        if l > self.max_log_lines:
            self.logObj.delete("1.0",f'{l-self.max_log_lines}.0\n')
        self.logObj.insert(tk.END,f'{txt}\n')
        self.logObj.see(tk.END)
        self.logObj.configure(state ='disabled')

class PyBotWithUI(PyBot):

    inv_icons = {
        "Copper Ore":"🪨",
        "Lapis Lazuli":"✨",
        "Iron Ore":"🪨",
        "Gold Ore":"🪨",
        "Redstone Ore":"✨",
        "Diamonds":"💎",
        "Emeralds":"✨",
        "Wheat":"🌽",
        "Spruce Log":"🪵",
        "Spruce Sapling":"🌲",
        "Wheat Seeds":"🌿",
    }

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

    def uiInventory(self, items):
        for widget in self.invUI.winfo_children():
            widget.destroy()

        if len(items) > 0:
            for i in items:
                if i not in self.inv_icons:
                    ttk.Label(self.invUI, text = f'{items[i]:>3} x {i}', width=27, anchor="w").pack(side=tk.TOP, anchor="w", padx=5)
            ttk.Separator(self.invUI).pack(side=tk.TOP, padx=10, pady=5, fill="x")
            for i in items:
                if i in self.inv_icons:
                    label = self.inv_icons[i]
                    ttk.Label(self.invUI, text = f'{items[i]:>3} x {label}{i}', width=27, anchor="w").pack(side=tk.TOP, anchor="w", padx=5)
        else:
            tk.Label(self.invUI, text = f'    Inventory is Empty', width=27, anchor="w").pack(side=tk.TOP, anchor="w", padx=5)

    def uiStatus(self, health, food, oxygen):
        for widget in self.statusUI.winfo_children():
            widget.destroy()

        if oxygen > 18:
            oxygen = 20

        fg_c, bg_c = botlib.colorHelper(health,20)
        h = tk.Label(self.statusUI, text = f'{int(100*health/20):>3}%  Health', bg=bg_c, fg=fg_c, width=130)
        h.pack(side=tk.TOP, anchor="w", padx=5, pady=2 )

        fg_c, bg_c = botlib.colorHelper(food,20)
        f = tk.Label(self.statusUI, text = f'{int(100*food/20):>3}%  Food', bg=bg_c, fg=fg_c, width=130)
        f.pack(side=tk.TOP, anchor="w", padx=5, pady=2)

        fg_c, bg_c = botlib.colorHelper(oxygen,20)
        o = tk.Label(self.statusUI, text = f'{int(100*oxygen/20):>3}%  Oxygen', bg=bg_c, fg=fg_c, width=130)
        o.pack(side=tk.TOP, anchor="w", padx=5, pady=2)

    def uiEquipment(self,hand):
        for widget in self.equipUI.winfo_children():
            widget.destroy()

        tk.Label(self.equipUI, text = f'    Hand: {hand}').pack(side=tk.TOP, anchor="w", padx=5)

    def refreshInventory(self):
        inventory = self.bot.inventory.items()
        iList = {}
        if inventory != []:
            for i in inventory:
                iname = i.displayName
                if iname not in iList:
                    iList[iname] = 0
                iList[iname] += i.count
        self.uiInventory(iList)

    def refreshEquipment(self):
        i_type, item = self.itemInHand()
        self.uiEquipment(item)
        pass

    def refreshStatus(self):
        self.uiStatus(self.bot.health, self.bot.food, self.bot.oxygenLevel)
        pass

    def refreshActivity(self, txt):
        pass

    def refresherJob(self):
        while True:
            self.refreshEquipment()
            self.refreshStatus()
            self.refreshInventory()
            time.sleep(1)

    def initUI(self):
        win = tk.Tk()
        self.win = win
        win.title("PyBot - The friendly Minecraft Bot")
        win.geometry("680x800")
        win.resizable(False, False)

        #  0 --------------------------------------------------------------------------------

        self.statusUI = tk.LabelFrame(win, text='Status')
        self.statusUI.place(x=20, y=10, width=200, height=100)

        self.equipUI = tk.LabelFrame(win, text='Equipment')
        self.equipUI.place(x=20, y=120, width=200, height=100)

        self.activityUI = tk.LabelFrame(win, text='Activity')
        self.activityUI.place(x=20, y=230, width=200, height=180)

        # ---

        self.areaUI = tk.LabelFrame(win, text='Area')
        self.areaUI.place(x=240, y=10, width=200, height=400)

        # ---

        self.invUI = tk.LabelFrame(win,text='Inventory')
        self.invUI.place(x=460, y=10, width=200, height=400)

        # 10 --------------------------------------------------------------------------------

        ttk.Separator(win,orient='horizontal').place(x=0, y=430, width=680)

        #self.commandUI = tk.Frame(frame)
        #self.commandUI.place(relx=0, rely=0.7)

        #self.botCmd = tk.StringVar()
        #ttk.Label(self.commandUI, text="General Command:").grid(row=0, column=0,  columnspan = 5,  sticky="W")
        #self.cmdEntry = ttk.Entry(self.commandUI, width=20, textvariable=self.botCmd)
        #self.cmdEntry.grid(row=0, column=5, columnspan=20, sticky="EW")
        #ttk.Button(self.commandUI, text="Go!", command=self.do_command).grid(row=0, column=25, columnspan=5, sticky="W")

        # 20 --------------------------------------------------------------------------------
        
        ttk.Separator(win,orient='horizontal').place(x=0, y=550, width=680)

        ttk.Label(win, text="Activity Log").place( x=20, y=560)
        self.logFrame = LogFrame(win)
        self.logFrame.place(x=0, y=580, width=680, height=220)

    def mainloop(self):
        @AsyncTask(start=True)
        def doRefresher(task):
            self.refresherJob()

        self.win.mainloop()

    def __init__(self, account):
        super().__init__(account)
        self.initUI()

if __name__ == "__main__":
    # Run in test mode

    pybot = PyBotWithUI.__new__(PyBotWithUI)
    pybot.initUI()

    items = MineBot.miningEquipList

    pybot.uiInventory(items)

    a = 1
    while True:
        pybot.logFrame.log(f'{a} test and {a}*{a} = {a*a}')
        pybot.win.update_idletasks()
        pybot.win.update()
        a += 1
        time.sleep(.1)

    time.sleep(5)

    pybot.win.mainloop()