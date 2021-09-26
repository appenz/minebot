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


#
# Math helper functions
#

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
    if not x.isdigit():
        return False
    x = int(x)
    if x >= min and x <= max:
        return x
    else:
        return 0


















