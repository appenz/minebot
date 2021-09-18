#
# Build various blueprints
#

from javascript import require
Vec3     = require('vec3').Vec3
from dataclasses import dataclass

from inventory import *
from blocks import *
from farming import *
import blueprints
import botlib

emptyBlocks = {
  "Air",
  "Cave Air",
  "Void Air",
}

# Blocks where the inventory item is different from the block in the world

blockW2I = {
  "Redstone Wire": "Redstone Dust",
  "Redstone Wall Torch": "Redstone Torch",
}

# Blocks that require sneak to place against (chests, repeaters etc.)

interactiveBlocks = [
  "Redstone Repeater",
  "Redstone Comparator",
  "Chest",
  "Hopper",
]

#
# Class for encapsulating special build instructions for a specific block
# in a blueprint
#

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
    bpList = []

    def __init__(self, name, width=0, height=0, depth=0, bpData=None, buildFunction=None):
        self.name = name
        self.buildFunction = buildFunction
        self.bpData = bpData
        self.width = width
        self.width2 = int((width-1)/2)
        self.height = height
        self.depth = depth

        self.xrange = range(-self.width2, self.width2+1)
        self.yrange = range(0,height)
        self.zrange = range(0,depth)

    def blockAt(self,v):
        return self.block(v.x,v.y,v.z)

    def block(self,x,y,z):
        if x not in self.xrange or y not in self.yrange or z not in self.zrange:
            print(f'*** error blueprint {self} index out of range {x} {y} {z}.')
            return False
        # Note: need to invert the y axis
        # print(f'[{x+self.width2}][{self.height-1-y}][{z}]')
        return self.bpData[z][self.height-1-y][x+self.width2]

    def __str__(self):
        return(self.name)

    # Add a Blueprint to the list of blueprints
    def learn(self):
        self.bpList.append(self)

    def listBlueprints():
        return ' '.join([str(n) for n in Blueprint.bpList])

    def getBlueprint(name):
        for b in Blueprint.bpList:
            if str(b) == name:
                return b
        else:
            return None


#
#  Translate world blocks to inventory items
#

def world2inv(block_name):
    if block_name in blockW2I:
        return blockW2I[block_name]
    else:
        return block_name

#
# init_build()
#
def init_build(bot):
    Blueprint.bot = bot
    blueprints.init()
    print("Blueprints: ",Blueprint.listBlueprints())

#
# Sorting System
#

sorterParts= {
  "Redstone Comparator":3,
  "Redstone Torch":3,
  "Redstone Repeater":3,
  "Stone Bricks":26,
  "Chest": 7,
  "Redstone Dust" : 9,
  "Hopper" : 10,
}

#
# Area in front of chest+torch
# x is lateral (torch is 0)
# z is depth (torch is at -1)
# y is height (chest is at 0)

class workArea:

    #
    # Initialize a work area
    #

    def __init__(self,bot,width,height,depth):
        self.bot = bot

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
        self.start_chest = findClosestBlock(bot,"Chest",xz_radius=3,y_radius=1)
        self.start_torch = findClosestBlock(bot,"Torch",xz_radius=3,y_radius=1)

        if not self.start_chest or not self.start_torch:
            print("Can't find starting position. Place chest, and torch on the ground towards the analysis direction.")
            return None

        if self.start_torch.position.y != self.start_chest.position.y:
            print("Can't find starting position. Place chest, and torch on the ground towards the analysis direction.")
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
        return self.bot.blockAt(self.toWorldV3(v))

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

#
# Build Functions
#


