#
# Misc chat functions
#


def sayStatus(bot):
	print('  level : ',bot.experience.level)
	print('  health: ',int(100*bot.health/20),"%")
	print('  food  : ',int(100*bot.food/20),"%")

def sayHello(bot):
    bot.chat('hello to you too!')