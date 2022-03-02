#
# Utility functions that didn't fit anywhere else
#

import time
import datetime

from javascript import require

from math import sqrt, atan2, sin, cos

Vec3  = require('vec3').Vec3

def myTime():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def myDate():
    now = datetime.datetime.now()
    return now.strftime("%m/%d/%y %H:%M")



#
# Math helper functions
#

def addVec3(v1,v2):
    return Vec3(v1.x+v2.x,v1.y+v2.y,v1.z+v2.z)

def subVec3(v1,v2):
    return Vec3(v1.x-v2.x,v1.y-v2.y,v1.z-v2.z)

def invVec3(v1):
    return Vec3(-v1.x,-v1.y,-v1.z)


def lenVec3(v):
    return sqrt(v.x*v.x+v.y*v.y+v.z*v.z)

# Minecraft is a right-handed coordinate system
#
#    0--------X------->  
#    |      North
#    Z   West   East
#    |      South
#    V    

def rotateLeft(v):
    return Vec3(v.z,0,-v.x)

def rotateRight(v):
    return Vec3(-v.z,0,v.x)

def directionStr(v):
    if abs(v.x) > abs(v.z):
        if v.x > 0:
            return "East"
        else:
            return "West"
    else:
        if v.z > 0:
            return "South"
        else:
            return "North"

def strDirection(d_str):
    d = d_str.lower()[0]
    if   d == 'n':
        return Vec3(0,0,-1)
    elif d == 's':
        return Vec3(0,0, 1)
    elif d == 'e':
        return Vec3(1,0, 0)
    elif d == 'w':
        return Vec3(-1,0,0)
    else:
        return None                


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
    return d/4.3+0.1

def getViewVector (pitch, yaw):
    csPitch = cos(pitch)
    snPitch = sin(pitch)
    csYaw = cos(yaw)
    snYaw = sin(yaw)
    #print(f'ViewVector {pitch} / {yaw} -> {-snYaw * csPitch},{snPitch},{-csYaw * csPitch}' )
    return Vec3(-snYaw * csPitch, snPitch, -csYaw * csPitch)

# Generator that steps through the outer part of a rectangle of w x h centered around 0,0

def rectangleBorder(w,h):

    if w == 0 and h == 0:
        yield 0,0
    elif h == 0:
        for dx in range(-w,w+1):
            yield dx,0
    elif w == 0:
        for dy in range(-h,h+1):
            yield 0,dy
    else:
        for dx in range(-w,w+1):
            yield dx,h
        for dy in range(h-1,-h-1,-1):
            yield w,dy
        for dx in range(w-1,-w-1,-1):
            yield dx,-h
        for dy in range(-h+1,h):
            yield -w,dy

def checkIntArg(x, min, max):
    if not x.lstrip('-').isdigit():
        return None
    x = int(x)
    if x >= min and x <= max:
        return x
    else:
        return None

def directionToVector(block):
    m = block.metadata

    if   m == 1: #North  001 vs 010
        return Vec3(0,0,-1)
    elif m == 3: # South 011 vs 011
        return Vec3(0,0,1)
    elif m == 5: # West  101 vs 100
        return Vec3(-1,0,0)
    elif m == 7: # East  111 vs 101
        return Vec3(1,0,0)
    else:
        return False

# Return a color based on current/max

def colorHelper(x,max):
    if x/max > 0.95:
        return "white","green"
    elif x/max > 0.75:
        return "black","yellow"
    elif x/max > 0.5:
        return "black","orange"
    else:
        return "white","red"











