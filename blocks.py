#
#  Various functions to deal with blocks
#


from javascript import require
Vec3     = require('vec3').Vec3
pathfinder = require('mineflayer-pathfinder')

import time

from math import sqrt, atan2, sin, cos

empty_blocks = [ "Water", "Lava", "Air", "Cave Air", "Void Air"]

# Add two vectors

def addVec3(v1,v2):
	return Vec3(v1.x+v2.x,v1.y+v2.y,v1.z+v2.z)

def subVec3(v1,v2):
	return Vec3(v1.x-v2.x,v1.y-v2.y,v1.z-v2.z)

def lenVec3(v):
	return sqrt(v.x*v.x+v.y*v.y+v.z*v.z)

def distanceVec3(v1,v2):
	if not v1:
		print("*** error: v1 in distanceVec3() is null.")
		return None
	if not v2:
		print("*** error: v2 in distanceVec3() is null.")
		return None
	dv = subVec3(v1,v2)
	return lenVec3(dv)

def walkTime(v1,v2):
	if not v1:
		print("*** error: v1 in walkTime() is null.")
		return None
	if not v2:
		print("*** error: v2 in walkTime() is null.")
		return None
	d = distanceVec3(v1,v2)
	return d/4.1+0.25

def getViewVector (pitch, yaw):
	csPitch = cos(pitch)
	snPitch = sin(pitch)
	csYaw = cos(yaw)
	snYaw = sin(yaw)
	#print(f'ViewVector {pitch} / {yaw} -> {-snYaw * csPitch},{snPitch},{-csYaw * csPitch}' )
	return Vec3(-snYaw * csPitch, snPitch, -csYaw * csPitch)

#
# Moving around
#

def safeWalk(bot,toPosition, radius=1):
	if not toPosition:
		print('*** error: toPosition is not defined.')
		return False
	if not toPosition.x:
		print('*** error: toPosition has no x coordinate. Not a position vector?')
		return False
	try:
		p = bot.pathfinder
		if p == None:
			print('  *** error: pathfinder is None in safeWalk.')
			return False
		p.setGoal(pathfinder.goals.GoalNear(toPosition.x,toPosition.y,toPosition.z,radius))
	except Exception as e:
		print(f'*** error in safeWalk {e}')
		return False
	t = walkTime(toPosition,bot.entity.position)
	time.sleep(t)
	return True

# this will attempt to walk on to block at v, and place a block in the direction d

def safePlaceBlock(bot,v,dv):
	v_gap = addVec3(v,dv)
	b     = bot.blockAt(v)
	b_gap = bot.blockAt(v_gap)

	if b_gap.displayName not in empty_blocks:
		print(f'*** error: safePlaceBlock cant place block in space occupied by {b_gap.displayName}.')
		print(f'  * {b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}')
		return False

	if b.displayName in empty_blocks:
		print(f'*** error safePlaceBlock cant place against air.')
		print(f'  * {b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}')
		return False

	try:
		bot.placeBlock(b,dv)
		return True
	except Exception as e:
		print(f'*** error: placing block failed.')
		print(f'"*** exception: {e}')
		print(f'  * {b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}')
		return False

def bridgeBlock(bot, v, d):

	v_gap = addVec3(v,d)

	b     = bot.blockAt(v)
	b_gap = bot.blockAt(v_gap)	

	d_inv = Vec3(-d.x,-d.y,-d.z)

	print(f'  bridging {b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}')

	safeWalk(bot,Vec3(v.x+0.5,v.y+1,v.z+0.5),0.2)
	time.sleep(1)
	
	# Test only
	#	safePlaceBlock(bot,Vec3(v_gap.x+1,v_gap.y-1,v_gap.z),Vec3(0,1,0))
	#	return False

	# Code from mineflayer.pathfinder: ---
	# Target viewing direction while approaching edge
    # The Bot approaches the edge while looking in the opposite direction from where it needs to go
    # The target Pitch angle is roughly the angle the bot has to look down for when it is in the position
    # to place the next block
    
	targetYaw = atan2(d.x, d.z)
	targetPitch = -1.421
	viewVector = getViewVector(targetPitch, targetYaw)
	pos = bot.entity.position
	if not pos:
		print("*** error: position is None in bridgeBlock.")
		return False
	p = pos.offset(viewVector.x, viewVector.y, viewVector.z)
	bot.lookAt(p, True)
	bot.setControlState('sneak', True)
	time.sleep(1)	
	bot.setControlState('back', True)
	time.sleep(1)
	bot.setControlState('back',False)
	if not safePlaceBlock(bot,v,d):
		return False
	
	safeWalk(bot,Vec3(v.x+0.5,v.y+1,v.z+0.5),0.2)
	bot.setControlState('sneak',False)
	time.sleep(1)
	return

#
#  Find a block with specific content
#  item can be:
#  - a displayName
#  - a list of displayNames
# radius specifies search area

def findClosestBlock(bot,target,xz_radius=2,y_radius=1):
	best_block = None
	best_dist  = 999

	for dx in range(-xz_radius,xz_radius+1):
		for dy in range(-y_radius,y_radius+1):
			for dz in range(-xz_radius,+xz_radius+1):
				v = addVec3(bot.entity.position,bot.Vec3(dx,dy,dz))
				b = bot.blockAt(v)
				#print(v,b.displayName)
				if b.displayName == target:
					dist = sqrt(dx*dx+dy*dy+dz*dz)
					# print("Found at ",v," distance ",dist)
					if best_block == None or best_dist > dist:
						best_block = b
						best_dist = dist

	return best_block
