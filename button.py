from door import *
import RPi.GPIO as GPIO
import time
from threading import Thread

GPIO.setmode(GPIO.BCM)

BUTTON_PIN = 12

def button_handler(channel):
	door_open()
	time.sleep(3)
	door_close()

def button_init():
	GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback = button_handler, bouncetime=100)

class button_thread(Thread):

	def __init__(self):
		Thread.__init__(self)
		GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	def run(self):
		while 1:
			GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING)
			door_open()
			time.sleep(3)
			door_close()


button_thr = button_thread()

