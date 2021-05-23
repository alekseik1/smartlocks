#!/usr/bin/python
import sys

import RPi.GPIO as GPIO
import datetime

from button import button_thr
from client import update_thr
from rfid_lib import rfid_thr
from loguru import logger
from device_manager import manager

logger.add('logs/log_{time}.log', rotation=datetime.timedelta(days=1), level='INFO')

logger.info('setting up GPIO mode')
GPIO.setmode(GPIO.BCM)
logger.info('(DONE) setting up GPIO mode')

try:
    DEBUG_ON_ = False
    logger.info("initializing threads")
    manager.door_magnet.close()
    update_thr.start()
    # Сильно жрет ЦПУ
    rfid_thr.start()
    button_thr.start()
except:
    manager.lcd_display.print_lcd("ERR: MAIN LOOP\n EXCEPTION")
    logger.critical("main loop exception: {}".format(sys.exc_info()))
    manager.rfid_reader.rfid_cleanup()
