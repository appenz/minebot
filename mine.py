#
# Functions for mining blocks
#

import itertools

from javascript import require
Vec3     = require('vec3').Vec3

from botlib import *
from inventory import *
from workarea import *

class MineBot:

    needs_iron_pickaxe = ["Gold Ore", "Redstone Ore", "Diamond Ore", "Emerald Ore"]
    needs_diamond_pickaxe = ["Obsidian"]
    needs_shovel = ["Dirt", "Gravel", "Sand"]

    # This is what we are looking for

    valuable_blocks = [
        "Coal Ore",
        "Copper Ore",
        "Lapis Lazuli Ore",
        "Iron Ore",
        "Gold Ore",
        "Redstone Ore",
        "Diamond Ore",
        "Emerald Ore",
        "Block of Coal",
    ]

    # These blocks never get mined up

    ignored_blocks = [
        "Torch",
        "Wall Torch",
        "Sign",
        "Air",
        "Cave Air",
        "Void Air",
        "Chest",
        "Crafting Table",
        "Furnace",
        "Ladder",
        "Glass",
        "Stone Bricks",
        "Chiseled Stone Bricks",
        "Stone Brick Stairs",
        "Water",
        "Flowing Water",
        "Bubble Column",
    ]

    # These blocks we need to bridge over

    dangerBlocks = {
        "Air",
        "Cave Air",
        "Void Air",
        "Lava",
        "Water",
        "Infested Stone",
    }

    # These blocks will drop down, we need to dig them up until done

    block_will_drop = [
        "Gravel",
        "Sand",
        "Red Sand",
        "Pointed Dropstone",
        "Anvil,"
    ]

    block_will_flow = [
        "Lava",
        "Water",
    ]

    # Blocks that will drop down on you

    dangerDropBlocks = block_will_flow + block_will_drop

    # These blocks we use to fill holes or build bridges

    fillBlocks = {
        "Stone Bricks",
        "Cobblestone",
        "Dirt"
    }

    # Inventory goals for normal mining

    miningEquipList= {
        "Bread":5,
        "Stone Pickaxe":5,
        "Stone Shovel":2,
        "Iron Pickaxe":2,
        "Torch": 10,
        "Cobblestone" : 64,
        "Stone Bricks" : 256,
        "Dirt" : 0,
        "Andesite" : 0,
        "Diorite" : 0,
        "Granite" : 0,
        "Sandstone" : 0,
        "Sand" : 0,
        "Gravel" : 0,
        "Flint" : 0,
        "Raw Iron" : 0,
        "Raw Gold" : 0,
        "Raw Copper" : 0,
        "Coal" : 0,
        "Redstone Dust" : 0,
        "Diamond" : 0,
        "Lapis Lazuli" : 0,
        "Emerald" : 0,
        "Chiseled Stone Bricks" : 0,
        "Block of Coal" : 0,
    }

    miningMinimumList = {
        "Bread":1,
        "Stone Pickaxe":2,
        "Stone Shovel":1,
        "Iron Pickaxe":1,
        "Torch": 5,
    }

    def __init__(self):
        print('mining ', end='')

    # Checks if walking to a specific block is considered safe

    def mining_safety_check(self,position):
        n = self.bot.blockAt(position).displayName
        if n in self.block_will_flow:
            self.stopActivity = True
            self.dangerType = "danger: "+n
            self.pdebug(f'danger: {n}, aborting mining',1)
            return False
        return True

    #
    # Mine a block with the right tool
    # Takes a Vector or x,y,z as input

    def mineBlock(self,x,y=None,z=None):
        if not y and not z:
            v = x
        else:
            v = Vec3(x,y,z)
        
        b = self.bot.blockAt(v)

        self.pdebug(f'    mine block   ({v.x},{v.y},{v.z}) {b.displayName} t:{b.digTime(274)}',3)

        t = b.digTime(274)
        if b.displayName:
            if b.displayName == "Copper Ore":
                t = 200

        if t > 100 and b.displayName not in self.ignored_blocks:
            # Ok, this looks mineable
            # Try 20 times, in case gravel is dropping down
            for attempts in range(0,20):
                if not self.mining_safety_check(self.bot.entity.position): return 0

                self.pdebug(f'    trying to mine',4)

                # Check for the right tool
                if b.displayName in self.needs_shovel:
                    if self.invItemCount("Stone Shovel") > 0:
                        self.wieldItem("Stone Shovel")
                    else:
                        self.wieldItem("Stone Pickaxe")
                elif b.displayName in self.needs_iron_pickaxe:
                    self.wieldItem("Iron Pickaxe")
                else:
                    self.wieldItem("Stone Pickaxe")

                # dig out the block
                try:
                    self.bot.dig(b)
                except Exception as e:
                    self.pexception(f'dig failed for block {v.x},{v.y},{v.z}) {b.displayName} t:{b.digTime(274)}',e)

                # Check if successful
                b = self.bot.blockAt(v)
                if b.digTime(274) == 0:
                    return 1
        else:
            #print(f'  ignore ({x},{y},{z}) {b.displayName}')
            return 0


    
    #
    # Mine a 1-wide path from start to end of height height
    # Assumes the bot is at start
    #

    def minePath(self,start,end,height, area=None):

        self.pdebug(f'minePath({start},{end},{height})',4)
        c = Vec3(start.x, start.y, start.z)
        d = Vec3( (end.x-start.x)/max(abs(end.x-start.x),1), 0, (end.z-start.z)/max(abs(end.z-start.z),1) )

        while True:

            # Check if path is safe
            bb = self.blockAt(c.x,c.y-1,c.z)
            if bb.displayName in self.dangerBlocks:
                self.perror(f'  stopping, dangerous block {bb.displayName} ')
                return False

            # Mine the column. May need a few tries due to gravel

            wait_t = 0

            for tries in range(0,30):

                if self.stopActivity:
                    return True

                # check if we have gravel or sand. If yes we need to check longer.
                for h in range(0,height+1):
                    b_name = self.bot.blockAt(Vec3(c.x,c.y+h,c.z)).displayName
                    if b_name in self.block_will_drop:
                        wait_t = 1
                        break

                # mine
                for h in range(0,height):
                    cc = self.mineBlock( c.x,c.y+h,c.z)
                    if area:
                        area.blocks_mined += cc

                if wait_t:
                    time.sleep(wait_t)

                for h in range(0,height):
                    b_name = self.bot.blockAt(Vec3(c.x,c.y+h,c.z)).displayName
                    if b_name not in self.ignored_blocks:
                        self.pdebug(f'  block not cleared: {b_name}.',2)
                        break
                else:
                    break

            if tries > 30:
                self.perror("can't clear this column.")
                self.stopActivity = True
                return False

            if not self.mining_safety_check(c): return 0

            self.safeWalk(c,0.3)

            # Check if we are done
            if c.x == end.x and c.z == end.z:
                return True

            if c.x != end.x:
                c.x += d.x
            if c.z != end.z:
                c.z += d.z

    #
    # Mine a rectangle of dx times dz, height h around a chest
    #

    def roomMine(self,dx_max,dz_max, height):

        dx_max = int( (checkIntArg(dx_max, 3, 99)-1)/2)
        dz_max = int( (checkIntArg(dz_max, 3, 99)-1)/2)
        height = checkIntArg(height, 2, 8)

        if not dx_max or not dz_max or not height:
            self.chat('Try: mine room <dx 3-99> <dz 3-99> <height 2-8>')
            return False

        area = workArea(self,1,1,1,notorch=True)
        if not area.valid:
            return False
        start = area.start

        self.refreshActivity([f'Room mining started'])
        self.pdebug(f'Mining out area of {2*dx_max+1} x {2*dz_max+1} x {height} blocks.',2)

        for dz in range(0,dz_max+1):    

            todo = False
            for dx in range(-dx_max,dx_max+1):
                for h in range(0,height):
                    if self.bot.blockAt(Vec3(start.x+dx, start.y+h, start.z+dz)).displayName not in self.ignored_blocks:
                        todo = True
                        break
                    if self.bot.blockAt(Vec3(start.x+dx, start.y+h, start.z-dz)).displayName not in self.ignored_blocks:
                        todo = True
                        break
                if todo:
                    break

            if not todo:
                continue

            self.refreshActivity("Restocking.")
            area.restock(self.miningEquipList)
            time.sleep(1)
            if not self.checkMinimumList(self.miningMinimumList):
                return False

            if not self.stopActivity:

                # Carve initial column
                self.refreshActivity( [ f'Blocks Mined: {area.blocks_mined}', f'Row: {dz}' ] )
                row_c = Vec3(start.x,start.y,start.z+dz)
                self.pdebug(f'walking to {row_c.x} {row_c.y} {row_c.z}',3)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x-dx_max,row_c.y,row_c.z),height, area=area)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x+dx_max,row_c.y,row_c.z),height, area=area)

            if not self.stopActivity:

                self.refreshActivity( [ f'Blocks Mined: {area.blocks_mined}', f'Row: {dz}' ] )
                row_c = Vec3(start.x,start.y,start.z-dz)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x-dx_max,row_c.y,row_c.z),height, area=area)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x+dx_max,row_c.y,row_c.z),height, area=area)


            if self.stopActivity:
                break

        # Mining ended
        area.restock(self.miningEquipList)

        return True

    #
    #  Find Valuables in a side corridor
    #  Returns max_x, max_y of the furthest

    def findValuables(self,area, max_x, max_y, z, min_y=0):
        if max_x < 0:
            r = range(0,max_x-1,-1)
        elif max_x > 0:
            r = range(0,max_x+1,1)
        else:
            return 0,0

        bx = 0
        by = 0
        name = None

        for x in r:
            for y in range(min_y,max_y):
                n = area.blockAt(x,y,z).displayName
                if n in self.valuable_blocks:
                    bx = x
                    by = max(y,by)
                    name = n
        if name:
            self.pdebug(f'  @{z:3} found {name}    {bx}/{by}',2)
            area.valuables = name
        return bx, by

    def bridgeIfNeeded(self, area, x, z):
        if area.blockAt(x,-1,z).displayName in self.dangerBlocks:
            v_place = area.toWorld(x,-1,z-1)
            # Try three times.
            for ii in range (0,3):
                self.wieldItemFromList(self.fillBlocks)
                self.bridgeBlock(v_place,area.forwardVector)
                if area.blockAt(x,-1,z).displayName not in self.dangerBlocks:
                    break
            else:                            
                self.perror(f'*** fatal error. Cant bridge dangerous block {area.blockAt(x,-1,z).displayName}')
                area.status = "blocked/drop"
                self.stopActivity = True
                return False
            area.blocks_mined += 1
        return True

    
    #
    # Mine up a column of a specific height
    # Bridge afterwards if needed.
    #

    def mineColumn(self, area, x, z, height):

        if self.stopActivity: return False
        self.pdebug(f'mineColumn(x:{x},z:{z},height:{height})',5)

        # Check if we need to do anything
        for y in range(0,height):                      
            if area.blockAt(x,y,z).displayName not in self.ignored_blocks:
                break
        else:
            return True

        # Check for infested
        for y in range(0,height):
            if area.blockAt(x,y,z).displayName == "Infested Stone":
                self.pdebug(f'  located {area.blockAt(x,y,z).displayName}, aborting!',1)
                area.status = "* Silverfish *"
                self.stopActivity = True
                return False

        # Try to mine the column. May take multiple attempts due to gravel.
        for tries in range(0,10):
            done = True
            for y in range(0,height):                     
                if self.stopActivity: return True
                if area.blockAt(x,y,z).displayName not in self.ignored_blocks:
                    # We need to clear this
                    done = False
                    if area.blockAt(x,y+1,z).displayName in self.block_will_drop:
                        self.mineBlock( area.toWorld(x,y,z) )
                        time.sleep(1)
                    else:
                        self.mineBlock( area.toWorld(x,y,z) )
                    area.blocks_mined += 1
            if done:
                break
                    
        for y in range(0,height):                      
            if area.blockAt(x,y,z).displayName not in self.ignored_blocks:
                self.perror(f'aborting - block not cleared: {area.blockAt(x,y,z).displayName}.')
                area.status = "blocked"
                self.stopActivity = True
                return False
                
        return True

