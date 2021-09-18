#
#  The python Minecraft Bot to rule them all.
#  Poggers!
#
#  (c) 2021 by Guido Appenzeller & Daniel Appenzeller
#

from javascript import require, On, Once, AsyncTask, once, off
import time

from inventory import *
from mine import *
from chat import *
from farming import *
from blocks import *
from build import *

#
# Main Bot Class
#
# Additional Methods are added via Mixin inheritance and are in the various modules
#

class PyBot(ChatBot, FarmBot):

  def __init__(self,account):
    # This is the Mineflayer bot
    self.bot = None
    self.account = account
    self.bossPlayer = self.account['master']
    self.callsign = self.account['user'][0:2]+":"

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
    self.init_ChatBot()
    time.sleep(1)

# Import credentials and server info, create the bot and log in
from account import account
pybot = PyBot(account.account)
print(f'Connected to server {account.account["host"]}.')

# Import list of known locations. Specific to the world.
if account.locations:
      pybot.myLocations = account.locations

#
# Init builds
#
init_build(pybot.bot)

time.sleep(1)

#
# Main Loop - We are driven by chat commands
#

# Report status
print(f'My boss is {pybot.bossPlayer}. Others can send commands to me with prefix "{pybot.callsign}"')
time.sleep(1)
pybot.sayStatus()
#pybot.printInventory()

@On(pybot.bot, 'chat')
def onChat(sender, message, this, *rest):
  pybot.handleChat(sender, message, this, *rest)

print(f'Ready.')

# The spawn event 
once(pybot.bot, 'login')
pybot.bot.chat('Bot '+pybot.bot.callsign+' joined.')

