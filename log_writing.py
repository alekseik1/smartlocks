import time
import sys

LOGS_PATH = "/home/pi/RPi_Washing/logs"

def print_log(s):
	try:
		f = open(LOGS_PATH, "a")
		f.write(time.asctime(time.localtime()) + ": " + s + "\n")
		f.close()
	except:
		print "log writing error", sys.exc_info()
