#
# Blueprints for construction
#

from javascript import require
Vec3     = require('vec3').Vec3

from blueprint import SpecialBuild, Blueprint


# Test Blueprint 1x2x1

bp_test = [
        [
                ["Torch"],
                ["Cobblestone"],
        ]
]

# Sorting System
# 3 x 4 x 6
# Two parts as we have to build the Chests first

bp_sorter_1 = [
  [
    ["Air"          , "Air"          , "Air" , ],
    ["Chest"        , "Chest"        , "Air" , ],
    ["Chest"        , "Chest"        , "Air" , ],
    ["Chest"        , "Chest"        , "Air" , ],
  ]
]

bp_sorter_2 = [
  [
    ["Air"          , "Air"          , "Stone Bricks" , ],
    ["Chest"        , "Chest"        , "Stone Bricks" , ],
    ["Chest"        , "Chest"        , "Stone Bricks" , ],
    ["Chest"        , "Chest"        , "Stone Bricks" , ],
  ],
  [
    ["Hopper"       , "Hopper"       , "Hopper"       , ],
    ["Hopper"       , "Hopper"       , "Hopper"       , ],
    ["Hopper"       , "Air"          , "Hopper"       , ],
    ["Air"          , "Hopper"       , "Hopper"       , ],
  ],
  [
    ["Redstone Comparator", "Redstone Comparator", "Redstone Comparator", ],
    ["Stone Bricks" , "Stone Bricks" , "Stone Bricks" , ],
    ["Redstone Wall Torch", "Redstone Wall Torch", "Redstone Wall Torch", ],
    ["Air"          , "Air"          , "Air"          , ],
  ],
  [
    ["Redstone Wire", "Redstone Wire", "Redstone Wire", ],
    ["Stone Bricks" , "Stone Bricks" , "Stone Bricks" , ],
    ["Stone Bricks" , "Stone Bricks" , "Stone Bricks" , ],
    ["Air"          , "Air"          , "Air"          , ],
  ],
  [
    ["Redstone Wire", "Redstone Wire", "Redstone Wire", ],
    ["Stone Bricks" , "Stone Bricks" , "Stone Bricks" , ],
    ["Redstone Repeater", "Redstone Repeater", "Redstone Repeater", ],
    ["Stone Bricks" , "Stone Bricks" , "Stone Bricks" , ],
  ],
  [
    ["Air"          , "Air"          , "Air"          , ],
    ["Redstone Wire", "Redstone Wire", "Redstone Wire", ],
    ["Stone Bricks" , "Stone Bricks" , "Stone Bricks" , ],
    ["Air"          , "Air"          , "Air"          , ],
  ],
]

def bp_sorter_buildf_1(x,y,z):
    # right chest halves place against left
    if x == 0 and y < 3:
        s = SpecialBuild()
        s.block_surface = Vec3(1,0,0)
        s.block_against = Vec3(-1,y,0)
        return s

def bp_sorter_buildf_2(x,y,z):

    # Redstone repeaters
    if y== 1 and z == 4:
        s = SpecialBuild()
        s.bot_pos = Vec3(x,2,z+1.5)
        return s

    # Hoppers. What a mess.
    if z == 1:
        if y == 0:
            #bottom row
            if x == 0:
                s = SpecialBuild()
                s.bot_pos = Vec3(0,0,2)
                s.block_against = Vec3(0,0,0)
                s.block_surface = Vec3(0,0,1)
                return s
            if x == 1:
                s = SpecialBuild()
                s.bot_pos = Vec3(1,0,2)
                s.block_against = Vec3(0,0,1)
                s.block_surface = Vec3(1,0,0)
                return s
        if y == 1:
            #2nd row
            if x == -1:
                s = SpecialBuild()
                s.bot_pos = Vec3(-1,0,2)
                s.block_against = Vec3(-1,1,0)
                s.block_surface = Vec3(0,0,1)
                return s
            if x == 1:
                s = SpecialBuild()
                s.bot_pos = Vec3(0,0,2)
                return s
        if y == 2:
            #3rd row
            if x == -1:
                s = SpecialBuild()
                s.bot_pos = Vec3(-2,0,2)
                return s
            if x == 0:
                s = SpecialBuild()
                s.bot_pos = Vec3(0,0,2)
                s.block_against = Vec3(0,2,0)
                s.block_surface = Vec3(0,0,1)
                return s
            if x == 1:
                s = SpecialBuild()
                s.bot_pos = Vec3(2,0,2)
                return s
        if y == 3:
            #3rd row
            if x == -1:
                s = SpecialBuild()
                s.bot_pos = Vec3(0,0,2)
                s.block_against = Vec3(-1,3,2)
                s.block_surface = Vec3(0,0,-1)
                return s
            if x == 0:
                s = SpecialBuild()
                s.bot_pos = Vec3(0,0,2)
                s.block_against = Vec3(0,3,2)
                s.block_surface = Vec3(0,0,-1)
                return s
            if x == 1:
                s = SpecialBuild()
                s.bot_pos = Vec3(0,0,2)
                s.block_against = Vec3(1,3,2)
                s.block_surface = Vec3(0,0,-1)
                return s

#
# Phases of a build are named NAME_1, NAME_2 etc.
#

def init(pybot):
    pybot.learnBlueprint( Blueprint("sorter_1",3,4,1,bp_sorter_1, bp_sorter_buildf_1) )
    pybot.learnBlueprint( Blueprint("sorter_2",3,4,6,bp_sorter_2, bp_sorter_buildf_2) ) 
    pybot.learnBlueprint( Blueprint("test_1",  1,2,1,bp_test,     None)               )
