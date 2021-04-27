
RFID_ERR_CODE = 228
TIMEOUT_CODE = 42

import sys

from client import*
from lcd_lib import*
from time import *
from door import *
from log_writing import *
from hw_lock import *

from threading import Thread

try:
	from pirc522 import RFID
	import RPi.GPIO
	from time import clock
	rdr = RFID(pin_rst = 1, pin_irq = 0, pin_mode = RPi.GPIO.BCM)
except:
	print_log("ERROR INITIALISING RFID MODULE: " + str(sys.exc_info()))

def wait_card(timeout = -1):
	err = 1
	start_time = clock()
	uid = []
	try:
        	while err:
			hw_acq("rfid read")
                	(err, tt) = rdr.request()
			if not err:
				(err, uid) = rdr.anticoll()
			if timeout > 0 and clock() - start_time > timeout:
				break
				err = TIMEOUT_CODE
			hw_rel("rfid read")
			sleep(0.1)
		return err, uid
	except:
		print_log("ERROR IN RFID MODULE: " + str(sys.exc_info()))
		print_lcd("RFID MODULE\n ERROR")
		hw_lock.release()
		return RFID_ERR_CODE, uid

def rfid_cleanup():
	try:
		rdr.cleanup()
	except:
		print_log("RFID CLEANUP ERROR: " + str(sys.exc_info()))

def uid_to_str(uid):
	#MIFARE CLASSIC
        return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])
	#s = ''
	#for b in uid[:-1]:
	#	s += str(b) + "."
	#s += str(uid[len(uid)-1])
	#return s

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
			try:

	                	same_uid_counter = (same_uid_counter + 1) * int(uid == last_uid)
				print_log(">->->->->RFID EVENT<-<-<-<-<")
        	      		print_log(uid_to_str(uid))

	                	status, cause = allowed_to_unlock(uid_to_str(uid))
				print_log("got result to unlock: " + str(status) +" "+ str(cause))
				if status:
					if cause == "admin":
						print_lcd(get_ip())
					elif cause == "last_time":
						print_lcd("IT IS YOUR\n LAST ENTER")
					elif cause == "random":
						print_lcd("SO LUCKY TODAY") 
					else:
						print_lcd("YOU ARE WELCOME")
					door_open()
					sleep(3)
					door_close()
              			else:
					if   cause == "unknown_user":
						print_lcd("please register\n your card")
					elif same_uid_counter == 0:
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
	                               		print_lcd("ACCESS DENIED")
	                		sleep(1.5)
				print_log("<-<-<-<-<RFID EVENT>->->->->\n")

			except:
				door_open()
				print_log("ERROR in rfig thread")
				sleep(3)
				door_close()
rfid_thr = rfid_thread()
