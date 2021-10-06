#
# Functions for running away
#

from javascript import require, On, Once, AsyncTask, once, off
from botlib import *

import sys

class CombatBot:

    # Special flag that is set while healing up
    healMode = False

    def __init__(self):
        print('combat ', end='')
        self.healMode = True

    def healthCheck(self):
        h = 100*self.bot.health/20
        f = 100*self.bot.food/20

        self.refreshStatus()
        self.pdebug(f'    health: {h}%   food: {f}%',4)    

        if self.healMode:
            return True

        if h <= 50:
            # Health 50%. Panic and ninja-log.
            self.pdebug(f'PANIC: Health at {h}%. Quitting immediately.',1)
            self.bot.end()
            sys.exit()
        elif h <= 90:
            # Health 90%. Stop current activity.
            self.pdebug(f'WARNING: Health at {h}%. Stopping current activity.',1)
            self.stopActivity = True
            self.dangerType = "danger: health"

        # Check Food
        if f <= 80:
            self.pdebug(f'WARNING: Food at {f}%.',1)
        elif f <= 50:
            self.pdebug(f'WARNING: Food at {f}%. Stopping current activity.',1)
            self.stopActivity = True
            self.dangerType = "out of food"

        # Check if damage is from lava 

        # Check for air

    def healToFull(self):
        if self.bot.health == 20 and self.bot.food > 18:
            return
        self.healMode = True
        self.pdebug(f'Bot is injured or hungry, resting.',2)    
        h = 0
        while self.bot.health < 20 or self.bot.food < 18:
            if self.bot.health > h:
                self.pdebug(f'  health: {int(100*self.bot.health/20)}%   food: {int(100*self.bot.food/20)}%',3)
                h = self.bot.health
            if not self.eatFood():
                break
            time.sleep(2)
        self.pdebug(f'  health: {int(100*self.bot.health/20)}%   food: {int(100*self.bot.food/20)}%',3)
        self.pdebug(f'done.',2)
        self.healMode = False
