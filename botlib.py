#
# Utility functions that didn't fit anywhere else
#

import time
import datetime

activity_start = 0
activity_name = "None"

def myTime():
	now = datetime.datetime.now()
	return now.strftime("%H:%M:%S")


def startActivity(bot,name):
	global activity_start
	global activity_name

	t_str = myTime()
	print(60*'-')
	print(f'   {name:20} ({t_str})')
	print(60*'-')
	activity_start = time.time()
	activity_name = name
	bot.stopActivity = False

def stopActivity(bot):
	global activity_start
	global activity_name

	t_str = myTime()
	d_str = str(datetime.timedelta(seconds=int(time.time()-activity_start)))
	print(f'Activity {activity_name:15} ended at {t_str} (duration: {d_str})')
	print('')
	bot.clearControlStates('sneak', False)
	bot.stopActivity = True