def doBuild(bot,bp_name):

    stage = 1

    while True:

        bp = Blueprint.getBlueprint(bp_name+"_"+str(stage))

        # Special handling for the first phase
        if stage == 1:
            if not bp:
                print(f'Cant find blueprint {bp_name}.')
                return False
            botlib.startActivity(bot,"Building: "+bp_name)
        else:
            if bp:
                print(f'Phase {stage} is starting.')
            else:
                # Done, no next phase
                break

        # Define the area - may be different for each phase
        area = workArea(bot,bp.width,bp.height,bp.depth)
        if not area:
            return False

        # Analyze what we need, and what is already there

        need= {"Bread":2}

        for v in area.allBlocks():
            old_b = area.blockAt(v).displayName
            new_b = bp.blockAt(v)

            if old_b not in emptyBlocks:
                # something is there already
                if old_b != new_b:
                    # and it's now what we expect
                    print(f'*** error: wrong object {old_b} instead of {new_b} at position {v}. Clear the area.')
                    return False
            elif new_b not in emptyBlocks:
                new_inv = world2inv(new_b)
                need[new_inv] = need.get(new_inv,0) + 1
            else:
                # This is an empty space
                pass

        if need:
            restockFromChest(bot, need)
        else:
            print("  all needed items already in inventory.")

        sneak = False
        jump = False

        # Build, back to front, bottom to top
        for z in range(bp.depth-1,-1,-1):
            if bot.stopActivity:
                break

            for y in bp.yrange:
                if bot.stopActivity:
                    break

                for x in bp.xrange:
                    if bot.stopActivity:
                        break

                    block_type = bp.blockAt(Vec3(x,y,z))

                    # Just air in the blueprint? Continue...
                    if block_type in emptyBlocks:
                        continue

                    # Correct block already there? Continue...
                    if area.blockAt(Vec3(x,y,z)).displayName == block_type:
                        continue

                    bot_v = area.toWorld(x,0,z-1.5)
                    bot_v_center = Vec3(bot_v.x+0.5, bot_v.y, bot_v.z+0.5)

                    # Figure out how we can place this block.
                    # This is complicated...

                    placement_type = "unknown"

                    if bp.buildFunction:
                        spec = bp.buildFunction(x,y,z)
                    else:
                        spec = None

                    if area.blockAt(Vec3(x,y-1,z)).displayName not in emptyBlocks:
                        # Easiest case: block below the block we want to place is not empty.
                        against_v = area.toWorld(x,y-1,z)
                        direction_v = Vec3(0,1,0)
                        placement_type = " (top)"
                    elif area.blockAt(Vec3(x,y,z+1)).displayName not in emptyBlocks:
                        # Block behind the block we want to palce is there, let's place against that
                        against_v = area.toWorld(x,y,z+1)
                        direction_v = Vec3(-area.d.x,0,-area.d.z)
                        placement_type = " (front)"
                    elif not spec:
                        # Nothing works, no special instructions
                        print(f'*** error ({x:3},{y:3},{z:3}) {block_type} no placement strategy found')
                        bot.stopActivity = True
                        break

                    if spec:
                        placement_type +=" S"
                        if spec.jump:
                            placement_type +=" jmp"
                        if spec.sneak:
                            placement_type +=" snk"
                        if spec.placement_type:
                            placement_type = spec.placement_type

                        if spec.bot_pos:
                            bot_v = area.toWorldV3(spec.bot_pos)
                            bot_v_center = Vec3(bot_v.x, bot_v.y, bot_v.z)
                            placement_type +=" pos"

                        if spec.block_against:
                            against_v = area.toWorldV3(spec.block_against)
                            placement_type +=" @ "

                        if spec.block_surface:
                            direction_v = area.dirToWorldV3(spec.block_surface)
                            placement_type +=" dir"

                        safeWalk(bot,bot_v_center,0.1)
                        if spec.bot_pos:
                            time.sleep(0.5)

                    else:
                        safeWalk(bot,bot_v_center,0.2)

                    against_type = bot.blockAt(against_v).displayName

                    # Let's do this

                    print(f'  ({x:3},{y:3},{z:3}) {block_type} -> {against_type} {placement_type}')

                    if not wieldItem(bot, world2inv(block_type),quiet=True):
                        print(f'*** aborting, cant wield item {block_type}')
                        bot.stopActivity = True
                        break

                    if against_type in interactiveBlocks:
                        bot.setControlState('sneak', True)
                        time.sleep(0.5)
                        sneak = True

                    if spec and spec.sneak:
                        bot.setControlState('sneak', True)
                        time.sleep(0.2)
                        sneak = True

                    if spec and spec.jump:
                        bot.setControlState('jump', True)
                        time.sleep(0.2)
                        jump = True

                    if not safePlaceBlock(bot,against_v,direction_v):
                        print(f'*** aborting, cant place block {block_type} at {x}, {y}, {z}')
                        bot.stopActivity = True
                        break

                    if sneak:
                        bot.setControlState('sneak', False)
                        sneak = False

                    if jump:
                        bot.setControlState('jump', False)
                        jump = False

        stage += 1

        safeWalk(bot,area.start)
        eatFood(bot)
        time.sleep(1)

    self.endActivity()

#
# Analyze the area in front and print in python format
#

def analyzeBuild(bot,width=3,height=4, depth=6):

    area = workArea(bot,width,height,depth)

    if not area:
        return False

    w2 = int((width-1)/2)    # offset from center for width

    print(f'# Minebot Blueprint')
    print(f'# {width} x {height} x {depth}')
    print(f'')
    print(f'bpData = [')

    for z in range(0,depth):
        print(f'  [')
        for y in range(height-1,-1,-1):
            print(f'    [',end="")
            for x in range(-w2, w2+1):
                b = bot.blockAt(area.toWorld(x,y,z))
                s = '"'+b.displayName+'"'
                print(f'{s:15}',end=", ")
            print(f'],')
        print(f'  ],')
    print(f']')
