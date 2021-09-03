#
# Farming
#

from javascript import require
Vec3       = require('vec3').Vec3
pathfinder = require('mineflayer-pathfinder')

from equipment import *
from blocks import * 
import time

farming_blocks = ["Wheat Crops"]
farming_items = ["Wheat"]
farming_seeds = ["Wheat Seeds"]

farmingEquipList = {
  "Bread":2,
  "Wheat Seeds":64,
  "Wheat":0
}

def safeMove(bot,x,y,z,r):
	try:
		bot.pathfinder.setGoal(pathfinder.goals.GoalNear(x,y,z,r))
	except Exception:
		pass

#
# Main farming loop. To start, the bot should be next to a chest, or deposit wont work
#
# Main loop
# - plant new crops
# - harvest ripe crops
# - deposit in chest

def findHarvestable(bot,center,r):

	global farming_blocks

	# Look for harvestable 
	for dx in range(-r,r+1):
		for dz in range(-r,r+1):
			v = addVec3(center,Vec3(dx,0,dz))
			b = bot.blockAt(v)
			#print(v,b.displayName)
			if b.displayName in farming_blocks and b.metadata == 7:
				return b
	return None

def findSoil(bot,center,r):

	global farming_blocks

	# Look for harvestable 
	for dx in range(-r,r+1):
		for dz in range(-r,r+1):
			v = addVec3(center,Vec3(dx,-1,dz))
			b = bot.blockAt(v)
			#print(v,b.displayName)
			if b.displayName == "Farmland":
				va = addVec3(center,Vec3(dx,0,dz))
				ba = bot.blockAt(va)
				if ba and ba.type == 0:
					return b
	return None

def doFarming(bot):

	up = Vec3(0, 1, 0)

	# Setup. Find out chest
	start_chest = findClosestBlock(bot,"Chest",2)
	if not start_chest:
		print("Please start farming near a chest.")
		return False
	start_pos = start_chest.position
	print("Farming started.")
	restockFromChest(bot, farmingEquipList)

	while True:
		if bot.stopActivity:
			print("Farming Ended.")
			return True

		long_break = 0

		# Harvest
		print("Harvesting:")
		for t in range(1,21):
			b = findHarvestable(bot,start_pos,10)
			if b and not bot.stopActivity:
				safeWalk(bot,b.position)
				print(f'  {b.displayName}  ({b.position.x}, {b.position.z}) ')
				try:
					bot.dig(b)
				except Exception as e:
					print("error while harvesting:",e)
				#time.sleep(0.2)
			else:
				print('  no more harvestable crops')
				long_break += 1
				break

		# Plant
		print("Planting:")
		crop = wieldItemFromList(bot,farming_seeds)
		if crop:
			for t in range(1,21):
				b = findSoil(bot,start_pos,10)
				if b and not bot.stopActivity:
					safeWalk(bot,b.position)
					if not checkInHand(bot,crop):
						print(f'Out of seeds of type {crop}.')
						break
					print(f'  {crop} ({b.position.x}, {b.position.z})')
					try:
						bot.placeBlock(b,up)
					except Exception as e:
						print("error while planting:",e)
				else:
					print('  no more empty soil')
					long_break += 1
					break

		else:
			print('  no plantable seeds in inventory.')

		# Deposit
		safeWalk(bot,start_pos)
		restockFromChest(bot, farmingEquipList)
		time.sleep(0.5)
		eatFood(bot)

		if long_break < 2:
			time.sleep(0.5)
		else:
			print('  nothing to do, taking a break.')
			time.sleep(60)