#
# Misc chat functions
#

import time
import datetime
import botlib

from javascript import require, On, Once, AsyncTask, once, off
pathfinder = require('mineflayer-pathfinder')

class ChatBot:

    def __init__(self):
        print('chat ', end='')
        self.stopActivity = True
        self.activity_start = 0
        self.activity_name = "None"
        self.activity_major = False

        # Command : [function, name, major activity flag, min_arguments]

        self.commandList = {
#               "analyze":      [self.analyzeBuild,             "Analyze building",     False, 0],
                "deposit":      [self.depositToChest,           "Deposit all in chest", False, 0],
                "farm":         [self.doFarming,                "Farming",              True , 0],
                "eatFood":      [self.eatFood,                  "Eat Something",        False, 0],
                "hello":        [self.sayHello,                 "Say Hello",            False, 0],
                "inventory":    [self.printInventory,           "List Inventory",       False, 0],
                "mine":         [self.doMining,                 "Mine for resources",   True,  1],
                "sleep":        [self.sleepInBed,               "Sleep in a bed",       False, 0],
                "stop":         [self.stopThis,                 "Stop all activities",  False, 0],
                "status":       [self.sayStatus,                "Report status",        False, 0],
                "wake":         [self.wakeUp,                   "Stop sleeping",        False, 0],
                "yeet":         [self.exitGame,                 "Exit the game",        False, 0],
        }

    def chat(self,txt):
        self.bot.chat(txt)
        print('  chat: ',txt)

    def sayStatus(self):
        print('  level : ',self.bot.experience.level)
        print('  health: ',int(100*self.bot.health/20),"%")
        print('  food  : ',int(100*self.bot.food/20),"%")

    def sayHello(self):
        self.chat('hello to you too!')

    def startActivity(self, name):
        t_str = botlib.myTime()
        print(60*'-')
        print(f'  {name:47} {t_str}')
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

    def safeSleep(self,t):
        for i in range(0,t):
            time.sleep(1)
            if self.stopActivity:
                return False
        return True

    def stopThis(self):
        self.stopActivity = True

    def sleepInBed(self):
        bed = self.findClosestBlock("White Bed",xz_radius=3,y_radius=1)
        if not bed:
            self.chat('cant find a White Bed nearby (I only use those)')
            print("*** error, can't find a White Bed nearby")
        else:
            self.bot.sleep(bed)
            self.chat('good night!')

    def wakeUp(self):
            self.bot.wake()
            self.chat('i woke up!')

    def exitGame(self):
            # exit the game
            off(self.bot, 'chat', onChat)

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

        # Handle standard commands

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
                    if c[3] > 0:
                        call_function(args)
                    else:
                        call_function()
            else:
                if c[3] > 0:
                    call_function(args)
                else:
                    call_function()
            return

        # Legacy commands, need to clean up

        # come - try to get to the player
        if 'come' in message or 'go' in message:
            if message == 'come':
                player = self.bot.players[sender]
            elif 'go to' in message:
                player = self.bot.players[message[6:]]
            else:
                self.chat("No Clear Target")
            target = player.entity
            if not target:
                self.chat("I don't see you!")
                return
            pos = target.position
            self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 1))

        if 'follow' in message:
            if message == 'follow':
                player = self.bot.players[sender]
            elif len(message) > 6:
                player = self.bot.players[message[7:]]
            else:
                self.chat("No Clear Target")
            target = player.entity
            if not target:
                self.chat("I don't see you!")
                return
            @AsyncTask(start=True)
            def follow(task):
                while self.stopActivity != True:
                    self.bot.pathfinder.setGoal(pathfinder.goals.GoalFollow(player.entity, 1))
                    time.sleep(2)

        if message.startswith('moveto'):
            args = message[6:].split()
            if len(args) != 1:
                self.chat('Need name of location to move to.')
                return
            @AsyncTask(start=True)
            def doMoveTo(task):
                gotoLocation(self.bot,args[0])

        if message.startswith('transfer to'):
            args = message[11:].split()
            if len(args) != 1:
                self.chat('Need name of target chest.')
                return
            @AsyncTask(start=True)
            def doTransfer(task):
                transferToChest(self.bot,args[0])

        if message.startswith('minebox'):
            args = [int(s) for s in message[7:].split() if s.isdigit()]
            if len(args) != 3:
                self.chat('Minebox needs three arguments: rx, ry and height.')
                return
            if args[0] < 1:
                self.chat(f'Box half lenght in x direction must be at least 1, is {args[0]}')
                return
            if args[1] < 1:
                self.chat(f'Box half lenght in y direction must be at least 1, is {args[1]}')
                return
            if args[2] < 2:
                self.chat(f'Box height must be at least 2, is {args[2]}')
                return
            @AsyncTask(start=True)
            def doAreaMine(task):
                areaMine(self.bot,args[0],args[1],args[2])

        if message.startswith('mineshaft'):
            args = [int(s) for s in message[9:].split() if s.isdigit()]
            if len(args) != 2:
                self.chat('Minebox needs three arguments: radius and max depth.')
                return
            if args[0] < 1:
                self.chat(f'Box radius must be at least 1, is {args[0]}')
                return
            if args[1] < 1:
                self.chat(f'Max depth must be at least 1, is {args[1]}')
                return
            @AsyncTask(start=True)
            def doShaftMine(task):
                shaftMine(self.bot,args[0],args[1])

        if message.startswith('build'):
            args = message[5:].split()
            if len(args) != 1:
                self.chat('Build needs name of blueprint to build.')
                return
            @AsyncTask(start=True)
            def doBuildTask(task):
                doBuild(self.bot,args[0])

