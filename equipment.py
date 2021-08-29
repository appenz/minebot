#
# Functions to manage inventory and eqipment
#

from blocks import * 
import time

foodList = [
  "Sweet Berries",
  "Bread"
]

def invItemCount(bot,item_name):
  if not item_name:
    print("*** error: no item name given for invItemCount().")
    return 0

  count = 0
  inventory = bot.inventory.items()
  if inventory != []:
    # Count how many items we have of this type
    for i in inventory:
      if item_name == i.displayName:
        count += i.count
  
  return count


# Print current inventory. Aggregate slots to numbers.

def printInventory(bot):
  print("Inventory:")
  inventory = bot.inventory.items()
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
    bot.chat('empty')

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

def wieldItem(bot,item):
  if item == None:
    print("error: trying to equip item 'None'.")
    return None

  if isinstance(item,str):

    # Check if we need to do this
    if bot.heldItem:
      if bot.heldItem.displayName == item:
        return item

    time.sleep(1)

    # convert string to item first
    if bot.inventory.items == []:
      print("error: empty inventory, can't wield "+item)
      return None
    ii = None
    # find in inventory list
    for i in bot.inventory.items():
      if i.displayName == item:
        ii = i
        break
    # check if we found it
    if ii == None:
      print("error: can't find item "+item+" to wield.")
      return None
    item = ii

  if bot.heldItem:
    if bot.heldItem.displayName != item.displayName:
      # only do this if we are not holding it already
      print(f'Switching to {item.displayName}')
    else:
      return bot.heldItem.displayName
  else:
    print(f'Equipping {item.displayName}')

  try:
    bot.equip(item,"hand")      
  except Exception as e:
    print("*** wielding item failed.",e)

  if bot.heldItem:
    return bot.heldItem.displayName
  else:
    return None

#
# Equip an item from a list of names
#

def wieldItemFromList(bot,iList):
  if iList == None:
    print("error: equip list is empty.")
    return None

  # check if we have anything
  if bot.inventory.items == []:
    print("error: empty inventory, can't wield anything")
    return None

  # find in inventory list
  for i in bot.inventory.items():
    if i.displayName in iList:
      return wieldItem(bot,i)

  # check if we found it
  print("error: can't find a useful item to wield.")
  return None

def printEquipment(bot):
	print("In Hand: ",bot.heldItem.displayName)

#
# Eat food, but only if hungry
#

def eatFood(bot):
  # Check if hungry
  if bot.food > 16:
    return  

  # Wield food in hand
  foodname = wieldItemFromList(bot,foodList)
  if foodname:
    print('eating food '+foodname)
    bot.consume()
  else:
    print(f'food level {int(100*bot.food/20)}, but no food in inventory!')

#
#  Chest Management
#

def chestSpaceAvailable(bot,chest):
  chest_size = chest.inventoryStart
  empty = chest_size
  # count empty slots in chest
  for s in chest.slots:
    if s != None and s.slot < chest_size:
      empty -= 1
  return empty

def depositOneToChest(bot,chest,i,count=None):
  if chestSpaceAvailable(bot,chest) < 2:
    print('chest is full')
    return False
  if not count:
    count = i.count
  print(f'  > {count} x {i.displayName}')
  try:
    # print("Deposit:",i,count)
    chest.deposit(i.type,None,count)
  except Exception as e:
    print("*** error while depositing.",e)
  return True

def withdrawOneFromChest(bot,chest,i,count=None):
#  if inventorySpaceAvailable(bot,chest) < 2:
#    print('chest is full')
#    return False
  if not count:
    count = i.count
  print(f'  < {count} x {i.displayName}')
  chest.withdraw(i.type,None,count)
  return True

# Depost items in chest
# - If whitelist is present, only deposit those items. Otherwise everything.
# - If blacklist is present, do NOT depost those items.

def depositToChest(bot, whitelist=[], blacklist=[]):
  chest_block = findClosestBlock(bot,"Chest",2)
  if chest_block == None:
    print("Depositing: can't deposit - no chest found")
    return False

  chest = bot.openChest(chest_block)
  time.sleep(0.5)
  chest_empty_slots = chestSpaceAvailable(bot,chest)
  print(f'Depositing ({chest_empty_slots}/{chest.inventoryStart} free):')
  itemList = bot.inventory.items()
  for i in itemList:
    if whitelist != [] and i.displayName not in whitelist:
      continue
    elif blacklist != [] and i.displayName in blacklist:
      continue
    depositOneToChest(bot,chest,i)

  chest.close()

#
# For any item on <itemList> make sure you have the right amount
# - If too many, deposit
# - If too few, take
# Other items are ignored

def restockFromChest(bot, itemList):
  chest_block = findClosestBlock(bot,"Chest",2)
  if chest_block == None:
    print("Depositing: can't restock - no chest found")
    return False

  chest = bot.openChest(chest_block)
  time.sleep(0.5)
 
  print("Restocking goals:")

  for name,n_goal in itemList.items():
    n_inv = invItemCount(bot,name)
    if n_goal > 0:
      print(f'  {name} {n_inv}/{n_goal}')

  print("Restocking operations:")

  for name,n_goal in itemList.items():
    n_inv = invItemCount(bot,name)

    if n_inv > n_goal:
      # deposit
      dn = n_inv-n_goal
      itemList = bot.inventory.items()
      for i in itemList:
        if i.displayName == name:
          count = min(i.count,dn)
          if count > 0:
            depositOneToChest(bot,chest,i,count)
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
            withdrawOneFromChest(bot,chest,i,count)
            time.sleep(0.5)
            dn -= count          
          if dn == 0:
            continue
    else:
      # print(f'{name} {n_inv}/{n_goal}')
      pass
 
  chest.close()








  