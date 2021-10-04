#
#  Various functions to deal with blocks, locations and movement
#

import time

from javascript import require
from math import sqrt, atan2, sin, cos
from botlib import *

Vec3     = require('vec3').Vec3
pathfinder = require('mineflayer-pathfinder')


#
# Movement functions for bot
#

class MovementManager:

    empty_blocks = [ "Water", "Lava", "Air", "Cave Air", "Void Air"]

    def __init__(self):
        print('movement ', end='')

    # Versatile blockAt, takes 3 coordinates or vector

    def blockAt(self, x, y=None, z=None):
        if y:
            v = Vec3(x,y,z)
        else:
            v = x
        return self.bot.blockAt(v)

    def safeWalk(self, toPosition, radius=1):
        self.pdebug(f'    safeWalk to {toPosition.x} {toPosition.y} {toPosition.z}  r={radius}',4)
        if not toPosition:
            print('*** error: toPosition is not defined.')
            return False
        if not toPosition.x:
            print('*** error: toPosition has no x coordinate. Not a position vector?')
            return False
        try:
            p = self.bot.pathfinder
            if p == None:
                print('  *** error: pathfinder is None in safeWalk.')
                return False
            p.setGoal(pathfinder.goals.GoalNear(toPosition.x,toPosition.y,toPosition.z,radius))
        except Exception as e:
            print(f'*** error in safeWalk {e}')
            return False
        t = walkTime(toPosition,self.bot.entity.position)
        if not self.speedMode:
             time.sleep(t)
        return True

    def walkTo(self,x,y=None,z=None):
        if hasattr(x, 'position') and x.position:
            v = Vec3(x.position.x,x.position.y,x.position.z)
            self.safeWalk(v,1)
        elif not y:
            self.safeWalk(x,1)
        else:
            v = Vec3(x,y,z)
            self.safeWalk(v,1)

    def walkToBlock(self,x,y=None,z=None):
        if hasattr(x, 'position') and x.position:
            v = Vec3(x.position.x+0.5,x.position.y,x.position.z+0.5)
            self.safeWalk(v)
        elif not y:
            v = Vec3(x.x+0.5,x.y,x.z+0.5)
            self.safeWalk(v)
        else:
            v = Vec3(x+0.5,y,z+0.5)
            self.safeWalk(v)

    def walkToBlock3(self,x,y=None,z=None):
        if hasattr(x, 'position') and x.position:
            v = Vec3(x.position.x+0.5,x.position.y,x.position.z+0.5)
            self.safeWalk(v,0.3)
        elif not y:
            v = Vec3(x.x+0.5,x.y,x.z+0.5)
            self.safeWalk(v,0.3)
        else:
            v = Vec3(x+0.5,y,z+0.5)
            self.safeWalk(v,0.3)


    # Walks on top of this block

    def walkOnBlock(self,x,y=None,z=None):
        if hasattr(x, 'position') and x.position:
            v = Vec3(x.position.x+0.5,x.position.y+1,x.position.z+0.5)
            self.safeWalk(v)
        elif not y:
            v = Vec3(x.x+0.5,x.y+1,x.z+0.5)
            self.safeWalk(v)
        else:
            v = Vec3(x+0.5,y+1,z+0.5)
            self.safeWalk(v)


    # this will attempt to walk on to block at v, and place a block in the direction d

    def safePlaceBlock(self,v,dv):
        v_gap = addVec3(v,dv)
        b     = self.bot.blockAt(v)
        b_gap = self.bot.blockAt(v_gap)

        if b_gap.displayName not in self.empty_blocks:
            self.perror(f'cant place block in space occupied by {b_gap.displayName}.')
            self.perror(f'{b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}')
            return False
        if b.displayName in self.empty_blocks:
            self.perror(f'place {b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}')
            return False
        try:
            self.bot.placeBlock(b,dv)
            return True
        except Exception as e:
            self.pexception(f'{b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}',e)
            return False

    def bridgeBlock(self, v, d):

        v_gap = addVec3(v,d)

        b     = self.bot.blockAt(v)
        b_gap = self.bot.blockAt(v_gap)

        d_inv = Vec3(-d.x,-d.y,-d.z)

        self.pdebug(f'  bridging {b_gap.displayName} @{v_gap.x}/{v_gap.y}/{v_gap.z} against {b.displayName} @{v.x}/{v.y}/{v.z}',2)

        self.walkToBlock(v.x,v.y+1,v.z)
        time.sleep(1)

        # Code from mineflayer.pathfinder
        # Target viewing direction while approaching edge
        # The Bot approaches the edge while looking in the opposite direction from where it needs to go
        # The target Pitch angle is roughly the angle the bot has to look down for when it is in the position
        # to place the next block

        targetYaw = atan2(d.x, d.z)
        targetPitch = -1.421
        viewVector = getViewVector(targetPitch, targetYaw)
        pos = self.bot.entity.position
        if not pos:
            print("*** error: position is None in bridgeBlock.")
            return False
        p = pos.offset(viewVector.x, viewVector.y, viewVector.z)
        self.bot.lookAt(p, True)
        self.bot.setControlState('sneak', True)
        time.sleep(0.5)
        self.bot.setControlState('back', True)
        time.sleep(0.5)
        self.bot.setControlState('back',False)
        if not self.safePlaceBlock(v,d):
            return False

        self.walkToBlock(v.x,v.y+1,v.z)
        self.bot.setControlState('sneak',False)
        time.sleep(0.5)
        return

    #
    #  Find closest (taxi geometry) block with specific content
    #  target can be a list or an item

    def findClosestBlock(self,target,xz_radius=2,y_radius=1,metadata=None,spaceabove=False):
        best_block = None
        best_dist  = 999

        p = self.bot.entity.position

        if type(target) is not list:
            target = [target]

        # Search larger and larger rectangles

        for r in range(0,xz_radius+1):
            for dx, dz in rectangleBorder(r,r):
                for dy in range(-y_radius,y_radius+1):
                        b = self.bot.blockAt(Vec3(p.x+dx,p.y+dy,p.z+dz))
                        #print(dx,dy,dz,b.displayName,target)
                        if b.displayName in target:
                            if metadata and b.metadata != metadata:
                                continue
                            if spaceabove:
                                b_above = self.bot.blockAt(Vec3(p.x+dx,p.y+dy+1,p.z+dz))
                                if not b_above or b_above.type != 0:
                                    continue
                            dist = sqrt(dx*dx+dy*dy+dz*dz)
                            # print("Found at ",v," distance ",dist)
                            if best_block == None or best_dist > dist:
                                best_block = b
                                best_dist = dist
            if best_block:
                return best_block
        return False


    def gotoLocation(self,l):
        if not l in self.myLocations:
            print(f'*** error: cant find location {l}')

        c = self.myLocations[l]
        print(f'moving to {l}')
        self.safeWalk(Vec3(c[0], c[1], c[2]), 1 )
        print("done.")