#
# Check for goodies in the floor. Works best to about 2 deep.
#

    def floorMine(self, area, x, z, depth):
        if self.stopActivity: return False

        if depth > 0:
            max_d = 0
            for d in range(1,depth+1):
                if area.blockAt(x,-d,z).displayName in self.valuable_blocks:
                    max_d = d
            if max_d > 0:
                # Ok, we found something
                for d in range(1,max_d+1):
                    self.mineBlock( area.toWorld(x,-d,z) )
                # Now fill it up, which gets us the blocks. Best effort.
                for d in range(max_d, 0, -1):
                    v_place = area.toWorld(x,-d-1,z)
                    self.wieldItemFromList(self.fillBlocks)
                    self.safePlaceBlock(v_place,Vec3(0,1,0))
                    time.sleep(0.2)
        return True

    def ceilingMine(self, area, x, z, max_height):
        if self.stopActivity: return False

        # Check the ceiling up to max reachable height (7 above)
        max_y = 0
        for y in range(2,max_height):
            if area.blockAt(x,y,z).displayName in self.valuable_blocks:
                max_y = y
        if max_y > 0:
            # Ok, we found something
            for y in range(2,max_y+1):
                if area.blockAt(x,y,z).displayName not in self.ignored_blocks:
                    if area.blockAt(x,y+1,z).displayName in self.dangerDropBlocks:
                        self.pdebug(f'  cant mine ceiling, {area.blockAt(x,y+1,z).displayName} above.',2)
                        return False
                    self.mineBlock( area.toWorld(x,y,z) )

    #
    # Mine up a row. Unlike minePath, this works in an area
    #

    def mineRow(self, area, max_x, height, z, floor_mine=0, ceiling_mine=0):
        #print(f'mineRow(max_x:{max_x},height:{height},z:{z},floor_mine:{floor_mine},ceiling_mine:{ceiling_mine})')
        if max_x == 0:
            return False
        elif max_x < 0:
            dx = -1
        elif max_x > 0:
            dx = 1

        r = range(dx*area.width2+dx, max_x+dx,dx)
        area.walkToBlock3(dx*area.width2,0,z)
        height = max(2,height)

        for x in r:
            if self.stopActivity : break
            if not self.mineColumn(area, x, z, height):
                return False
            # Check floors
            if floor_mine > 0:
                self.floorMine(area, x, z, floor_mine)
            if ceiling_mine > 0:
                self.ceilingMine(area, x, z, ceiling_mine)
            # Bridge if needed
            if area.blockAt(x,-1,z).displayName in self.dangerBlocks:
                v_place = area.toWorld(x-dx,-1,z)
                # Try three times.
                self.wieldItemFromList(self.fillBlocks)
                self.bridgeBlock(v_place,area.dirToWorldV3(Vec3(dx,0,0)))
                if area.blockAt(x,-1,z).displayName in self.dangerBlocks:
                        self.pdebug(f'    cant reach, bridging failed {area.blockAt(x,-1,z).displayName}.',2)
                        area.walkToBlock3(0,0,z)
                        return False
            if not self.mining_safety_check(area.toWorld(x,0,z)): return False
            area.walkToBlock3(x,0,z)
        time.sleep(0.5)
        return True

    # Helper function for UI

    def mineActivity(self,area,z,txt1="",txt2=""):
            l = [
                    f'Depth: {z}    ⏱️ {int(100*(area.blocks_mined-area.last_break)/area.break_interval)}%',
                    f'Status: {area.status}', 
                    txt1,
                    txt2
                ]
            self.refreshActivity(l)

    #
    #  Build a strip mine of a specific height and width and light it up
    #

    def stripMine(self,width=3,height=3,valrange=3):

        z_torch = 0
        z =0
        area = workArea(self,width,height,99999)
        if not area.valid:
            return False
        self.speedMode = True   # explore fast until we find something

        self.refreshActivity([f'Mining started'])

        while not self.stopActivity:
            # Get ready
            self.mineActivity(area,z,"Restocking.")
            area.restock(self.miningEquipList)
            area.last_break = area.blocks_mined
            time.sleep(1)
            if not self.checkMinimumList(self.miningMinimumList):
                return False

            self.mineActivity(area,z,"Walking back to work")
            while area.blocks_mined-area.last_break < area.break_interval and not self.stopActivity:
                if not self.mining_safety_check(area.toWorld(0,0,z)): break
                area.walkToBlock3(0,0,z-1)

                if area.blocks_mined > 0: self.speedMode = False

                # Step 0 - Check if we are still good
                if not self.checkMinimumList(self.miningMinimumList):
                    self.perror("Aborting, out of required equipment.")
                    self.stopActivity = True
                    area.status = "out of tools"
                    break

                # Step 1 - Mine the main tunnel
                self.mineActivity(area,z,"Walking back to work", f'Mining main tunnel')
                for x in area.xRange():
                    self.mineColumn(area, x, z, height)
                    self.floorMine(area, x, z, 2)
                    self.ceilingMine(area, x, z, height+2)
                    
                # Step 2 - Bridge if needed 
                for x in area.xRange():
                    self.bridgeIfNeeded(area, x, z)
                if self.stopActivity: break

                area.walkToBlock3(0,0,z)
                # Step 3 - Look for Valuables Left and Right

                bx, by  = self.findValuables(area, -area.width2-valrange, height+2, z, min_y=-2)
                by = min(by,height-1)
                if bx != 0:
                    self.mineActivity(area, z, f'Found: {area.valuables}✨', f'⬅️ Left side {bx}/{by+1}')
                    self.mineRow(area, bx, by+1, z, floor_mine=2, ceiling_mine=height+2)
                    area.walkToBlock3(0,0,z)

                bx, by  = self.findValuables(area, area.width2+valrange, height+2, z, min_y=-2)
                by = min(by,height-1)
                if bx != 0:
                    self.mineActivity(area, z, f'Found: {area.valuables}✨', f'➡️ Right side {bx}/{by+1}')
                    self.mineRow(area, bx, by+1, z, floor_mine=2, ceiling_mine=height+2)
                    area.walkToBlock3(0,0,z)

                # Step 4 - Light up if needed and move forward by one.
                if z > z_torch:
                    self.mineActivity(area, z, f'Placing Torch')
                    # try to place a torch
                    torch_v = area.toWorld(area.width2,1,z)
                    wall_v  = area.toWorld(area.width2+1,1,z)
                    dv = subVec3(torch_v, wall_v)
                    if self.bot.blockAt(wall_v).displayName not in self.ignored_blocks:
                        if self.bot.blockAt(torch_v).displayName != "Wall Torch":
                            self.pdebug("  placing torch.",2)
                            self.wieldItem("Torch")
                            self.safePlaceBlock(wall_v,dv)
                        z_torch += 6
                z += 1

            # ...and back to the chest to update sign and restock
            self.speedMode = False
            self.mineActivity(area, z, f'Walking to Chest')
            area.walkToStart()
            if self.dangerType:
                s = self.dangerType
            else:
                s = area.status
            self.mineActivity(area, z, f'Updating Sign')
            txt = [f'Mine {area.directionStr()} {width}x{height}', f'Length: {z}', myDate(), s ]
            self.updateSign(txt,tryonly=True)

        # Mining ended
        area.restock(self.miningEquipList)


    #
    # Mine a vertical shaft of N x N down to depth D
    #

    def shaftMine(self,d,min_y):

        r = int( (checkIntArg(d, 1, 99)-1)/2)
        d = r*2+1
        min_y = checkIntArg(min_y, -64, 320)

        if r == None or min_y == None:
            print(r,min_y)
            self.chat('Try: mine shaft <diameter: 1 to 99> <bottom: -65 to 320>')
            return False

        area = workArea(self,d,d,1,notorch=True)
        if not area.valid:
            return False
        start = area.start
        area.restock(self.miningEquipList)

        self.refreshActivity([f'Shaft mining started'])
        self.pdebug(f'Mining vertical shaft of {d} x {d} down to level {min_y}',2)

        for y in range(0, min_y-start.y-1, -1):
            for dz in range(0,r+1):    

                if not self.stopActivity:
                    self.refreshActivity( [ f'Vertical Shaft {d}x{d} to lvl {min_y}',f'Blocks Mined: {area.blocks_mined}', f'Depth: {y}' ] )
                    area.walkToBlock(0,y,dz)
                    self.minePath(area.toWorld(0,y,dz),area.toWorld(-r,y,dz),2, area=area)
                    area.walkToBlock(0,y,dz)
                    self.minePath(area.toWorld(0,y,dz),area.toWorld( r,y,dz),2, area=area)

                if not self.stopActivity:

                    self.refreshActivity( [ f'Vertical Shaft {d}x{d} to lvl {min_y}',f'Blocks Mined: {area.blocks_mined}', f'Depth: {y}' ] )
                    area.walkToBlock(0,y,-dz)
                    self.minePath(area.toWorld(0,y,-dz),area.toWorld(-r,y,-dz),2, area=area)
                    area.walkToBlock(0,y,-dz)
                    self.minePath(area.toWorld(0,y,-dz),area.toWorld( r,y,-dz),2, area=area)

                if self.stopActivity:
                    break

        # Mining ended - no deposit as we may not be able to get up the shaft

        return True
     

    def doMining(self,args):

        if len(args) == 0:
            self.chat('Need to specify type of mine. Try "fast", "3x3" or "5x5".')
        else:
            mtype = args[0]
            if mtype == '3x3':
                self.activity_name = "Mine 3x3"
                self.stripMine(3,3,5)
            elif mtype == 'tunnel3x3':
                self.activity_name = "Tunnel 3x3"
                self.stripMine(3,3,0)
            elif mtype == '5x5':
                self.activity_name = "Mine 5x5"
                self.stripMine(5,5,5)
            elif mtype == 'tunnel5x5':
                self.activity_name = "Tunnel 5x5"
                self.stripMine(5,5,0)
            elif mtype == 'branch' or mtype == 'fast':
                self.activity_name = "Branchmine"
                self.stripMine(1,5,5)
            elif mtype == 'room':
                if len(args) < 4:
                    self.chat('Try: mine room <length> <width> <height>')
                else:
                    self.activity_name = f'Mine Room {args[1]}x{args[2]}x{args[3]}'
                    self.roomMine(args[1],args[2],args[3])
            elif mtype == 'shaft':
                if len(args) < 3:
                    self.chat('Try: mine shaft <diameter> <layer of shaft bottom>')
                    self.activity_name = f'Mine Vertical Shaft {args[1]}x{args[1]} to level {args[2]}'
                else:
                    self.shaftMine(args[1],args[2])
            else:
                self.chat(f'I don\'t know how to mine a \'{mtype}\'.')

        self.endActivity()
        time.sleep(1)
        return True