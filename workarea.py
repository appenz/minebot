#
# Definition of a work area to do stuff in (e.g. build, mine etc.)
# Main purpose is to handle relative to absolute coordinates
#

from botlib import *

# Area in front of chest+torch
#   x is lateral (torch is 0)
#   z is depth (torch is at -1)
#   y is height (chest is at 0)
#
#   NOTE: This means this is a LEFT HANDED coordinate system while
#         Minecraft uses a RIGHT HANDED coordinate system. Yes, I know.
#         It still makes more sense this way.

class workArea:

    #
    # Initialize a work area
    #

    valuables = None
    status = "all good"
    blocks_mined = 0
    last_break = 0
    break_interval = 100

    def __init__(self,pybot,width,height,depth, notorch=False):
        self.valid = False
        self.pybot = pybot

        if width % 2 != 1:
            self.pybot.perror(f'Error: width={width} but only odd width work areas are supported.')
            return None

        self.width = width
        self.width2 = int((width-1)/2)
        self.height = height
        self.depth = depth


        self.start_chest = pybot.findClosestBlock("Chest",xz_radius=3,y_radius=1)

        if not self.start_chest:
            self.pybot.chat("Can't find starting position. Place a chest on the ground to mark it.")
            return None

        if notorch:
            # Area with arbitrary direction, we pick point in front of chest
            p = self.start_chest.getProperties()
            self.d = strDirection(p["facing"])
            self.start = addVec3(self.start_chest.position,self.d)

            # Origin
            self.origin = self.start

        else:
            # Determine "forward" direction from chest+torch
            torch   = pybot.findClosestBlock("Torch",xz_radius=3,y_radius=1)
            r_torch = pybot.findClosestBlock("Redstone Torch",xz_radius=3,y_radius=1)

            # Redstone Torch has precedence
            if r_torch:
                self.start_torch = r_torch
            else:
                self.start_torch = torch

            if not self.start_torch:
                self.pybot.chat("Can't find starting position. Place chest, and torch on the ground next to it to mark the direction.")
                return None

            if self.start_torch.position.y != self.start_chest.position.y:
                self.pybot.chat("Can't find starting position. Chest and torch at different levels??")
                return None

            # Direction of the Area
            self.d = subVec3(self.start_torch.position, self.start_chest.position)
            if lenVec3(self.d) != 1:
                self.pybot.chat("Can't find starting position. Torch is not next to chest.")
                return None

            self.start = self.start_chest.position

            # Origin
            self.origin = Vec3(self.start.x+2*self.d.x,self.start.y,self.start.z+2*self.d.z)

        # Vector directions
        self.forwardVector = self.d
        self.backwardVector = invVec3(self.d)

        # Note that we flip build area vs. world coordinates. Left Handed vs Right handed.
        self.leftVector = rotateLeft(self.d)
        self.rightVector = rotateRight(self.d)

        self.latx = self.rightVector.x
        self.latz = self.rightVector.z

        # Done. Set flag.
        self.valid = True

    def xRange(self):
        return range(-self.width2, self.width2+1)

    def yRange(self):
        return range(0,self.height)

    def zRange(self):
        return range(0,self.depth)


    def toWorld(self,x,y,z):
        return Vec3(self.origin.x+self.latx*x+self.d.x*z,
                    self.origin.y+y,
                    self.origin.z+self.latz*x+self.d.z*z)

    # Convert position relative to absolute coordinates

    def toWorldV3(self,v):
        return Vec3(self.origin.x+self.latx*v.x+self.d.x*v.z,
                    self.origin.y+v.y,
                    self.origin.z+self.latz*v.x+self.d.z*v.z)


    # Convert direction relative to absolute coordinates

    def dirToWorldV3(self,v):
        return Vec3(self.latx*v.x+self.d.x*v.z,
                    v.y,
                    self.latz*v.x+self.d.z*v.z)

    # Minecraft block at relative coordinates

    def blockAt(self,*argv):
        if len(argv) == 3:
            return self.pybot.bot.blockAt(self.toWorld(argv[0],argv[1],argv[2]))
        else:
            return self.pybot.bot.blockAt(self.toWorldV3(argv[0]))

    # Returns a list of all blocks in the workArea

    def allBlocks(self):
        blocks = []

        for z in self.zRange():
            for y in self.yRange():
                for x in self.xRange():
                    blocks.append(Vec3(x,y,z))
        return blocks

    # Returns a list of all blocks in the workArea

    def allBlocksWorld(self):
        blocks = []

        for z in self.zRange():
            for y in self.yRange():
                for x in self.xRange():
                    blocks.append(self.toVec3(x,y,z))
        return blocks

    # Convert position relative to absolute coordinates

    def walkTo(self, *argv):
        if len(argv) == 3:
            v = self.toWorld(argv[0],argv[1],argv[2])
        else:
            v = self.toWorldV3(argv[0])
        self.pybot.walkTo(v)

    def walkToBlock(self, *argv):
        if len(argv) == 3:
            v = self.toWorld(argv[0],argv[1],argv[2])
        else:
            v = self.toWorldV3(argv[0])
        self.pybot.walkToBlock(v)

    # More precise version (0.3 blocks)

    def walkToBlock3(self, *argv):
        if len(argv) == 3:
            v = self.toWorld(argv[0],argv[1],argv[2])
        else:
            v = self.toWorldV3(argv[0])
        self.pybot.walkToBlock3(v)


    # String area direction as North, South etc.

    def directionStr(self):
        return directionStr(self.d)

    # Walk back to Torch

    def walkToStart(self):
        self.pybot.walkToBlock3(self.start)        

    # Restock from Chest

    def restock(self, item_list):
        self.walkToStart()
        self.pybot.restockFromChest(item_list)
        self.pybot.eatFood()

