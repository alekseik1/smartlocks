import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
from hw_lock import hw_acq, hw_rel
import time
from loguru import logger

MAGNET_PIN = 5
DETECTOR_PIN = 6


def door_init():
    logger.debug('GPIO init door')
    GPIO.setup(MAGNET_PIN, GPIO.OUT)
    GPIO.setup(DETECTOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    logger.debug('(DONE) GPIO init door')


def door_open():
    logger.info("sending door open signal")
    hw_acq("door open")
    GPIO.output(MAGNET_PIN, 0)
    time.sleep(0.5)
    hw_rel("door open")
    logger.info("(DONE) sending door open signal")


def door_close():
    logger.info("sending door close signal")
    hw_acq("door close")
    GPIO.output(MAGNET_PIN, 1)
    time.sleep(0.5)
    hw_rel("door close")
    logger.info("(DONE) sending door close signal")


from threading import Thread


class door_test_thread(Thread):
    def __init__(self):
        logger.debug('init door test thread')
        Thread.__init__(self)
        self.name = "magnet test thread"
        logger.debug('(DONE) init door test thread')

    def run(self):
        while 1:
            logger.debug('[thread test] calling door close and open')
            door_close()
            time.sleep(20)
            door_open()
            time.sleep(3)
            logger.debug('(DONE) [thread test] calling door close and open')


door_test_thr = door_test_thread()
