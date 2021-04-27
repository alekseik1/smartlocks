import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
from hw_lock import hw_acq, hw_rel
import time
from log_writing import print_log

MAGNET_PIN = 5
DETECTOR_PIN = 6


def door_init():
    GPIO.setup(MAGNET_PIN, GPIO.OUT)
    GPIO.setup(DETECTOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def door_open():
    hw_acq("door open")
    print_log("door opened")
    GPIO.output(MAGNET_PIN, 0)
    time.sleep(0.5)
    hw_rel("door open")


def door_close():
    hw_acq("door close")
    print_log("door closed")
    GPIO.output(MAGNET_PIN, 1)
    time.sleep(0.5)
    hw_rel("door close")


from threading import Thread


class door_test_thread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.name = "magnet test thread"

    def run(self):
        while 1:
            door_close()
            time.sleep(20)
            door_open()
            time.sleep(3)


door_test_thr = door_test_thread()
