#
# Gathering Functionality for the bot
#

from inventory import *
from botlib import *
from workarea import *

class BoundingBox:

    # Computes the bounding block of a set of connected blocks
    # For example, give it part of a tree trunk, get back the bounding box of all of the tree's wood

    def __init__(self, pybot, block):
        self.pybot = pybot
        b_type = block.displayName
        x_max = block.position.x
        x_min = block.position.x
        y_max = block.position.y
        y_min = block.position.y
        z_max = block.position.z
        z_min = block.position.z
    
        found = True

        while found:
            found = False
            for x in range(x_min-1, x_max+2):
                for y in range(y_min-1, y_max+2):
                    for z in range(z_min-1, z_max+2):
                        b = pybot.blockAt(x,y,z)
                        if b.displayName == b_type:
                            if x_min <=x and x_max >= x and y_min <= y and y_max >= y and z_min <= z and z_max >= z:
                                continue
                            x_min = x if x < x_min else x_min
                            x_max = x if x > x_max else x_max
                            y_min = y if y < y_min else y_min
                            y_max = y if y > y_max else y_max
                            z_min = z if z < z_min else z_min
                            z_max = z if z > z_max else z_max
                            found = True
        self.pybot.pdebug(f'    bounding box: {x_min}:{x_max}  {y_min}:{y_max}  {z_min}:{z_max}',4)
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.z_min = z_min
        self.z_max = z_max

    def dx(self):
        return self.x_max-self.x_min+1

    def dy(self):
        return self.y_max-self.y_min+1

    def dz(self):
        return self.z_max-self.z_min+1



class GatherBot:

    chopEquipList = {
      "Stone Axe":5,
      "Spruce Log":0,
      "Spruce Sapling":0,
      "Stick":0,
    }

    def __init__(self):
        print('gather ', end='')

    def chopBlock(self,x,y,z):
        v = Vec3(x,y,z)
        b = self.bot.blockAt(v)

        if b.displayName != "Air":
            self.pdebug(f'  chop   ({x},{y},{z}) {b.displayName}',3)
            self.bot.dig(b)
            if self.bot.blockAt(v).displayName == "Air":
                return 1
            else:
                return 0
        return 1

    def chop(self,x,y,z,height):
        self.wieldItem("Stone Axe")
        for h in range(0,height):
            self.chopBlock(x,y+h,z)

    def chopBigTree(self):
        self.pdebug(f'Looking for tree block...',3)
        self.refreshActivity([' ❓ searching: giant spruce'])
        b0 = self.findClosestBlock("Spruce Log",xz_radius=25,y_radius=1)
        if self.stopActivity:
            return False
        if not b0:
            self.perror('Cant find any tree to chop down nearby')
            return False
        self.pdebug(f'  found at {b0.position.x},{b0.position.z}',3)
        box = BoundingBox(self,b0)

        if box.dx() != 2 or box.dz() != 2 or box.dy() < 5:
            self.perror(f'Tree has wrong dimensions {box.dx()} x {box.dy()} x {box.dz()}')
            return False
        
        self.refreshActivity([f'🌲 Tree at {b0.position.x},{b0.position.z}',f'  height: {box.dy()}'])
        self.pdebug(f'Found big tree of height {box.dy()}',2)

        self.walkToBlock(box.x_min-1, box.y_min, box.z_min-1)

        x0 = box.x_min
        y  = box.y_min
        z0 = box.z_min

        self.walkToBlock(x0-1, y, z0-1)
        self.chop(x0-1, y, z0-1, 3)
        self.walkToBlock(x0-1, y, z0-1)

        while True:
            self.chop(x0,y+1, z0,3)
            self.walkOnBlock(x0,y,z0)
            self.refreshActivity([f'🌲 Tree at {b0.position.x},{b0.position.z}',f'  height: {box.dy()}',f'  y: {y-box.y_min}','  ⬆️ heading up'])
            time.sleep(0.5)
            self.chop(x0+1,y+2, z0,3)
            self.walkOnBlock(x0+1,y+1,z0)
            self.refreshActivity([f'🌲 Tree at {b0.position.x},{b0.position.z}',f'  height: {box.dy()}',f'  y: {y-box.y_min+1}','  ⬆️ heading up'])
            time.sleep(0.5)
            self.chop(x0+1,y+3, z0+1,3)
            self.walkOnBlock(x0+1,y+2,z0+1)
            self.refreshActivity([f'🌲 Tree at {b0.position.x},{b0.position.z}',f'  height: {box.dy()}',f'  y: {y-box.y_min+2}','  ⬆️ heading up'])
            time.sleep(0.5)
            self.chop(x0,y+4, z0+1,3)
            self.walkOnBlock(x0,y+3,z0+1)
            self.refreshActivity([f'🌲 Tree at {b0.position.x},{b0.position.z}',f'  height: {box.dy()}',f'  y: {y-box.y_min+3}','  ⬆️ heading up'])
            time.sleep(0.5)
            if y+8 >= box.y_max:
                break
            else:
                y = y + 4

        self.pdebug(f'At the top, chopping down',2)

        self.eatFood()

        y = box.y_max

        while y >= box.y_min:
            self.chop(x0,  y, z0,   1)
            self.chop(x0+1,y, z0,   1)
            self.chop(x0+1,y, z0+1, 1)
            self.chop(x0,  y, z0+1, 1)
            y = y - 1
            self.refreshActivity([f'🌲 Tree at {b0.position.x},{b0.position.z}',f'  height: {box.dy()}',f'  y: {y-box.y_min}','  ⬇️ heading down'])
            self.healToFull()

        return True

    def chopWood(self):

        area = workArea(self,1,1,1,notorch=True)
        if area.valid:            
            while not self.stopActivity:                
                area.restock(self.chopEquipList)
                if not self.chopBigTree():
                    break
        self.refreshActivity(['Restocking'])
        area.restock(self.chopEquipList)
        self.endActivity()
        return True
