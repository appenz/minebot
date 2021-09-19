#
# Farming
#

from javascript import require
Vec3       = require('vec3').Vec3
pathfinder = require('mineflayer-pathfinder')

from inventory import *
from blocks import *
import time

class FarmBot:

    farming_blocks = ["Wheat Crops"]
    farming_items  = ["Wheat"]
    farming_seeds  = ["Wheat Seeds"]

    farmingEquipList = {
      "Wheat Seeds":64,
      "Wheat":0
    }

    def safeMove(self,x,y,z,r):
        try:
            self.bot.pathfinder.setGoal(pathfinder.goals.GoalNear(x,y,z,r))
        except Exception:
            print("*** error: safeMove failed.")
            pass

    #
    # Main farming loop. To start, the bot should be next to a chest, or deposit wont work
    #
    # Main loop
    # - plant new crops
    # - harvest ripe crops
    # - deposit in chest

    def findHarvestable(self,center,r):

        bot_p = self.bot.entity.position

        # Check adjacent
        for dx,dz in [ [-1,0], [1,0], [0,-1], [0,1], [1,1], [1,-1], [-1,1], [-1,-1] ] :
            v = addVec3(bot_p,Vec3(dx,1,dz))
            b = self.bot.blockAt(v)
            #print(v,b.displayName)
            if b.displayName in self.farming_blocks and b.metadata == 7:
                return b

        # Look for harvestable
        for dx in range(-r,r+1):
            for dz in range(-r,r+1):
                v = addVec3(center,Vec3(dx,0,dz))
                b = self.bot.blockAt(v)
                #print(v,b.displayName)
                if b.displayName in self.farming_blocks and b.metadata == 7:
                    return b
        return None

    def findSoil(self,center,r):

        bot_p = self.bot.entity.position

        # Check adjacent
        for dx,dz in [ [-1,0], [1,0], [0,-1], [0,1], [1,1], [1,-1], [-1,1], [-1,-1] ] :
            v = addVec3(bot_p,Vec3(dx,0,dz))
            b = self.bot.blockAt(v)
            #print(v,b.displayName)
            if b.displayName == "Farmland":
                va = addVec3(bot_p,Vec3(dx,1,dz))
                ba = self.bot.blockAt(va)
                if ba and ba.type == 0:
                    return b

        # Look for harvestable
        for dx in range(-r,r+1):
            for dz in range(-r,r+1):
                v = addVec3(center,Vec3(dx,-1,dz))
                b = self.bot.blockAt(v)
                #print(v,b.displayName)
                if b.displayName == "Farmland":
                    va = addVec3(center,Vec3(dx,0,dz))
                    ba = self.bot.blockAt(va)
                    if ba and ba.type == 0:
                        return b
        return None

    def doFarming(self):

        max_range = 25

        up = Vec3(0, 1, 0)

        # Setup. Find out chest
        start_chest = findClosestBlock(self.bot,"Chest",2)
        if not start_chest:
            print("Please start farming near a chest.")
            return False
        start_pos = start_chest.position
        print("Farming started.")
        self.restockFromChest(self.farmingEquipList)

        while not self.stopActivity:

            long_break = 0

            # Harvest
            print("Harvesting:")
            for t in range(1,21):
                if self.stopActivity:
                    break
                b = self.findHarvestable(start_pos,max_range)
                if b and not self.stopActivity:
                    safeWalk(self.bot,b.position,0.5)
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
                for t in range(1,21):
                    if self.stopActivity:
                        break
                    b = self.findSoil(start_pos,max_range)
                    if b:
                        safeWalk(self.bot,addVec3(b.position,Vec3(0,1,0)),0.5)
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
            safeWalk(self.bot,start_pos)
            self.restockFromChest(self.farmingEquipList)
            time.sleep(0.5)
            self.eatFood()

            if not self.stopActivity:
                if long_break < 2:
                    time.sleep(0.5)
                else:
                    print('  nothing to do, taking a break.')
                    time.sleep(60)

        self.endActivity()
        return True
