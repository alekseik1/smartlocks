#!/usr/bin/python
import sys

import RPi.GPIO as GPIO

from button import button_thr
from door import door_init, door_close
from client import update_thr
from rfid_lib import rfid_thr, rfid_cleanup
from lcd_lib import print_lcd
from log_writing import print_log

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
    print("MAIN LOOP EXCEPTION: ", sys.exc_info())
    rfid_cleanup()
    GPIO.cleanup()
