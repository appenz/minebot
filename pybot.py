#
#  The python Minecraft Bot to rule them all.
#  Poggers!
#
#  (c) 2021 by Guido Appenzeller & Daniel Appenzeller
#

import javascript
from javascript import require, On, Once, AsyncTask, once, off
import time
import asyncio
import argparse

from inventory import *
from movement import *
from farming import *
from mine import *
from build import *
from chat import *
from combat import *
from gather import *


#
# Main Bot Class
#
# Additional Methods are added via Mixin inheritance and are in the various modules
#

class PyBot(ChatBot, FarmBot, MineBot, GatherBot, BuildBot, CombatBot, MovementManager, InventoryManager):

    def __init__(self,account):
        # This is the Mineflayer bot
        self.bot = None
        self.account = account
        self.callsign = self.account['user'][0:2]+":"
        self.debug_lvl = 3
        self.lastException = None

        self.stopActivity = False
        self.dangerType = None

        self.speedMode = False # Move fast 

        mineflayer = require('mineflayer')

        bot = mineflayer.createBot(
            {
            'host'    : self.account['host'],
            'username': self.account['user'],
            'password': self.account['password'],
            'version': self.account['version'],
            'hideErrors': False,
            } )

        self.mcData   = require('minecraft-data')(bot.version)
        self.Block    = require('prismarine-block')(bot.version)
        self.Item     = require('prismarine-item')(bot.version)
        self.Vec3     = require('vec3').Vec3

        # Setup for the pathfinder plugin
        pathfinder = require('mineflayer-pathfinder')
        bot.loadPlugin(pathfinder.pathfinder)
        # Create a new movements class
        movements = pathfinder.Movements(bot, self.mcData)
        movements.blocksToAvoid.delete(self.mcData.blocksByName.wheat.id)
        bot.pathfinder.setMovements(movements)
        self.bot = bot

        # Initialize modules
        # Python makes this hard as __init__ of mixin classes is not called automatically

        print(f'pybot - a smart minecraft bot by Guido and Daniel Appenzeller.')

        classes = PyBot.mro()
        print('  modules: ', end='')
        for c in classes[1:]:
            c.__init__(self)
        print('.')

    # Debug levels: 
    #   0=serious error
    #   1=important info or warning 
    #   2=major actions or events
    #   3=each action, ~1/second
    #   4=spam me!
    #   5=everything

    def perror(self, message):
        print(f'*** error: {message}')

    def pexception(self, message,e):
        print(f'*** exception: {message}')
        if self.debug_lvl >= 4:
            print(e)
        else:
            with open("exception.debug", "w") as f:
                f.write("PyBit Minecraft Bot - Exception Dump")
                f.write(str(e))
                f.write("")
        self.lastException = e

    def pinfo(self, message):
        if self.debug_lvl > 0:
            print(message)

    def pdebug(self,message,lvl=4,end="\n"):
        if self.debug_lvl >= lvl:
            print(message,end=end)

    # Dummy functions, they get overriden by the GUI if we have it

    def mainloop(self):
        pass

    def refreshInventory(self):
        pass

    def refreshEquipment(self):
        pass

    def refreshStatus(self):
        pass

    def refreshActivity(self,txt):
        pass

    def bossPlayer(self):
        return self.account["master"]

#
# Run the bot. 
# Note that we can run with or without UI
#

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='python pybot.py')
    parser.add_argument('--nowindow', action='store_true', help='run in the background, i.e. without the Tk graphical UI')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='verbosity from 1-5. Use as -v, -vv, -vvv etc.')
    args = parser.parse_args()
    argsd = vars(args)

    # Import credentials and server info, create the bot and log in
    from account import account
    if  argsd["nowindow"]:
        pybot = PyBot(account.account)
    else:
        from ui import PyBotWithUI
        pybot = PyBotWithUI(account.account)
    pybot.pdebug(f'Connected to server {account.account["host"]}.',0)
    if 'verbose' in argsd:
        pybot.debug_lvl = argsd['verbose']

    # Import list of known locations. Specific to the world.
    if account.locations:
        pybot.myLocations = account.locations

    #
    # Main Loop - We are driven by chat commands
    #

    # Report status
    while not pybot.bot.health:
        time.sleep(1)

    @On(pybot.bot, 'chat')
    def onChat(sender, message, this, *rest):
        pybot.handleChat(sender, message, this, *rest)

    @On(pybot.bot, 'health')
    def onHealth(arg):
        pybot.healthCheck()

    @AsyncTask(start=True)
    def asyncInitialHeal(task):
        pybot.healToFull()

    if pybot.debug_lvl >= 4:
        pybot.printInventory()
    pybot.pdebug(f'Ready.',0)

    pybot.mainloop()
    # The spawn event
    #once(pybot.bot, 'login')
    #pybot.bot.chat('Bot '+pybot.bot.callsign+' joined.')
