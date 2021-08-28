#
# Functions for mining blocks
#

from javascript import require
Vec3     = require('vec3').Vec3

from equipment import *
from blocks import *
from farming import *

mining_equipment = ["Stone Pickaxe", "Torch", "Bread"]
ignored_blocks = [ "Torch", "Sign"]

miningEquipList= {
  "Bread":2,
  "Stone Pickaxe":3,
  "Torch": 10,
  "Cobblestone" : 64,
  "Dirt" : 0,
  "Andesite" : 0,
  "Diorite" : 0,
  "Granite" : 0,
  "Gravel" : 0,
  "Flint" : 0,
  "Iron Ore" : 0,
  "Gold Ore" : 0,
  "Coal" : 0,
  "Redstone" : 0,
  "Lapis" : 0,
  "Emerald" : 0,
  "Sand" : 0,
  "Sandstone" : 0
}

dangerBlocks = {
	"Air",
	"Lava",
	"Water"
}

fillBlocks = {
	"Cobblestone",
	"Dirt"
}

def mineBlock(bot,x,y,z):
	v = bot.Vec3(x,y,z)
	b = bot.blockAt(v)
	if b.digTime(274) > 100 and b.displayName not in ignored_blocks:
		print(f'  mine   ({x},{y},{z}) {b.displayName} t:{b.digTime(274)}')	
		bot.dig(b)
		return 1	
	else:
		# print(f'  ignore ({x},{y},{z}) {b.displayName}')	
		return 0


def mineRect(bot,sx,sz,r,sy):
	for x in range(sx,sx+r,1):
		mineBlock(bot,x,sz+r,sy)		
	for z in range(sz+r,sz-r,-1):
		mineBlock(bot,sx+r,z,sy)		
	for x in range(sx+r,sx-r,-1):
		mineBlock(bot,x,sz-r,sy)		
	for z in range(sz-r,sz+r,1):
		mineBlock(bot,sx-r,z,sy)		
	for x in range(sx-r,sx,1):
		mineBlock(bot,x,sz+r,sy)		

# 
# Mine a rectacgle (without the center)
# centered around x,z with distance from center of r
#

def areaMine(bot):
	#wieldPickaxe(bot)
	# Get center position
	sx = int(bot.entity.position.x-1)
	sy = int(bot.entity.position.y)
	sz = int(bot.entity.position.z)
	print("Starting at:",sx,sz)
	mineRect(bot,sx,sz,1,sy)
	mineRect(bot,sx,sz,2,sy)
	mineRect(bot,sx,sz,3,sy)
	mineRect(bot,sx,sz,4,sy)


def stripMine(bot):

	width = 3
	height = 3

	# Determine "forward" direction	from chest+torch
	start_chest = findClosestBlock(bot,"Chest",xz_radius=3,y_radius=1)
	start_torch = findClosestBlock(bot,"Torch",xz_radius=3,y_radius=1)

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

	restockFromChest(bot, miningEquipList)

	while True:
		if bot.stopActivity:
			print("Strip mining ended.")
			return

		mined_blocks = 0

		while mined_blocks < 100 and not bot.stopActivity:

			# Move deeper down the strip mine
			cursor = addVec3(cursor, d)
			tic = abs(cursor.x)+abs(cursor.z)

			safeWalk(bot,cursor)

			# Check if safe

			for i in range(-w2, w2+1):
				v = Vec3(cursor.x+i*latx, cursor.y-1, cursor.z+i*latz)
				b = bot.blockAt(v)		
				if b.displayName in dangerBlocks:
					# Can't walk on this block. We need to address this, or have to stop.
					# Calculate block we need to place against
					v_place = Vec3(cursor.x+i*latx-d.x, cursor.y-1-d.y, cursor.z+i*latz-d.z)
					# Try three times.
					for ii in range (0,1):						
						wieldItemFromList(bot,fillBlocks)
						bridgeBlock(bot,v_place,d)
						b = bot.blockAt(v)
						if b.displayName not in dangerBlocks:
							continue

				if b.displayName in dangerBlocks:
					print(f'*** fatal error. Cant bridge dangerous block {b.displayName}')
					bot.stopActivity = True
					continue

			if bot.stopActivity == True:
				continue

			for i in range(-w2, w2+1):
				for j in range(0,height):
					wieldItem(bot,"Stone Pickaxe")
					mined_blocks += mineBlock(bot,cursor.x+i*latx, cursor.y+j, cursor.z+i*latz)

			if tic % 8 == 0:
				# place a torch
				torch_v = Vec3(cursor.x+(w2)*latx, cursor.y+1, cursor.z+(w2)*latz)

				#print(bot.blockAt(torch_v))
				if bot.blockAt(torch_v).displayName != "Wall Torch":
					torch_wall = Vec3(cursor.x+(w2+1)*latx, cursor.y+1, cursor.z+(w2+1)*latz)
					if bot.blockAt(torch_wall).displayName != "Air":	
						torch_surface = Vec3(-latx, 0, -latz)
						#print(bot.blockAt(torch_wall))
						print("  placing torch")
						wieldItem(bot,"Torch")
						bot.placeBlock(bot.blockAt(torch_wall),torch_surface)

		# Deposit mined materials
		safeWalk(bot,start)
		restockFromChest(bot, miningEquipList)
		time.sleep(0.5)
		eatFood(bot)
		time.sleep(0.5)





