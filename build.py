#
# Build various blueprints
#

from javascript import require
from botlib import *

Vec3     = require('vec3').Vec3

from blueprint import *
from workarea import *

import blueprint_data

#
# Main class that has the build, analyze and helper functions
#

class BuildBot:

    def __init__(self):
        self.blueprintList = []
        print('build ', end='')
        blueprint_data.init(self)

    def learnBlueprint(self,b):
        self.blueprintList.append(b)

    def listBlueprints(self):
        return ' '.join([str(n) for n in Blueprint.bpList])

    def getBlueprint(self,name):
        for b in self.blueprintList:
            if str(b) == name:
                return b
        else:
            return None


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
    #  Translate world blocks to inventory items
    #

    def world2inv(self,block_name):
        if block_name in self.blockW2I:
            return self.blockW2I[block_name]
        else:
            return block_name

    #
    # Build an Thing
    #

    def doBuild(self,args):

        if len(args) == 0:
            self.chat('Need to specify blueprint to build.')
        else:
            bp_name = args[0]

        stage = 1

        while not self.stopActivity:

            bp = self.getBlueprint(bp_name+"_"+str(stage))

            # Special handling for the first phase
            if stage == 1:
                if not bp:
                    print(f'Cant find blueprint {bp_name}.')
                    break
            else:
                if bp:
                    print(f'Phase {stage} is starting.')
                else:
                    # Done, no next phase
                    break

            # Define the area - may be different for each phase
            area = workArea(self,bp.width,bp.height,bp.depth)
            if not area.valid:                
                break

            # Analyze what we need, and what is already there

            need= {"Bread":2}

            for v in area.allBlocks():
                old_b = area.blockAt(v).displayName
                new_b = bp.blockAt(v)

                if old_b not in self.emptyBlocks:
                    # something is there already
                    if old_b != new_b:
                        # and it's now what we expect
                        print(f'*** error: wrong object {old_b} instead of {new_b} at position {v}. Clear the area.')
                        self.endActivity()
                        return False
                elif new_b not in self.emptyBlocks:
                    new_inv = self.world2inv(new_b)
                    need[new_inv] = need.get(new_inv,0) + 1
                else:
                    # This is an empty space
                    pass

            if need:
                print(need)
                area.restock(need)
            else:
                print("  all needed items already in inventory.")

            sneak = False
            jump = False

            # Build, back to front, bottom to top
            for z in range(bp.depth-1,-1,-1):
                for y in bp.yRange():
                    for x in bp.xRange():
                        if self.stopActivity:
                            break

                        block_type = bp.blockAt(Vec3(x,y,z))

                        # Just air in the blueprint? Continue...
                        if block_type in self.emptyBlocks:
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

                        if area.blockAt(Vec3(x,y-1,z)).displayName not in self.emptyBlocks:
                            # Easiest case: block below the block we want to place is not empty.
                            against_v = area.toWorld(x,y-1,z)
                            direction_v = Vec3(0,1,0)
                            placement_type = " (top)"
                        elif area.blockAt(Vec3(x,y,z+1)).displayName not in self.emptyBlocks:
                            # Block behind the block we want to palce is there, let's place against that
                            against_v = area.toWorld(x,y,z+1)
                            direction_v = Vec3(-area.d.x,0,-area.d.z)
                            placement_type = " (front)"
                        elif not spec:
                            # Nothing works, no special instructions
                            print(f'*** error ({x:3},{y:3},{z:3}) {block_type} no placement strategy found')
                            self.stopActivity = True
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
                                bot_v_center = Vec3(bot_v.x+0.5, bot_v.y, bot_v.z+0.5)
                                placement_type +=" pos"

                            if spec.block_against:
                                against_v = area.toWorldV3(spec.block_against)
                                placement_type +=" @ "

                            if spec.block_surface:
                                direction_v = area.dirToWorldV3(spec.block_surface)
                                placement_type +=" dir"

                            self.safeWalk(bot_v_center,0.1)
                            time.sleep(1)

                        else:
                            self.safeWalk(bot_v_center,0.2)
                            time.sleep(1)

                        against_type = self.bot.blockAt(against_v).displayName

                        # Let's do this

                        print(f'  ({x:3},{y:3},{z:3}) {block_type} -> {against_type} {placement_type}')

                        if not self.wieldItem(self.world2inv(block_type)):
                            print(f'*** aborting, cant wield item {block_type}')
                            self.stopActivity = True
                            break

                        if against_type in self.interactiveBlocks:
                            self.bot.setControlState('sneak', True)
                            time.sleep(0.5)
                            sneak = True

                        if spec and spec.sneak:
                            self.bot.setControlState('sneak', True)
                            time.sleep(0.2)
                            sneak = True

                        if spec and spec.jump:
                            self.bot.setControlState('jump', True)
                            time.sleep(0.2)
                            jump = True

                        if not self.safePlaceBlock(against_v,direction_v):
                            print(f'*** aborting, cant place block {block_type} at {x}, {y}, {z}')
                            self.stopActivity = True
                            break

                        if sneak:
                            self.bot.setControlState('sneak', False)
                            sneak = False

                        if jump:
                            self.bot.setControlState('jump', False)
                            jump = False

            stage += 1

            self.safeWalk(area.start)
            time.sleep(1)

        self.endActivity()

    #
    # Analyze the area in front and print in python format
    #

    def analyzeBuild(self,width=3,height=4, depth=6):

        area = workArea(self,width,height,depth)

        if not area.valid:
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
                    b = self.bot.blockAt(area.toWorld(x,y,z))
                    s = '"'+b.displayName+'"'
                    print(f'{s:15}',end=", ")
                print(f'],')
            print(f'  ],')
        print(f']')
