
RFID_ERR_CODE = 228
TIMEOUT_CODE = 42

import sys
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
		
