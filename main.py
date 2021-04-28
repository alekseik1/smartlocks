#!/usr/bin/python
import sys

import RPi.GPIO as GPIO
import datetime

from button import button_thr
from door import door_init, door_close
from client import update_thr
from rfid_lib import rfid_thr, rfid_cleanup
from lcd_lib import print_lcd
from loguru import logger

logger.add('logs/log_{time}.log', rotation=datetime.timedelta(days=1))

try:
    DEBUG_ON_ = False
    logger.info("initializing threads")
    door_init()
    door_close()
    #	hw_acq("main stop")
    #	door_test_thr.start()
    update_thr.start()
    # Сильно жрет ЦПУ
    rfid_thr.start()
    button_thr.start()
except:
    print_lcd("ERR: MAIN LOOP\n EXCEPTION")
    logger.critical("main loop exception: {}".format(sys.exc_info()))
    rfid_cleanup()
    GPIO.cleanup()
