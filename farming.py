#
# Farming
#

from javascript import require
Vec3       = require('vec3').Vec3
pathfinder = require('mineflayer-pathfinder')

from inventory import *
from botlib import *
from workarea import *
import time

class FarmBot:

    farming_blocks = ["Wheat Crops"]
    farming_items  = ["Wheat"]
    farming_seeds  = ["Wheat Seeds"]

    farmingEquipList = {
      "Wheat Seeds":64,
      "Wheat":0,
      "Bread":5,
    }

    def __init__(self):
        print('farming ', end='')

    #
    # Main farming loop. To start, the bot should be next to a chest, or deposit wont work
    #
    # Main loop
    # - plant new crops
    # - harvest ripe crops
    # - deposit in chest

    def findHarvestable(self, r):
        return self.findClosestBlock(self.farming_blocks, r, y_radius=1, metadata=7 )

    def findSoil(self,center,r):
        return self.findClosestBlock("Farmland", r, y_radius=1, spaceabove=True )

    def doFarming(self):

        break_interval = 32
        max_range = 25
        up = Vec3(0, 1, 0)

        area = workArea(self,1,1,1,notorch=True)
        if not area.valid:
            self.endActivity()
            return False
        area.restock(self.farmingEquipList)

        # Main loop. Keep farming until told to stop.

        while not self.stopActivity:
            long_break = 0

            # Harvest
            self.pdebug(f'Harvesting.',2)
            for t in range(0,break_interval):
                if self.stopActivity:
                    break
                self.refreshActivity(['Harvesting',' ❓ searching for crops'])
                b = self.findHarvestable(max_range)
                if b and not self.stopActivity:
                    self.refreshActivity(['Harvesting',f' ✅ {b.displayName}'])
                    self.walkToBlock(b)
                    self.pdebug(f'  {b.displayName}  ({b.position.x}, {b.position.z}) ',3)
                    try:
                        self.bot.dig(b)
                    except Exception as e:
                        self.pexception("error while harvesting:",e)
                    #time.sleep(0.2)
                else:
                    self.pdebug('  no more harvestable crops',2)
                    self.refreshActivity(['Harvesting',' ❌ no more harvestable crops.'])
                    long_break += 1
                    break

            # Plant
            self.pdebug(f'Planting.',2)
            crop = self.wieldItemFromList(self.farming_seeds)
            if crop:
                for t in range(0,break_interval):
                    if self.stopActivity:
                        break
                    self.refreshActivity(['Planting',' ❓ searching for soil'])
                    b = self.findSoil(area.origin,max_range)
                    self.refreshActivity(['Planting',f' ✅ empty soil'])
                    if b:
                        self.walkOnBlock(b)
                        if not self.checkInHand(crop):
                            self.refreshActivity(['Planting',f' ❌ no seeds for {crop}'])
                            self.pdebug(f'Out of seeds of type {crop}.',2)
                            break
                        self.pdebug(f'  {crop} ({b.position.x}, {b.position.z})',3)
                        try:
                            self.bot.placeBlock(b,up)
                        except Exception as e:
                            self.pexception("error while planting:",e)
                    else:
                        self.refreshActivity(['Planting',f' ❌ no more empty soil'])
                        self.pdebug('  no more empty soil',3)
                        long_break += 1
                        break
            else:
                self.refreshActivity(['Planting',f' ❌ no more seeds'])
                self.pdebug('  no plantable seeds in inventory.',2)

            # Deposit
            area.walkToStart()
            area.restock(self.farmingEquipList)

            if not self.stopActivity:
                if long_break < 2:
                    time.sleep(0.5)
                else:
                    self.refreshActivity(['Taking a break.'])
                    self.pdebug('Nothing to do, taking a break.',2)
                    self.safeSleep(30)

        self.endActivity()
        return True
