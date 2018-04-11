import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time

MAGNET_PIN = 5
DETECTOR_PIN = 6

def door_init():
	GPIO.setup(MAGNET_PIN, GPIO.OUT)
	GPIO.setup(DETECTOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def door_open():
	print "door opened"
	GPIO.output(MAGNET_PIN, 0)

def door_close():
	print "door closed"
	GPIO.output(MAGNET_PIN, 1)

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
