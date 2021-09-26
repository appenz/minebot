#
# Functions to manage inventory and eqipment
#

import time
from botlib import *

foodList = [
  "Sweet Berries",
  "Bread"
]

class Chest:

    def __init__(self,pybot):
        self.pybot = pybot
        self.block = self.pybot.findClosestBlock("Chest",2)
        self.chestObj = None
        if self.block == None:
            self.pybot.error("Can't find any chest nearby.")
            return

    def open(self):
            if self.chestObj:
                return True
            self.chestObj = self.pybot.bot.openChest(self.block)
            if not self.chestObj:
                self.pybot.perror("Can't open chest.")
                return False
            time.sleep(0.2)
            return True

    def close(self):
            self.chestObj.close()
            self.chestObj = None

    def spaceAvailable(self):
        if self.open():
            chest_size = self.chestObj.inventoryStart
            empty = chest_size
            # count empty slots in chest
            for s in self.chestObj.slots:
                if s != None and s.slot < chest_size:
                    empty -= 1
            return empty
        else:
            return 0

    def printContents(self, debug_lvl=1):
        if self.open():
            self.pybot.pdebug(f'Chest contents:', debug_lvl)
            empty = True
            for i in self.chestObj.containerItems():
                empty = False
                self.pybot.pdebug(f'  {i.count:2} {i.displayName}', debug_lvl)
            if empty:
                self.pybot.pdebug(f'  (none)', debug_lvl)

    def printItems(self, items):
        self.pybot.pdebug(f'  Item List:',1)
        for i in items:
            self.pybot.pdebug(f'    {i.slot:3}: {i.count:3} x {i.displayName}',1)

    def itemCount(self,item_arg):

        item_type, item_name = self.pybot.itemTypeAndName(item_arg)

        count = 0
        inventory = self.chestObj.containerItems()
        if inventory != []:
            # Count how many items we have of this type
            for i in inventory:
                if item_type == i.type:
                    count += i.count

        return count

    def depositItem(self,item_type,count=None):
        itemObj = self.pybot.Item(item_type,1)
        item_name = itemObj.displayName
        if self.spaceAvailable() < 2:
            self.pybot.perror('chest is full')
            return False
        count_max = self.pybot.invItemCount(item_type)
        if count < 1:
            count = count_max
        elif count > count_max:
            self.pybot.pdebug(f'  warning: deposit of {count} x {item_name} exceeds inventory ({count_max})',2)
            count = count_max

        self.pybot.pdebug(f'  > {count:2} x {item_name}   ({item_type})',3)
        try:
            newChest = self.chestObj.deposit(item_type,None,count)
            if newChest:
                self.chestObj = newChest
        except Exception as e:
            self.pybot.pexception(f'depositing {count} of item {item_name} type {item_type}',e)
            return False
        return True

    def withdrawItem(self,item_type,count=None):
        itemObj = self.pybot.Item(item_type,1)
        item_name = itemObj.displayName
        count_max = self.itemCount(item_type)
        if count < 1:
            count = count_max
        elif count > count_max:
            self.pybot.pdebug(f'  warning: withdrawal of {count} x {item_name} exceeds inventory ({count_max})',2)
            count = count_max
            
        self.pybot.pdebug(f'  < {count} x {item_name}   ({item_type})',3)
        try:
            newChest = self.chestObj.withdraw(item_type,None,count)
            if newChest:
                self.chestObj = newChest
        except Exception as e:
            self.pybot.pexception(f'*** withdrawing {count} of item {item_name} ({count_max} left)',e)
            return False
        return True

    # Depost items in chest
    # - If whitelist is present, only deposit those items. Otherwise everything.
    # - If blacklist is present, do NOT depost those items.

    def deposit(self, whitelist=[], blacklist=[]):
        if not self.open():
            self.pybot.perror('Cant open chest to deposit Items.')
            return False
        empty_slots = self.spaceAvailable()
        self.pybot.pdebug(f'Depositing ({empty_slots}/{self.chestObj.inventoryStart} free):',3)
        itemList = self.pybot.bot.inventory.items()
        for i in itemList:
            if whitelist != [] and i.displayName not in whitelist:
                continue
            elif blacklist != [] and i.displayName in blacklist:
                continue
            self.depositItem(i.type)

    # For any item on <itemList> make sure you have the right amount
    # - If too many, deposit
    # - If too few, take
    # Other items are ignored

    def restock(self, itemList):
        if not self.open():
            self.pybot.perror('Cant open chest to restock Items.')
            return False

        self.pybot.pdebug("Restocking goals for chest:",4)

        for name,n_goal in itemList.items():
            n_inv = self.pybot.invItemCount(name)
            if n_goal > 0:
                self.pybot.pdebug(f'  {name} {n_inv}/{n_goal}',4)

        self.pybot.pdebug("Restocking operations:",3)

        nothing = True
        for name,n_goal in itemList.items():
            n_inv = self.pybot.invItemCount(name)

            if n_inv > n_goal:
                # deposit
                dn = n_inv-n_goal
                invList = self.pybot.bot.inventory.items()
                for i in invList:
                    if i.displayName == name:
                        count = min(i.count,dn)
                        if count > 0:
                            self.depositItem(i.type,count)
                            nothing = False
                            dn -= count
                        if dn == 0:
                            continue
            elif n_goal > n_inv:
                # withdraw
                dn = n_goal-n_inv

                for i in self.chestObj.containerItems():
                    if i.displayName == name:
                        count = min(i.count,dn)
                        if count > 0:
                            self.withdrawItem(i.type,count)
                            nothing = False
                            dn -= count
                        if dn == 0:
                            continue
            else:
                self.pybot.pdebug(f'  {name} {n_inv}/{n_goal} -- no action',5)

        if nothing:
            self.pybot.pdebug(f'  nothing to do.',5)


