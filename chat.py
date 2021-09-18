#
# Misc chat functions
#

import time
import datetime
import botlib

from javascript import require, On, Once, AsyncTask, once, off
pathfinder = require('mineflayer-pathfinder')

class ChatBot:

	def init_ChatBot(self):
		self.stopActivity = True
		self.activity_start = 0
		self.activity_name = "None"
		self.activity_major = False

		# Command : [function, name, is-this-a-major-activity]

		self.commandList = {
#			"analyze": 	[self.analyzeBuild, 	"Analyze building", False],
#			"deposit": 	[self.depositToChest, 	"Deposit all to Chest", False],
			"farm": 	[self.doFarming, 		"Farming", True],
#			"eatFood": 	[self.eatFood, 			"Eat Something", False],
			"hello": 	[self.sayHello, 		"Say Hello", False],
#			"inventory":[self.printInventory, 	"List Inventory", False],
			"stop":  	[self.stopThis, 		"Stop all activities", False],
#			"status":  	[self.sayStatus, 		"Report Status", False],
		}

	def sayStatus(self):
		print('  level : ',self.bot.experience.level)
		print('  health: ',int(100*self.bot.health/20),"%")
		print('  food  : ',int(100*self.bot.food/20),"%")

	def sayHello(self):
	    self.bot.chat('hello to you too!')

	def startActivity(self, name):
		t_str = botlib.myTime()
		print(60*'-')
		print(f'   {name:20} ({t_str})')
		print(60*'-')
		self.activity_start = time.time()
		self.activity_name = name
		self.stopActivity = False
		self.activity_major = True

	def endActivity(self):
		if self.activity_major:
			t_str = botlib.myTime()
			d_str = str(datetime.timedelta(seconds=int(time.time()-self.activity_start)))
			print(f'Activity {self.activity_name} ended at {t_str} (duration: {d_str})')
			self.bot.clearControlStates('sneak', False)
		self.bot.stopActivity = True
		self.activity_major = False

	def stopThis(self):
		self.stopActivity = True

	def handleChat(self,sender, message, this, *rest):

		# check if order is incorrect to fix a bug we are seeing between Guido and Daniel
		if type(sender) != type(""):
			# reorder
			t = sender
			sender = message
			message =  this
			this = t

		message = message.strip()

		# Is this for me, or for someone else?
		if message.startswith(self.callsign):
			print(f'{sender} messaged me "{message}"')
			message = message[len(self.callsign):]
		elif sender != self.bossPlayer:
			return

		cmd = message.split()[0]
		args = message.split()[1:]

		if cmd in self.commandList:
			c = self.commandList[cmd]
			call_function = c[0]
			if c[2]:
				# Major activity
				if self.activity_major:
					print(f'*** error: major activity in progress, stop it first {self.activity_name}.')
					return
				self.startActivity(c[1])
				@AsyncTask(start=True)
				def asyncActivity(task):
					call_function()
			else:
				call_function()
			return

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

		if message.startswith('build'):
			args = message[5:].split()
			if len(args) != 1:
			  self.bot.chat('Build needs name of blueprint to build.')
			  return
			@AsyncTask(start=True)
			def doBuildTask(task):
			  doBuild(self.bot,args[0])


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