#
# Utility functions that didn't fit anywhere else
#

import time
import datetime

def myTime():
	now = datetime.datetime.now()
	return now.strftime("%H:%M:%S")


