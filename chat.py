#
# Misc chat functions
#

from javascript import require, On, Once, AsyncTask, once, off
pathfinder = require('mineflayer-pathfinder')

from farming import *

class ChatBot:

	def __init__(self):
		self.stopActivity = True

	def sayStatus(self):
		print('  level : ',self.bot.experience.level)
		print('  health: ',int(100*self.bot.health/20),"%")
		print('  food  : ',int(100*self.bot.food/20),"%")

	def sayHello(self):
	    self.bot.chat('hello to you too!')

	def handleChat(self,sender, message, this, *rest):

	  # check if order is incorrect to fix a bug we are seeing between Guido and Daniel
	  if type(sender) != type(""):
	    # reorder
	    t = sender
	    sender = message
	    message =  this
	    this = t

	  message = message.strip()

	  if message.startswith(self.callsign):
	    print(f'{sender} messaged me "{message}"')
	    message = message[2:]
	  elif sender != self.bossPlayer:
	    return

	  # "stop" should stop all activities

	  if 'stop' in message:
	    self.stopActivity = True
	  else:
	    self.stopActivity = False

	  # come - try to get to the player
	  if 'come' in message or 'go' in message:
	    if message == 'come':
	      player = self.bot.players[sender]
	    elif 'go to' in message:
	      player = self.bot.players[message[6:]]
	    else:
	      self.bot.chat("No Clear Target")
	    target = player.entity
	    if not target:
	      self.bot.chat("I don't see you!")
	      return
	    pos = target.position
	    self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 1))

	  if 'follow' in message:
	    if message == 'follow':
	      player = self.bot.players[sender]
	    elif len(message) > 6:
	      player = self.bot.players[message[7:]]
	    else:
	      self.bot.chat("No Clear Target")
	    target = player.entity
	    if not target:
	      self.bot.chat("I don't see you!")
	      return
	    @AsyncTask(start=True)
	    def follow(task):
	      while self.stopActivity != True:
	        self.bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(player.entity, 1))
	        time.sleep(2)

	  if message.startswith('moveto'):
	    args = message[6:].split()
	    if len(args) != 1:
	      self.bot.chat('Need name of location to move to.')
	      return
	    @AsyncTask(start=True)
	    def doMoveTo(task):
	      gotoLocation(self.bot,args[0])

	  if message.startswith('transfer to'):
	    args = message[11:].split()
	    if len(args) != 1:
	      self.bot.chat('Need name of target chest.')
	      return
	    @AsyncTask(start=True)
	    def doTransfer(task):
	      transferToChest(self.bot,args[0])      

	  if message == 'mine3':
	    @AsyncTask(start=True)
	    def doStripMine(task):
	      stripMine(self.bot,3,3)

	  if message == 'tunnel3':
	    @AsyncTask(start=True)
	    def doStripMine(task):
	      stripMine(self.bot,3,3)

	  if message == 'mine':
	    @AsyncTask(start=True)
	    def doStripMine(task):
	      stripMine(self.bot,1,5)

	  if message == 'mine5':
	    @AsyncTask(start=True)
	    def doStripMine(task):
	      stripMine(self.bot,5,5)

	  if message == 'tunnel5':
	    @AsyncTask(start=True)
	    def doStripMine(task):
	      stripMine(self.bot,5,5,0)

	  if message.startswith('minebox'):
	    args = [int(s) for s in message[7:].split() if s.isdigit()]
	    if len(args) != 3:
	      self.bot.chat('Minebox needs three arguments: rx, ry and height.')
	      return
	    if args[0] < 1:
	      self.bot.chat(f'Box half lenght in x direction must be at least 1, is {args[0]}')
	      return
	    if args[1] < 1:
	      self.bot.chat(f'Box half lenght in y direction must be at least 1, is {args[1]}')
	      return
	    if args[2] < 2:
	      self.bot.chat(f'Box height must be at least 2, is {args[2]}')
	      return
	    @AsyncTask(start=True)
	    def doAreaMine(task):
	      areaMine(self.bot,args[0],args[1],args[2])

	  if message.startswith('mineshaft'):
	    args = [int(s) for s in message[9:].split() if s.isdigit()]
	    if len(args) != 2:
	      self.bot.chat('Minebox needs three arguments: radius and max depth.')
	      return
	    if args[0] < 1:
	      self.bot.chat(f'Box radius must be at least 1, is {args[0]}')
	      return
	    if args[1] < 1:
	      self.bot.chat(f'Max depth must be at least 1, is {args[1]}')
	      return
	    @AsyncTask(start=True)
	    def doShaftMine(task):
	      shaftMine(self.bot,args[0],args[1])


	  if message == 'farm':
	    @AsyncTask(start=True)
	    def doFarmingTask(task):
	      self.doFarming()
	 
	  if message == 'analyze':
	    @AsyncTask(start=True)
	    def doAnalyzeBuildTask(task):
	      analyzeBuild(self.bot)

	  if message.startswith('build'):
	    args = message[5:].split()
	    if len(args) != 1:
	      self.bot.chat('Build needs name of blueprint to build.')
	      return
	    @AsyncTask(start=True)
	    def doBuildTask(task):
	      doBuild(self.bot,args[0])

	  if message == 'deposit':
	    depositToChest(self.bot)

	  if message == 'status':
	    sayStatus(self.bot)
	  if message == 'hello':
	    sayHello(self.bot)
	  if message =='inventory':
	    printInventory(self.bot)
	  if message == 'eat':
	    eatFood(self.bot)
	  if message == 'sleep':
	    bed = findClosestBlock(self.bot,"White Bed",xz_radius=3,y_radius=1)
	    if not bed:
	      self.bot.chat('cant find a White Bed nearby (I only use those)')
	      print("*** error, can't find a White Bed nearby")
	    else:
	      #try:
	      self.bot.sleep(bed)
	      self.bot.chat('good night!')
	      #except Exception:
	      self.bot.chat('sleeping failed - is it at night?')
	      print("*** error, can't find a White Bed nearby")
	  if message == 'wake':
	    self.bot.wake()
	    self.bot.chat('i woke up!')
	  if message == 'yeet':
	    # exit the game
	    off(self.bot, 'chat', onChat)