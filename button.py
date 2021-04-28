from threading import Thread

import RPi.GPIO as GPIO
import time

from door import door_open, door_close
from loguru import logger

GPIO.setmode(GPIO.BCM)

BUTTON_PIN = 12
TIMEOUT = 3


def button_handler(channel):
    logger.info('[function] opening door for {} seconds'.format(TIMEOUT))
    door_open()
    time.sleep(TIMEOUT)
    door_close()
    logger.info('(DONE) [function] opening door for {} seconds'.format(TIMEOUT))


def button_init():
    logger.debug('init button')
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_handler, bouncetime=100)
    logger.debug('(DONE) init button')


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
            door_open()
            time.sleep(TIMEOUT)
            door_close()
            logger.info('(DONE) [thread] opening door for {} seconds'.format(TIMEOUT))


button_thr = button_thread()
