#
# Class for encapsulating special build instructions for a specific block
# in a blueprint
#

from dataclasses import dataclass
from javascript import require
Vec3     = require('vec3').Vec3

@dataclass
class SpecialBuild:
    bot_pos : Vec3 = None
    block_against : Vec3 = None
    block_surface : Vec3 = None
    placement_type: str = None
    sneak : bool = False
    jump : bool = False

#
# Class that stores a blueprint
#

class Blueprint:

    def __init__(self, name, width=0, height=0, depth=0, bpData=None, buildFunction=None):
        self.name = name
        self.buildFunction = buildFunction
        self.bpData = bpData
        self.width = width
        self.width2 = int((width-1)/2)
        self.height = height
        self.depth = depth
        
    def xRange(self):
        return range(-self.width2, self.width2+1)

    def yRange(self):
        return range(0,self.height)

    def zRange(self):
        return range(0,self.depth)

    def blockAt(self,v):
        return self.block(v.x,v.y,v.z)

    def block(self,x,y,z):
        if x not in self.xRange() or y not in self.yRange() or z not in self.zRange():
            print(f'*** error blueprint {self} index out of range {x} {y} {z}.')
            return False
        # Note: need to invert the y axis
        # print(f'[{x+self.width2}][{self.height-1-y}][{z}]')
        return self.bpData[z][self.height-1-y][x+self.width2]

    def __str__(self):
        return(self.name)