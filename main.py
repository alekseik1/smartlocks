#!/usr/bin/python
from client import *
from lcd_lib import *
from rfid_lib import *
from time import sleep

def uid_to_str(uid):
	return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3]) + "." + str(uid[4])

configure('config.txt')

while 1:
	err, uid = wait_card()
	print uid_to_str(uid)
	print_lcd ("alowed to unlock\n" + str(allowed_to_unlock(uid_to_str(uid))))
	sleep(5)

#print_lcd ("allowed to unlock\n" + str(allowed_to_unlock('136.52.198.107.1')))
#sleep(5)
#print_lcd ("allowed to unlock\n" + str(allowed_to_unlock('1234')))
#sleep(5)
