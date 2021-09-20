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

        # Setup. Find out chest
        start_chest = self.findClosestBlock("Chest",2)
        if not start_chest:
            print("Please start farming near a chest.")
            return False
        start_pos = start_chest.position
        print("Farming started.")
        self.restockFromChest(self.farmingEquipList)

        # Main loop. Keep farming until told to stop.

        while not self.stopActivity:
            long_break = 0

            # Harvest
            print("Harvesting:")
            for t in range(0,break_interval):
                if self.stopActivity:
                    break
                b = self.findHarvestable(max_range)
                if b and not self.stopActivity:
                    self.walkToBlock(b)
                    print(f'  {b.displayName}  ({b.position.x}, {b.position.z}) ')
                    try:
                        self.bot.dig(b)
                    except Exception as e:
                        print("error while harvesting:",e)
                    #time.sleep(0.2)
                else:
                    print('  no more harvestable crops')
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
                            print(f'Out of seeds of type {crop}.')
                            break
                        print(f'  {crop} ({b.position.x}, {b.position.z})')
                        try:
                            self.bot.placeBlock(b,up)
                        except Exception as e:
                            print("error while planting:",e)
                    else:
                        print('  no more empty soil')
                        long_break += 1
                        break
            else:
                print('  no plantable seeds in inventory.')

            # Deposit
            self.walkTo(start_pos)
            self.restockFromChest(self.farmingEquipList)
            time.sleep(0.5)
            self.eatFood()

            if not self.stopActivity:
                if long_break < 2:
                    time.sleep(0.5)
                else:
                    print('  nothing to do, taking a break.')
                    self.safeSleep(60)

        self.endActivity()
        return True
