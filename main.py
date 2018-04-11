#!/usr/bin/python
from client import *
from lcd_lib import *
from rfid_lib import *
from button import *
from door import *

import sys
import RPi.GPIO as GPIO
from time import sleep

print_lcd("READY")
sleep(1)

try:
	configure("config.txt")
	door_init()
	door_close()
	door_test_thr.start()
	update_thr.start()
	rfid_thr.start()
	button_thr.start()
except:
	print_lcd("ERR: MAIN LOOP\n EXCEPTION")
	print "MAIN LOOP EXCEPTION: ", sys.exc_info()
	rfid_cleanup()
	GPIO.cleanup()
