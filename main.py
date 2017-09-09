#!/usr/bin/python
from client import *
from lcd_lib import *
from rfid_lib import *
import sys
import RPi.GPIO as GPIO
from time import sleep

def uid_to_str(uid):
	return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3]) + "." + str(uid[4])

configure('config.txt')

last_uid = []
same_uid_counter = 0
uid = []

print_lcd("READY")
sleep(1)

try:

	while 1:
		print_lcd("PLACE CARD \n ON READER")

		last_uid = uid

		while 1:
			err, uid = wait_card(15*60)
			if err: update_list() 
			else: break
	
		same_uid_counter = (same_uid_counter + 1) * int(uid == last_uid)
	
		print uid_to_str(uid)

		if allowed_to_unlock(uid_to_str(uid)):
			print_lcd("YOU ARE WELCOME")
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
except:
	print_lcd("ERR: MAIN LOOP\n EXCEPTION")
	print "MAIN LOOP EXCEPTION: ", sys.exc_info()
	rfid_cleanup()
	GPIO.cleanup()
