#
#
#

import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk, PhotoImage
import time
import datetime
from functools import partial
from javascript import require, On, Once, AsyncTask, once, off
Vec3     = require('vec3').Vec3

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

    # List means first is color (or None) second is icon

    block_icons = {
        "Air"           : None,
        "Cave Air"      : None,
        "Void Air"      : None,
        "Torch"         : None,
        "Wall Torch"    : None,
        "Redstone Torch": None,
        "Rail"          : [None,"#"],
        "Chest"         : ["brown","📦"],
        "Spruce Log"    : "brown",
        "Spruce Leaves" : "dark green",
        "Wheat Crops"   : ["green","🌾"],
        "Lava"          : "red",
        "Water"         : "blue", 
        "Bubble Column" : "blue",
        "Crafting Table": "brown",
    }

    inv_icons = {
        "Lapis Lazuli":"✨",
        "Raw Iron":"🪙",
        "Raw Copper":"🥉",
        "Raw Gold":"✨",
        "Redstone Dust":"🔴",
        "Diamond":"💎",
        "Emerald":"✨",
        "Wheat":"🌽",
        "Spruce Log":"🪵",
        "Spruce Sapling":"🌲",
        "Wheat Seeds":"🌿",
        "Coal":"🪨",
    }

    hand_icons = {
        "Wheat Seeds":"🌿",    
        "Stone Axe":"🪓",
        "Iron Axe":"🪓",
        "Diamond Axe":"🪓",
        "Stone Pickaxe":"⛏️",
        "Iron Pickaxe":"⛏️",
        "Diamond Pickaxe":"⛏️",
        "Cobblestone":"🪨",
        "Stone Brick":"🧱",
        "Bread":"🍞",
        "Stone Shovel":"⚒️",
        "Iron Shovel":"⚒️",
        "Diamond Shovel":"⚒️",
        "Stone Sword":"🗡️",
        "Iron Sword":"🗡️",
        "Diamond Sword":"🗡️",
    }

    button_mapping = [
        ["Come here"     , "come"],
        ["Follow me"     , "follow"],
        ["Farm Crops"    , "farm"],
        ["Chop Wood"     , "chop"],
        ["Deposit All"   , "deposit"],
        ["STOP!"         , "stop"],
        ["Mine Fast"     , "mine fast"],
        ["Mine 3x3"      , "mine 3x3"],
        ["Mine 5x5"      , "mine 5x5"],
        ["Mine Room"     , "mine room 5 5 3"],
        ["Mine Hall"     , "mine room 11 11 5"],
        ["Mine Shaft"    , "mineshaft 5 10"],
    ]

    def blockToIcon(self,name):
        if name in self.block_icons:
            return self.block_icons[name]
        else:
            return "grey"

    def blockToColor(self,name):
        if name in self.block_icons:
            l = self.block_icons[name]
            if type(l) == list:
                return l[0]
            else:
                return l
        else:
            return "grey"

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

    def uiInventory(self, items):
        for widget in self.invUI.winfo_children():
            widget.destroy()

        if len(items) > 0:
            for i in items:
                if i not in self.inv_icons:
                    ttk.Label(self.invUI, text = f'{items[i]:>3} x {i}', width=25, anchor="w").pack(side=tk.TOP, anchor="w", padx=5)
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
        h = tk.Label(self.statusUI, text = f'{int(100*health/20):>3}%  Health', background=bg_c, foreground=fg_c, width=130)
        h.pack(side=tk.TOP, anchor="w", padx=5, pady=1 )

        fg_c, bg_c = botlib.colorHelper(food,20)
        f = tk.Label(self.statusUI, text = f'{int(100*food/20):>3}%  Food', background=bg_c, foreground=fg_c,  width=130)
        f.pack(side=tk.TOP, anchor="w", padx=5, pady=1)

        fg_c, bg_c = botlib.colorHelper(oxygen,20)
        o = tk.Label(self.statusUI, text = f'{int(100*oxygen/20):>3}%  Oxygen', background=bg_c, foreground=fg_c,  width=130)
        o.pack(side=tk.TOP, anchor="w", padx=5, pady=1)

    def uiMap(self, blocks):
        self.map.delete("all")
        y = 0
        for x in range(0,13):
            for z in range(0,13):
                n = self.blockToIcon(blocks[y][x][z])
                if n:
                    if type(n) != list:
                        self.map.create_rectangle(10+x*14,10+z*14, 10+x*14+14, 10+z*14+14, fill=n)
                    else:
                        self.map.create_text(10+x*14+7,10+z*14+7, text=n[1])                        
        self.map.create_text(100, 100, text='🤖')

    def uiEquipment(self,item):
        if item in self.hand_icons:
            item = f'✋:  {self.hand_icons[item]} {item}'
        self.mainHandLabel.configure(text=item)

    def refreshMap(self):
        p = self.bot.entity.position

        blocks = []
        for x in range(0,13):
            new = []
            for z in range(0,13):
                new.append(0)
            blocks.append(new)

        for x in range(0,13):
            for z in range(0,13):
                v = Vec3(p.x+x-6,p.y+0.3,p.z+z-6)
                n = self.bot.blockAt(v).displayName
                blocks[x][z] = n

        self.uiMap([blocks])

    def refreshWorldStatus(self):

        t = self.bot.time.timeOfDay
        h = (int(t/1000)+6) % 24
        m = int( 60*(t % 1000)/1000)
        time_str = f'{h:02}:{m:02}'
        p = self.bot.entity.position
        pos_str = f'x: {int(p.x)}   y: {int(p.y)}   z: {int(p.z)}'
        if self.bot.time.isDay:
            self.timeLabel.configure(text=f'  Time: 🌞 {time_str}', background="light grey", foreground="black")
        else:
            self.timeLabel.configure(text=f'  Time: 🌙 {time_str}', background="dark blue", foreground="white")

        self.placeLabel.configure(text=f'  🧭  {pos_str}')

        self.connLabel.configure(text=f'  🌐 {self.account["host"]}   {self.bot.player.ping} ms')

        #tk.Label(self.equipUI, text = f'    Hand: {hand}').pack(side=tk.TOP, anchor="w", padx=5)

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
        o = self.bot.oxygenLevel
        if not o:
            o = 100
        self.uiStatus(self.bot.health, self.bot.food, o)
        pass

    def refreshActivity(self, txt):            
        if self.activity_major == False:
            status = f' ({self.activity_last_duration})'
        elif self.stopActivity:
            status = "🛑 Stop"
        else:
            status = str(datetime.timedelta(seconds=int(time.time()-self.activity_start)))
        self.activityTitleLabel.configure(text=f'{self.activity_name} {status}')

        if txt:
            if isinstance(txt,str):
                lines = [txt]
            elif isinstance(txt,list):
                lines = txt
            else:
                return
            while len(lines) < 6:
                lines.append("")
            for i in range(0,6):
                self.activityLine[i].configure(text=lines[i])

    def bossPlayer(self):
        return self.bossNameVar.get()

    def refresherJob(self):
        while True:
            self.refreshActivity(None)
            self.refreshWorldStatus()
            self.refreshStatus()
            self.refreshInventory()
            self.refreshMap()
            time.sleep(1)

    def do_command(self,cmd):
        if cmd != "stop":
            if self.activity_major == True:
                return False
        self.handleCommand(cmd, self.bossPlayer())

    def initUI(self):
        win = tk.Tk()
        self.win = win
        win.title("PyBot - The friendly Minecraft Bot")
        win.geometry("680x800")
        win.resizable(False, False)

        #  0 --------------------------------------------------------------------------------

        self.worldUI = ttk.LabelFrame(win, text='World Status')
        self.worldUI.place(x=20, y=10, width=200, height=100)

        self.timeLabel = tk.Label(self.worldUI, text = f'  🌞 00:00', width=130)
        self.timeLabel.pack(side=tk.TOP, anchor="w", padx=5)

        self.placeLabel = ttk.Label(self.worldUI, text = f'  Location TBD')
        self.placeLabel.pack(side=tk.TOP, anchor="w", padx=5, pady=2)

        self.connLabel = ttk.Label(self.worldUI, text = f'  Not Connected')
        self.connLabel.pack(side=tk.TOP, anchor="w", padx=5, pady=2)


        # -

        self.statusUI = ttk.LabelFrame(win, text='Player Status')
        self.statusUI.place(x=20, y=120, width=200, height=100)

        # -

        self.equipmentUI = ttk.LabelFrame(win, text='Equipment')
        self.equipmentUI.place(x=20, y=230, width=200, height=180)

        self.mainHandLabel = ttk.Label(self.equipmentUI, text = f'Main Hand: empty')
        self.mainHandLabel.pack(side=tk.TOP, anchor="w", padx=5)

        self.armorLine = [None,None,None,None,None,None]
        for i in range(0,4):
            self.armorLine[i] = ttk.Label(self.equipmentUI, text = f'')
            self.armorLine[i].pack(side=tk.TOP, anchor="w", padx=5)

        # -----------

        self.areaUI = tk.Frame(win)
        self.areaUI.place(x=240, y=10, width=200, height=200)

        #ttk.Label(self.areaUI, text='Area Map').pack(side=tk.TOP,anchor="w")

        self.map = tk.Canvas(self.areaUI, bg="#222", height=200, width=200)
        self.map.pack(side=tk.TOP)
        
        self.activityUI = ttk.LabelFrame(win, text='Activity')
        self.activityUI.place(x=240, y=230, width=200, height=180)

        self.activityTitleLabel = ttk.Label(self.activityUI, text = f'No Activity')
        self.activityTitleLabel.pack(side=tk.TOP, anchor="w", padx=5)

        self.activityLine = [None,None,None,None,None,None]
        for i in range(0,6):
            self.activityLine[i] = ttk.Label(self.activityUI, text = f'')
            self.activityLine[i].pack(side=tk.TOP, anchor="w", padx=5)

        # -----------

        self.invUI = ttk.LabelFrame(win,text='Inventory')
        self.invUI.place(x=460, y=10, width=200, height=400)

        # 10 --------------------------------------------------------------------------------

        ttk.Separator(win,orient='horizontal').place(x=0, y=430, width=680)

        self.commandUI = ttk.Frame(win)
        self.commandUI.place(x=10,y=440,width=660,height=100)

        self.commandButton = []
        but_i = 0
        for r in range(0,2):
            self.commandButton.append(None)
            self.commandButton[r] = []
            for c in range(0,6):
                self.commandUI.grid_columnconfigure(c, weight=1)
                self.commandButton[r].append(None)
                txt = self.button_mapping[but_i][0]
                f = partial(self.do_command,self.button_mapping[but_i][1])
                self.commandButton[r][c] = ttk.Button(self.commandUI, text=txt, command=f)
                self.commandButton[r][c].grid(row=r, column=c, sticky="we")
                but_i += 1

        self.cmdFrame = ttk.Frame(self.commandUI)
        self.cmdFrame.grid(row=10, column=0, columnspan=30, sticky="we")

        self.botCmd = tk.StringVar()
        ttk.Label(self.cmdFrame, text="Command:").grid(row=1, column=0, sticky="W")
        self.cmdEntry = ttk.Entry(self.cmdFrame, width=25, textvariable=self.botCmd)
        self.cmdEntry.grid(row=1, column=1, sticky="EW")
        ttk.Button(self.cmdFrame, text="Do it!", command=self.do_command).grid(row=1, column=2, sticky="W")

        self.bossNameVar = tk.StringVar()
        ttk.Label(self.cmdFrame, text="Boss:").grid(row=1, column=4,  sticky="W")
        self.bossName = ttk.Entry(self.cmdFrame, width=13, textvariable=self.bossNameVar)
        self.bossName.grid(row=1, column=5, sticky="EW")
        self.cmdFrame.grid_columnconfigure(3, weight=1)

        if hasattr(self,'account'):
            self.bossNameVar.set(self.account["master"])        

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
    print("UI Test - Part of PyBot, the friendly Minecraft Bot.")
    pybot = PyBotWithUI.__new__(PyBotWithUI)
    pybot.initUI()

    items = MineBot.miningEquipList

    pybot.uiInventory(items)

    pybot.uiStatus(20,15,10)

    blocks = [ [ ["grey"]*13 ] *13 ]
    blocks[0][6][5] = "Air"
    blocks[0][6][6] = "Air"
    blocks[0][6][7] = "Air"

    pybot.uiMap(blocks)
    pybot.uiEquipment("Stone Pickaxe")
    pybot.refreshActivity(["Test1", "Test2", "Test3"])

    a = 1
    while True:
        pybot.logFrame.log(f'{a} test and {a}*{a} = {a*a}')
        pybot.win.update_idletasks()
        pybot.win.update()
        a += 1
        time.sleep(.1)

    time.sleep(5)

    pybot.win.mainloop()