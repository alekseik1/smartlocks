
RFID_ERR_CODE = 228
TIMEOUT_CODE = 42

import sys

from client import*
from lcd_lib import*
from time import *
from door import *

from threading import Thread

try:
	from pirc522 import RFID
	import RPi.GPIO
	from time import clock
	rdr = RFID(pin_rst = 1, pin_irq = 0, pin_mode = RPi.GPIO.BCM)
except:
	print "ERROR INITIALISING RFID MODULE: ", sys.exc_info()

def wait_card(timeout = -1):
	err = 1
	start_time = clock()
	uid = [-1, -1, -1, -1, -1]
	try:
        	while err:
                	(err, tt) = rdr.request()
			if not err:
				(err, uid) = rdr.anticoll()
			if timeout > 0 and clock() - start_time > timeout: 
				break
				err = TIMEOUT_CODE
			sleep(0.1)
		return err, uid
	except:
		print "ERROR IN RFID MODULE: ", sys.exc_info()
		print_lcd("RFID MODULE\n ERROR")
		return RFID_ERR_CODE, uid

def rfid_cleanup():
	try:
		rdr.cleanup()
	except:
		print "RFID CLEANUP ERROR: ", sys.exc_info()

def uid_to_str(uid):
        return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3]) + "." + str(uid[4])


class rfid_thread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.name = "rfid thread"

	def run(self):
		last_uid = []
		same_uid_counter = 0
		uid = []


		while 1:
                	print_lcd("PLACE CARD \n ON READER")

                	last_uid = uid

			err,uid = wait_card()

	                same_uid_counter = (same_uid_counter + 1) * int(uid == last_uid)

        	        print uid_to_str(uid)

	                if allowed_to_unlock(uid_to_str(uid)):
        	                print_lcd("YOU ARE WELCOME")
				door_open()
				sleep(3)
				door_close()
              		else:
				if   same_uid_counter == 0:
                        	        print_lcd("access denied\ntry again :)")
         	               	elif same_uid_counter == 1:
                	                print_lcd("access denied\nsorry :(")
	                        elif same_uid_counter == 2:
	                                print_lcd("access denied\nyou may go...")
	                        elif same_uid_counter == 3:
	                                print_lcd("access denied\nwhat's now?!")
	                        elif same_uid_counter == 4:
	                                print_lcd("ACCESS DENIED!!!\nplease go away:(")
	                        elif same_uid_counter == 5:
	                                print_lcd("goodbye _|___|_\n /(^_^)/")
	                        elif same_uid_counter > 5:
	                                print_lcd("  FUCK\n      OFF")
	                	sleep(1.5)


rfid_thr = rfid_thread()
