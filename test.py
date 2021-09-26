#
#  Test Routines for the bot
#

import time
from inventory import *

def wieldTest(pybot):
    delay_t = 0.0

    pybot.printInventory()

    print('-- Static tests')
    print(f'Stone Pickaxe: {pybot.mcData.itemsByName.stone_pickaxe.id}')
    print(f'Stone Axe:     {pybot.mcData.itemsByName.stone_axe.id}')
    print(f'End Crystal:   {pybot.mcData.itemsByName.end_crystal.id}')

    print('--- Test stone pickaxe:')
    if pybot.wieldItem(pybot.mcData.itemsByName.stone_pickaxe.id) != "Stone Pickaxe":
        print('Exception:')
        print(pybot.lastException)
        return
    else:
        print('passed')

    print('--- Test stone axe:')
    if pybot.wieldItem("Stone Axe") != "Stone Axe":
        print('Exception:')
        print(pybot.lastException)
        return
    else:
        print('passed')

    print('')
    print('--- Item equip long-term stability test.')
    i = 0
    while True:
        r = pybot.wieldItem('Stone Pickaxe')
        if r != "Stone Pickaxe": 
            break
        time.sleep(delay_t)
        i = i+1
        r = pybot.wieldItem('Stone Axe')
        if r != "Stone Axe": 
            break
        time.sleep(delay_t)
        i = i+1

    print(f'error after {i} equip operations.')
    print('')
    print('Exception:')
    print(pybot.lastException)

def chestTest1(pybot):

    chest = Chest(pybot)

    while True:
        chest.open()
        for i in chest.chestObj.containerItems():
            if i.count > 0:
                chest.withdrawItem(i,i.count)
        chest.close()

        time.sleep(1)

        chest.open()
        chest.deposit()
        chest.close()

def chestTest2(pybot):

    q = [1,5,20,40,63,64,60,15,2]
    i = 0

    chest = Chest(pybot)

    while True:

        i = (i +1) % len(q)

        restockList = {
            "Stone Pickaxe":q[i],
            "Stone Axe":q[i],
            "Bread":q[i],
            "Cobblestone":q[i],
            "Dirt":q[i],
            "Torch":q[i],
        }

        chest.open()
        chest.restock(restockList)
        chest.close()
        time.sleep(2)