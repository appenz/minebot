#
# Farming
#

from javascript import require
Vec3       = require('vec3').Vec3
pathfinder = require('mineflayer-pathfinder')

from inventory import *
from botlib import *
import time

class FarmBot:

    farming_blocks = ["Wheat Crops"]
    farming_items  = ["Wheat"]
    farming_seeds  = ["Wheat Seeds"]

    farmingEquipList = {
      "Wheat Seeds":64,
      "Wheat":0
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

        # Setup. Find the chest and restock
        start_chest = Chest(self)
        if not start_chest.block:
            self.perror('Please start farming near a chest.')
            return False
        start_pos = start_chest.block.position
        start_chest.restock(self.farmingEquipList)
        start_chest.close()

        # Main loop. Keep farming until told to stop.

        while not self.stopActivity:
            long_break = 0

            # Harvest
            self.pdebug(f'Harvesting.',2)
            for t in range(0,break_interval):
                if self.stopActivity:
                    break
                b = self.findHarvestable(max_range)
                if b and not self.stopActivity:
                    self.walkToBlock(b)
                    self.pdebug(f'  {b.displayName}  ({b.position.x}, {b.position.z}) ',3)
                    try:
                        self.bot.dig(b)
                    except Exception as e:
                        self.pexception("error while harvesting:",e)
                    #time.sleep(0.2)
                else:
                    self.pdebug('  no more harvestable crops',2)
                    long_break += 1
                    break

            # Plant
            print("Planting:")
            crop = self.wieldItemFromList(self.farming_seeds)
            if crop:
                for t in range(0,break_interval):
                    if self.stopActivity:
                        break
                    b = self.findSoil(start_pos,max_range)
                    if b:
                        self.walkOnBlock(b)
                        if not self.checkInHand(crop):
                            self.pdebug(f'Out of seeds of type {crop}.',2)
                            break
                        self.pdebug(f'  {crop} ({b.position.x}, {b.position.z})',3)
                        try:
                            self.bot.placeBlock(b,up)
                        except Exception as e:
                            self.pexception("error while planting:",e)
                    else:
                        self.pdebug('  no more empty soil',3)
                        long_break += 1
                        break
            else:
                self.pdebug('  no plantable seeds in inventory.',2)

            # Deposit
            self.walkTo(start_pos)
            start_chest.restock(self.farmingEquipList)
            start_chest.close()
            time.sleep(0.5)
            self.eatFood()

            if not self.stopActivity:
                if long_break < 2:
                    time.sleep(0.5)
                else:
                    self.pdebug('Nothing to do, taking a break.',2)
                    self.safeSleep(60)

        self.endActivity()
        return True
