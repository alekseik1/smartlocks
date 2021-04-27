#!/usr/bin/python
from client import *
from lcd_lib import *
from rfid_lib import *
from button import *
from door import *
from log_writing import *
from hw_lock import *

import sys
import RPi.GPIO as GPIO
from time import sleep

try:
	DEBUG_ON_ = False
	print_log("STARTUP")
	door_init()
	door_close()
#	hw_acq("main stop")
#	door_test_thr.start()
	update_thr.start()
	rfid_thr.start()
	button_thr.start()
except:
	print_lcd("ERR: MAIN LOOP\n EXCEPTION")
	print "MAIN LOOP EXCEPTION: ", sys.exc_info()
	rfid_cleanup()
	GPIO.cleanup()
