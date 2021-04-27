from threading import Thread

import RPi.GPIO as GPIO
import time

from door import door_open, door_close
from log_writing import print_log

GPIO.setmode(GPIO.BCM)

BUTTON_PIN = 12


def button_handler(channel):
    door_open()
    time.sleep(3)
    door_close()


def button_init():
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_handler, bouncetime=100)


class button_thread(Thread):

    def __init__(self):
        Thread.__init__(self)
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def run(self):
        while 1:
            GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING)
            print_log(">->->->->BUTTON PRESSED EVENT<-<-<-<-<")
            door_open()
            time.sleep(3)
            door_close()
            print_log("<-<-<-<-<BUTTON PRESSED EVENT>->->->->\n")


button_thr = button_thread()
