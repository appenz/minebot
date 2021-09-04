#
#  The python Minecraft Bot to rule them all.
#  Poggers!
#
#  (c) 2021 by Guido Appenzeller & Daniel Appenzeller
#

from javascript import require, On, Once, AsyncTask, once, off
import time

from account import account
from equipment import *
from mine import *
from chat import *
from farming import *
from blocks import *

# Setup and log into server

mineflayer = require('mineflayer')

bot = mineflayer.createBot(
	{   'host'	  : '34.83.26.64', 
		'username': account.account_user, 
		'password': account.account_password, 
		'hideErrors': False, 
    'version': '1.16.5'
	}
)

bot.mcData   = require('minecraft-data')(bot.version)
bot.Block    = require('prismarine-block')(bot.version)
bot.Vec3     = require('vec3').Vec3
bot.callsign = account.account_user[0]

# Setup for the pathfinder plugin

pathfinder = require('mineflayer-pathfinder')
bot.loadPlugin(pathfinder.pathfinder)
# Create a new movements class
movements = pathfinder.Movements(bot, bot.mcData)
movements.blocksToAvoid.delete(bot.mcData.blocksByName.wheat.id)
bot.pathfinder.setMovements(movements)
# How far to be fromt the goal
RANGE_GOAL = 1

time.sleep(2)

#
# Main Loop - We are driven by chat commands
#

bot.stopActivity = True

@On(bot, 'chat')
def onChat(sender, message, this, *rest):
  # check if order is incorrect to fix a bug we are seeing between Guido and Daniel
  if type(sender) != type(""):
    # reorder
    t = sender
    sender = message
    message =  this
    this = t

  if message[0] == bot.callsign and message[1] == '.':
    print(f'{sender} messaged me "{message}"')
    message = message[2:]
  elif sender == account.account_master:
    pass
  else:
    return

  # "stop" should stop all activities

  if 'stop' in message:
    bot.stopActivity = True
  else:
    bot.stopActivity = False

  # come - try to get to the player
  if 'come' in message or 'go' in message:
    if message == 'come':
      player = bot.players[sender]
    elif 'go to' in message:
      player = bot.players[message[6:]]
    else:
      bot.chat("No Clear Target")
    target = player.entity
    if not target:
      bot.chat("I don't see you!")
      return
    pos = target.position
    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, RANGE_GOAL))

  if 'follow' in message:
    if message == 'follow':
      player = bot.players[sender]
    elif len(message) > 6:
      player = bot.players[message[7:]]
    else:
      bot.chat("No Clear Target")
    target = player.entity
    if not target:
      bot.chat("I don't see you!")
      return
    @AsyncTask(start=True)
    def follow(task):
      while bot.stopActivity != True:
        bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(player.entity, RANGE_GOAL))
        time.sleep(2)

  if message == 'mine':
    @AsyncTask(start=True)
    def doStripMine(task):
      stripMine(bot)

  if message == 'mine5':
    @AsyncTask(start=True)
    def doStripMine(task):
      stripMine(bot,5,5)

  if message.startswith('minebox'):
    args = [int(s) for s in message[7:].split() if s.isdigit()]
    if len(args) != 3:
      bot.chat('Minebox needs three arguments: rx, ry and height.')
      return
    if args[0] < 1:
      bot.chat(f'Box half lenght in x direction must be at least 1, is {args[0]}')
      return
    if args[1] < 1:
      bot.chat(f'Box half lenght in y direction must be at least 1, is {args[1]}')
      return
    if args[2] < 2:
      bot.chat(f'Box height must be at least 2, is {args[2]}')
      return
    @AsyncTask(start=True)
    def doAreaMine(task):
      areaMine(bot,args[0],args[1],args[2])

  if message.startswith('mineshaft'):
    args = [int(s) for s in message[9:].split() if s.isdigit()]
    if len(args) != 2:
      bot.chat('Minebox needs three arguments: radius and max depth.')
      return
    if args[0] < 1:
      bot.chat(f'Box radius must be at least 1, is {args[0]}')
      return
    if args[1] < 1:
      bot.chat(f'Max depth must be at least 1, is {args[1]}')
      return
    @AsyncTask(start=True)
    def doShaftMine(task):
      shaftMine(bot,args[0],args[1])


  if message == 'farm':
    @AsyncTask(start=True)
    def doFarmingTask(task):
      doFarming(bot)
 
  if message == 'deposit':
    depositToChest(bot)

  if message == 'status':
    sayStatus(bot)
  if message == 'hello':
    sayHello(bot)
  if message =='inventory':
    printInventory(bot)
  if message == 'eat':
    eatFood(bot)
  if message == 'sleep':
    bed = findClosestBlock(bot,"White Bed",xz_radius=3,y_radius=1)
    if not bed:
      bot.chat('cant find a White Bed nearby (I only use those)')
      print("*** error, can't find a White Bed nearby")
    else:
      #try:
      bot.sleep(bed)
      bot.chat('good night!')
      #except Exception:
      bot.chat('sleeping failed - is it at night?')
      print("*** error, can't find a White Bed nearby")
  if message == 'wake':
    bot.wake()
    bot.chat('i woke up!')
  if message == 'yeet':
    # exit the game
    off(bot, 'chat', onChat)


def commandSend():
  command = ''
  command = input() 
  return command

@AsyncTask(start=True)
def commandTask(task):
  while True:
    onChat('Command Line', commandSend(), 'this is a placeholder for the real thing')

# Report status
print('Connected, call sign: "'+bot.callsign+'"')
time.sleep(1)
sayStatus(bot)
printInventory(bot)

# The spawn event 
once(bot, 'login')
bot.chat('Bot '+bot.callsign+' joined.')

