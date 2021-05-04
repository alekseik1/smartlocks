from threading import Thread

import RPi.GPIO as GPIO
import time

from device_manager import manager
from loguru import logger

BUTTON_PIN = 12
TIMEOUT = 3


class button_thread(Thread):

    def __init__(self):
        logger.debug('init button thread')
        Thread.__init__(self)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        logger.debug('(DONE) init button thread')

    def run(self):
        while 1:
            GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING)
            logger.info('[thread] opening door for {} seconds'.format(TIMEOUT))
            manager.door_magnet.open()
            time.sleep(TIMEOUT)
            manager.door_magnet.close()
            logger.info('(DONE) [thread] opening door for {} seconds'.format(TIMEOUT))


button_thr = button_thread()
