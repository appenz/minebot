#
# Functions to manage inventory and eqipment
#

import time
from botlib import *

foodList = [
  "Sweet Berries",
  "Bread"
]

class InventoryManager:

    def __init__(self):
        print('inventory ', end='')

    def invItemCount(self,item_name):
        if not item_name:
            print("*** error: no item name given for invItemCount().")
            return 0

        count = 0
        inventory = self.bot.inventory.items()
        if inventory != []:
            # Count how many items we have of this type
            for i in inventory:
                if item_name == i.displayName:
                    count += i.count

        return count


    # Print current inventory. Aggregate slots to numbers.

    def printInventory(self):
        print("Inventory:")
        inventory = self.bot.inventory.items()
        iList = {}
        if inventory != []:

            # Count how many items we have of each type
            for i in inventory:
                iname = i.displayName
                if iname not in iList:
                    iList[iname] = 0
                iList[iname] += i.count

            # Now show the list
            for i in iList:
                print(f'  {iList[i]} {i}')
        else:
            self.bot.chat('empty')

    #
    # Check if a specific item is in hand
    #

    def checkInHand(self,item_name):

        if not self.bot.heldItem:
            return False

        if self.bot.heldItem.displayName == item_name:
            return True
        else:
            return False

    #
    # Equip an Item into the main hand.
    #
    # item can be:
    # - an Item in the inventory
    # - an Item ID
    # - displayName of an Item
    #
    # Returns name of the item in hand
    #

    def wieldItem(self,item,quiet=False):
        if item == None:
            print("error: trying to equip item 'None'.")
            return None

        if isinstance(item,str):

            # Check if we need to do this
            if self.bot.heldItem:
                if self.bot.heldItem.displayName == item:
                    return item

            time.sleep(1)

            # convert string to item first
            if self.bot.inventory.items == []:
                print("error: empty inventory, can't wield "+item)
                return None
            ii = None
            # find in inventory list
            for i in self.bot.inventory.items():
                if i.displayName == item:
                    ii = i
                    break
            # check if we found it
            if ii == None:
                print("error: can't find item "+item+" to wield.")
                return None
            item = ii

        if self.bot.heldItem:
            if self.bot.heldItem.displayName != item.displayName:
                # only do this if we are not holding it already
                if not quiet:
                    print(f'Switching to {item.displayName}')
                pass
            else:
                return self.bot.heldItem.displayName
        else:
            if not quiet:
                print(f'Equipping {item.displayName}')
            pass

        try:
            self.bot.equip(item,"hand")
        except Exception as e:
            print("*** wielding item failed. In hand {self.bot.heldItem.displayName} vs {item.displayName}")

        if self.bot.heldItem:
            return self.bot.heldItem.displayName
        else:
            return None

    #
    # Equip an item from a list of names
    #

    def wieldItemFromList(self,iList):
        if iList == None:
            print("error: equip list is empty.")
            return None

        # check if we have anything
        if self.bot.inventory.items == []:
            print("error: empty inventory, can't wield anything")
            return None

        # find in inventory list
        for i in self.bot.inventory.items():
            if i.displayName in iList:
                return self.wieldItem(i)

        # check if we found it
        print("error: can't find a useful item to wield.")
        return None

    def printEquipment(self):
        print("In Hand: ",bot.heldItem.displayName)

    #
    # Eat food, but only if hungry
    #

    def eatFood(self):
        # Check if hungry
        if self.bot.food > 16:
            return

        # Wield food in hand
        foodname = self.wieldItemFromList(foodList)
        if foodname:
            print('eating food '+foodname)
            self.bot.consume()
        else:
            print(f'food level {int(100*self.bot.food/20)}, but no food in inventory!')

    #
    #  Chest Management
    #

    def chestSpaceAvailable(self,chest):
        chest_size = chest.inventoryStart
        empty = chest_size
        # count empty slots in chest
        for s in chest.slots:
            if s != None and s.slot < chest_size:
                empty -= 1
        return empty

    def depositOneToChest(self,chest,i,count=None):
        if self.chestSpaceAvailable(chest) < 2:
            print('chest is full')
            return False
        if not count:
            count = i.count
        print(f'  > {count} x {i.displayName}')
        try:
            # print("Deposit:",i,count)
            chest.deposit(i.type,None,count)
        except Exception as e:
            print(f'*** error depositing {count} of item {i.displayName} ({i.count} in inventory)')
            return False
        return True

    def withdrawOneFromChest(self,chest,i,count=None):
        if not count:
            count = i.count
        print(f'  < {count} x {i.displayName}')
        try:
            chest.withdraw(i.type,None,count)
        except Exception as e:
            print(f'*** error withdrawing {count} of item {i.displayName} ({i.count} left)')
            return False
        return True

    # Depost items in chest
    # - If whitelist is present, only deposit those items. Otherwise everything.
    # - If blacklist is present, do NOT depost those items.

    def depositToChest(self, whitelist=[], blacklist=[]):
        chest_block = self.findClosestBlock("Chest",2)
        if chest_block == None:
            print("Depositing: can't deposit - no chest found")
            return False

        chest = self.bot.openChest(chest_block)
        time.sleep(0.5)
        chest_empty_slots = self.chestSpaceAvailable(chest)
        print(f'Depositing ({chest_empty_slots}/{chest.inventoryStart} free):')
        itemList = self.bot.inventory.items()
        for i in itemList:
            if whitelist != [] and i.displayName not in whitelist:
                continue
            elif blacklist != [] and i.displayName in blacklist:
                continue
            self.depositOneToChest(chest,i)

        chest.close()

    #
    # For any item on <itemList> make sure you have the right amount
    # - If too many, deposit
    # - If too few, take
    # Other items are ignored

    def restockFromChest(self, itemList):
        chest_block = self.findClosestBlock("Chest",2)
        if chest_block == None:
            print("Depositing: can't restock - no chest found")
            return False

        chest = self.bot.openChest(chest_block)
        time.sleep(0.5)

        print("Restocking goals:")

        for name,n_goal in itemList.items():
            n_inv = self.invItemCount(name)
            if n_goal > 0:
                print(f'  {name} {n_inv}/{n_goal}')

        print("Restocking operations:")

        nothing = True
        for name,n_goal in itemList.items():
            n_inv = self.invItemCount(name)

            if n_inv > n_goal:
                # deposit
                dn = n_inv-n_goal
                itemList = self.bot.inventory.items()
                for i in itemList:
                    if i.displayName == name:
                        count = min(i.count,dn)
                        if count > 0:
                            self.depositOneToChest(chest,i,count)
                            nothing = False
                            time.sleep(0.5)
                            dn -= count
                        if dn == 0:
                            continue
            elif n_goal > n_inv:
                # withdraw
                dn = n_goal-n_inv

                for i in chest.containerItems():
                    if i.displayName == name:
                        count = min(i.count,dn)
                        if count > 0:
                            self.withdrawOneFromChest(chest,i,count)
                            nothing = False
                            time.sleep(0.5)
                            dn -= count
                        if dn == 0:
                            continue
            else:
                # print(f'{name} {n_inv}/{n_goal}')
                pass

        if nothing:
            print('  no action taken.')

        chest.close()

    #
    #  Transfer all of the content of the closest chest, to the target chest
    #

    def transferToChest(self, target):

        chest_block = self.findClosestBlock("Chest",2)
        if chest_block == None:
            print("Depositing: can't transfer - no chest found")
            return False

        self.startActivity(bot,"Transfer chest contents to "+target)

        while not self.stopActivity:

            chest = self.bot.openChest(chest_block)
            time.sleep(0.5)

            print("Taking:")

            slots = 0
            for i in chest.containerItems():
                if i.count > 0:
                    #print(f'  taking {i.displayName} {i.count}')
                    withdrawOneFromChest(bot,chest,i,i.count)
                    time.sleep(0.5)
                    slots += 1
                    if slots > 27:
                        break

            chest.close()

            if slots == 0:
                print(f'  nothing left')
                break

            gotoLocation(self.bot,target)

            self.depositToChest()

            safeWalk(self.bot, chest_block.position)

        self.stopActivity()
