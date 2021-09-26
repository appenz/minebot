#
# Functions for mining blocks
#

from javascript import require
Vec3     = require('vec3').Vec3

from botlib import *
from inventory import *

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
        "Emerald Ore"
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
        "Stone Bricks"
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
        "Sand"
    ]

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
        "Torch": 5,
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
        "Iron Ore" : 0,
        "Gold Ore" : 0,
        "Copper Ore" : 0,
        "Coal" : 0,
        "Redstone Dust" : 0,
        "Diamond" : 0,
        "Lapis Lazuli" : 0,
        "Emerald" : 0,
    }

    def __init__(self):
        print('mining ', end='')

    #
    # Mine a block with the right tool
    #

    def mineBlock(self,x,y,z):
        v = Vec3(x,y,z)
        b = self.bot.blockAt(v)

        if b.digTime(274) > 100 and b.displayName not in self.ignored_blocks:
            # Ok, this looks mineable
            # Try 20 times, in case gravel is dropping down
            for attempts in range(0,20):
                print(f'  mine   ({x},{y},{z}) {b.displayName} t:{b.digTime(274)}')

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
                self.bot.dig(b)
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

    def minePath(self,start,end,height):

        c = Vec3(start.x, start.y, start.z)
        d = Vec3( (end.x-start.x)/max(abs(end.x-start.x),1), 0, (end.z-start.z)/max(abs(end.z-start.z),1) )

        while True:

            # Check if path is safe
            bb = self.bot.blockAt(c.x,c.y-1,c.z)
            if bb.displayName in self.dangerBlocks:
                print(f'  stopping, dangerous block {bb.displayName} ')
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
                    self.mineBlock( c.x,c.y+h,c.z)

                if wait_t:
                    time.sleep(wait_t)

                for h in range(0,height):
                    b_name = self.bot.blockAt(Vec3(c.x,c.y+h,c.z)).displayName
                    if b_name not in self.ignored_blocks:
                        print(f'  block not cleared: {b_name}.')
                        break
                else:
                    break

            if tries > 30:
                print("  *** error, can't clear this column.")
                self.stopActivity = True
                return False

            self.safeWalk(c,0.3)

            # Check if we are done
            if c.x == end.x and c.z == end.z:
                #print("  side mining complete")
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

        chest = Chest(self)
        chest.open()

        if not chest.block:
            self.perror("Can't find starting position. Place chest wiht materials to place the center.")
            return False

        self.pdebug(f'Mining out area of {2*dx_max+1} x {2*dz_max+1} x {height} blocks.',2)
        start = chest.block.position
        chest.restock(self.miningEquipList)
        chest.close()
        self.eatFood()


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

            if not self.stopActivity:

                self.pdebug(f'  starting row: +{dz}',2)

                # Carve initial column

                row_c = Vec3(start.x,start.y,start.z+dz)
                self.pdebug(f'walking to {row_c.x} {row_c.y} {row_c.z}',3)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x-dx_max,row_c.y,row_c.z),height)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x+dx_max,row_c.y,row_c.z),height)

            if not self.stopActivity:

                self.pdebug(f'  starting row: -{dz}',2)
                row_c = Vec3(start.x,start.y,start.z-dz)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x-dx_max,row_c.y,row_c.z),height)
                self.walkTo(row_c)
                self.minePath(row_c,Vec3(row_c.x+dx_max,row_c.y,row_c.z),height)

            self.safeWalk(start)
            chest.restock(self.miningEquipList)
            chest.close()
            self.eatFood()

            if self.stopActivity:
                break

        return True



    #
    # Build a strip mine of a specific height and width and light it up
    #

    def stripMine(self,width=3,height=3,valrange=3):

        # Determine "forward" direction from chest+torch
        start_chest = self.findClosestBlock("Chest",xz_radius=3,y_radius=1)
        start_torch = self.findClosestBlock("Torch",xz_radius=3,y_radius=1)

        if not start_chest or not start_torch:
            print("Can't find starting position. Place chest, and torch on the ground towards the mining direction.")
            return

        if start_torch.position.y != start_chest.position.y:
            print("Can't find starting position. Place chest, and torch on the ground towards the mining direction.")
            return

        d = subVec3(start_torch.position, start_chest.position)
        if lenVec3(d) != 1:
            print("Torch is not next to chest.")
            return

        print(f'Strip mining started towards ({d.x}, {d.z}):')
        start = start_chest.position

        # position 2 forward from starting position
        cursor = addVec3(start, d)

        # lateral direction (i.e. strip mine cross section)
        latx = abs(d.z)
        latz = abs(d.x)

        w2 = int((width-1)/2)    # offset from center for width

        self.restockFromChest(self.miningEquipList)

        while True:
            if self.stopActivity:
                print("Strip mining ended.")
                return

            mined_blocks = 0

            while mined_blocks < 100 and not self.stopActivity:

                # Move deeper down the strip mine
                cursor = addVec3(cursor, d)
                tic = abs(cursor.x)+abs(cursor.z)

                self.safeWalk(cursor)

                for i in range(-w2, w2+1):

                    c = Vec3(cursor.x+i*latx, cursor.y, cursor.z+i*latz)
                    # Try 30 up to times to clear the column. Needed for gravel
                    for tries in range(0,30):

                        if self.stopActivity:
                            break

                        wait_t = None
                        # check if block needs special handling
                        for h in range(0,height+1):
                            b_name = self.bot.blockAt(Vec3(c.x,c.y+h,c.z)).displayName
                            if b_name in self.block_will_drop:
                                wait_t = 1
                                break
                            if b_name == "Infested Stone":
                                self.stopActivity = True
                                break

                        # mine
                        for h in range(0,height):
                            mined_blocks += self.mineBlock( c.x,c.y+h,c.z)

                        if wait_t:
                            time.sleep(wait_t)

                        for h in range(0,height):
                            b_name = self.bot.blockAt(Vec3(c.x,c.y+h,c.z)).displayName
                            if b_name not in self.ignored_blocks:
                                print(f'  block not cleared: {b_name}.')
                                break
                        else:
                            break

                # check sides for valuable things

                if valrange > 0 and not self.stopActivity:
                    h_max = 1
                    v_max = None

                    for i in range(0, w2+valrange+1):

                        # Check for danger
                        v = Vec3(cursor.x+i*latx, cursor.y-1, cursor.z+i*latz)
                        b = self.bot.blockAt(v)
                        if b.displayName in self.dangerBlocks:
                            print(f'Danger: {b.displayName}')
                            self.safeWalk(cursor)
                            break

                        for j in range(0,height):
                            v = Vec3(cursor.x+i*latx, cursor.y+j, cursor.z+i*latz)
                            b = self.bot.blockAt(v)
                            if b.displayName in self.valuable_blocks:
                                found = True
                                if j > h_max:
                                    h_max = j
                                v_max = v
                                self.pdebug(f'  located {b.displayName}',2)
                        
                    if v_max:
                        self.minePath(cursor,Vec3(v_max.x,cursor.y,v_max.z),h_max+1)
                        self.safeWalk(cursor)

                    h_max = 1
                    v_max = None

                    for i in range(0, -w2-valrange-1, -1):

                        # Check for danger
                        v = Vec3(cursor.x+i*latx, cursor.y-1, cursor.z+i*latz)
                        b = self.bot.blockAt(v)
                        if b.displayName in self.dangerBlocks:
                            print(f'Danger: {b.displayName}')
                            self.safeWalk(cursor)
                            break

                        for j in range(0,height):
                            v = Vec3(cursor.x+i*latx, cursor.y+j, cursor.z+i*latz)
                            b = self.bot.blockAt(v)
                            if b.displayName in self.valuable_blocks:
                                found = True
                                if j > h_max:
                                    h_max = j
                                v_max = v
                                self.pdebug(f'located {b.displayName}')
                        
                    if v_max:
                        self.minePath(cursor,Vec3(v_max.x,cursor.y,v_max.z),h_max+1)
                        self.safeWalk(cursor)


                if tic % 7 == 0:
                    # place a torch
                    torch_v = Vec3(cursor.x+(w2)*latx, cursor.y+1, cursor.z+(w2)*latz)

                    #print(self.bot.blockAt(torch_v))
                    if self.bot.blockAt(torch_v).displayName != "Wall Torch":
                        torch_wall = Vec3(cursor.x+(w2+1)*latx, cursor.y+1, cursor.z+(w2+1)*latz)
                        if self.bot.blockAt(torch_wall).displayName not in self.ignored_blocks:
                            torch_surface = Vec3(-latx, 0, -latz)
                            #print(self.bot.blockAt(torch_wall))
                            print("  placing torch")
                            self.wieldItem("Torch")
                            self.safePlaceBlock(torch_wall,torch_surface)

                # Check if safe ahead, if not bridge
                for i in range(-w2, w2+1):
                    v = Vec3(cursor.x+i*latx, cursor.y-1, cursor.z+i*latz)
                    b = self.bot.blockAt(v)
                    if b.displayName in self.dangerBlocks:
                        # Can't walk on this block. We need to address this, or have to stop.
                        # Calculate block we need to place against
                        v_place = Vec3(cursor.x+i*latx-d.x, cursor.y-1-d.y, cursor.z+i*latz-d.z)
                        # Try three times.
                        for ii in range (0,1):
                            self.wieldItemFromList(self.fillBlocks)
                            self.bridgeBlock(v_place,d)
                            mined_blocks += 1
                            b = self.bot.blockAt(v)
                            if b.displayName not in self.dangerBlocks:
                                continue

                    if b.displayName in self.dangerBlocks:
                        print(f'*** fatal error. Cant bridge dangerous block {b.displayName}')
                        self.stopActivity = True
                        continue

                if self.stopActivity == True:
                    continue

            # Deposit mined materials
            self.safeWalk(start)
            self.restockFromChest(self.miningEquipList)
            self.eatFood()

            if self.stopActivity:
                break

    #
    # Mine a vertical shaft of N x N down to depth D
    #

    def shaftMine(self,r,min_y):

        # Determine center
        start_chest = self.findClosestBlock("Chest",xz_radius=3,y_radius=1)

        if not start_chest:
            print("Can't find starting position. Place chest wiht materials to place the center.")
            return

        print(f'Mining out area of {2*r+1} x {2*r+1} down to depth z={min_y}.')
        start = start_chest.position
        self.restockFromChest(self.miningEquipList)
        self.eatFood()

        for y in range(start.y-1,min_y,-1):

            print(f'  layer: {y}')

            for dz in range(0,r+1):

                if not self.stopActivity:

                    row_c = Vec3(start.x,y,start.z+dz)
                    self.safeWalk(row_c,1)
                    self.minePath(row_c,Vec3(row_c.x-r,row_c.y,row_c.z),2)
                    self.safeWalk(row_c,1)
                    self.minePath(row_c,Vec3(row_c.x+r,row_c.y,row_c.z),2)

                if not self.stopActivity:

                    row_c = Vec3(start.x,y,start.z-dz)
                    self.safeWalk(row_c,1)
                    self.minePath(row_c,Vec3(row_c.x-r,row_c.y,row_c.z),2)
                    self.safeWalk(row_c,1)
                    self.minePath(row_c,Vec3(row_c.x+r,row_c.y,row_c.z),2)

            if self.stopActivity:
                break

        print(f'Shaft mining ended at y={y}.')
        return True

    def doMining(self,args):

        if len(args) == 0:
            self.chat('Need to specify type of mine. Try "fast", "3x3" or "5x5".')
        else:
            mtype = args[0]
            if mtype == '3x3':
                self.stripMine(3,3,5)
            elif mtype == 'tunnel3x3':
                self.stripMine(3,3,0)
            elif mtype == '5x5':
                self.stripMine(5,5,5)
            elif mtype == 'tunnel5x5':
                self.stripMine(5,5,0)
            elif mtype == 'fast':
                self.stripMine(1,5,5)
            elif mtype == 'room':
                if len(args) < 4:
                    self.chat('Try: mine room <length> <width> <height>')
                else:
                    self.roomMine(args[1],args[2],args[3])

        self.endActivity()
        time.sleep(1)
        return True