#
# Definition of a work area to do stuff in (e.g. build, mine etc.)
# Main purpose is to handle relative to absolute coordinates
#

from botlib import *

# Area in front of chest+torch
#   x is lateral (torch is 0)
#   z is depth (torch is at -1)
#   y is height (chest is at 0)

class workArea:

    #
    # Initialize a work area
    #

    def __init__(self,pybot,width,height,depth):
        self.valid = False
        self.pybot = pybot

        if width % 2 != 1:
            print(f'Error: width={width} but only odd width blueprints are supported.')
            return None

        self.width = width
        self.width2 = int((width-1)/2)
        self.height = height
        self.depth = depth

        self.xrange = range(-self.width2, self.width2+1)
        self.yrange = range(0,height)
        self.zrange = range(0,depth)

        # Determine "forward" direction from chest+torch
        self.start_chest = pybot.findClosestBlock("Chest",xz_radius=3,y_radius=1)
        self.start_torch = pybot.findClosestBlock("Torch",xz_radius=3,y_radius=1)

        if not self.start_chest or not self.start_torch:
            print("Can't find starting position. Place chest, and torch on the ground towards the analysis direction.")
            return None

        if self.start_torch.position.y != self.start_chest.position.y:
            print("Can't find starting position. Chest and torch at different levels??")
            return None

        # Direction of the Area
        self.d = subVec3(self.start_torch.position, self.start_chest.position)
        if lenVec3(self.d) != 1:
            print("Torch is not next to chest.")
            return None

        self.start = self.start_chest.position

        # Origin
        self.origin = Vec3(self.start.x+2*self.d.x,self.start.y,self.start.z+2*self.d.z)

        # lateral direction, note that this is always positive
        # This means we mirror construction
        self.latx = abs(self.d.z)
        self.latz = abs(self.d.x)
        
        # Done. Set flag.
        self.valid = True


    # Convert position relative to absolute coordinates

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

    def blockAt(self,v):
        return self.pybot.bot.blockAt(self.toWorldV3(v))

    # Returns a list of all blocks in the workArea

    def allBlocks(self):
        blocks = []

        for z in self.zrange:
            for y in self.yrange:
                for x in self.xrange:
                    blocks.append(Vec3(x,y,z))
        return blocks

    # Returns a list of all blocks in the workArea

    def allBlocksWorld(self):
        blocks = []

        for z in self.zrange:
            for y in self.yrange:
                for x in self.xrange:
                    blocks.append(self.toVec3(x,y,z))
        return blocks