#
# Mixin Class for the Bot. Has all the inventory and equipment functions
#

class InventoryManager:

    def __init__(self):
        print('inventory ', end='')

    #
    # Returns a pair of (item name, item type)
    # Input can be:
    # - displayName of an Item
    # - ID of an item
    # - an Item
    #

    def itemTypeAndName(self,item_arg):
        if isinstance(item_arg,int):
            item_type = item_arg
            itemObj = self.Item(item_type,1)
            item_name = itemObj.displayName
        elif isinstance(item_arg,str):
            item_name = item_arg
            # Find this item in the inventory
            if self.bot.inventory.items != []:
                # find in inventory list
                for item in self.bot.inventory.items():
                    if item.displayName == item_name:
                        item_type = item.type
                        break
                else:
                    item_type = None
        elif item_arg.type and item_arg.displayName:
            item_type = item_arg.type
            item_name = item_arg.displayName
        else:
            item_type = None
            item_name = "Unknown"

        return item_type, item_name

    def invItemCount(self,item_arg):

        item_type, item_name = self.itemTypeAndName(item_arg)

        count = 0
        inventory = self.bot.inventory.items()
        if inventory != []:
            # Count how many items we have of this type
            for i in inventory:
                if item_type == i.type:
                    count += i.count

        return count


    # Print current inventory. Aggregate slots to numbers.

    def printInventory(self):
        inventory = self.bot.inventory.items()
        iList = {}
        if inventory != []:
            self.pdebug(f'Inventory Slots:',4)

            # Count how many items we have of each type
            for i in inventory:
                self.pdebug(f'  -> {i.count:2} {i.displayName}',4)
                iname = i.displayName
                if iname not in iList:
                    iList[iname] = 0
                iList[iname] += i.count

            self.pdebug(f'Inventory:',1)

            # Now show the list
            for i in iList:
                self.pdebug(f'  {iList[i]:3} {i}',1)
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

    def wieldItem(self,item_arg):

        if not item_arg:
            self.perror("trying to equip item 'None'.")
            return None

        # Translate argument into type and name

        item_type, item_name = self.itemTypeAndName(item_arg)

        # check if we found it
        if item_type == None:
            self.perror(f'cant find item {item_name} ({item_type}) to wield.')
            return None

        # Am I already holding it?
        if self.bot.heldItem and self.bot.heldItem.type == item_type:
            return item_name

        # Equip the item
        self.pdebug(f'  equip {item_name} ({item_type})',3)

        try:
            self.bot.equip(item_type,"hand")
        except Exception as e:
            if self.bot.heldItem:
                n = self.bot.heldItem.displayName
            else:
                n = "None"
            self.pexception(f'wielding item failed. In hand {n} vs {item_name}',e)

        if not self.checkInHand(item_name):
            self.perror(f'Wielding item {item_name} failed!')
            
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
        if self.bot.food > 18:
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

    #
    # Depost items in chest
    # - If whitelist is present, only deposit those items. Otherwise everything.
    # - If blacklist is present, do NOT depost those items.

    def depositToChest(self, whitelist=[], blacklist=[]):
        chest = Chest(self)
        chest.deposit(whitelist,blacklist)
        chest.close()

    #
    # Find closest chest and restock from it according to the list
    #

    def restockFromChest(self, itemList):
        chest = Chest(self)
        chest.restock(itemList)
        chest.close()

    #
    #  Transfer all of the content of the closest chest, to the destination chest
    #

    def transferToChest(self, target):

        c1 = Chest(self)
        if c1.block == None:
            self.perror("Can't transfer chest contents - no chest found near starting point")
            return False

        self.startActivity("Transfer chest contents to "+target)

        while not self.stopActivity:

            # Pick up from the source chest
            c1.open()
            self.pdebug("Taking:",3)
            slots = 0
            for i in c1.chestObj.containerItems():
                if i.count > 0:
                    c1.withdrawItem(i.type,i.count)
                    time.sleep(0.2)
                    slots += 1
                    if slots > 27:
                        break
            c1.close()

            if slots == 0:
                print(f'  nothing left')
                break

            # Drop all into the destination chest
            self.gotoLocation(target)
            self.depositToChest()
            self.safeWalk(chest_block.position)

        self.stopActivity()
