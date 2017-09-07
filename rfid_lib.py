from pirc522 import RFID
import RPi.GPIO
from time import clock
rdr = RFID(pin_rst = 1, pin_irq = 0, pin_mode = RPi.GPIO.BCM)

def wait_card(timeout = -1):
	err = 1
	start_time = clock()
        while err:
                (err, tt) = rdr.request()
		if not err:
			(err, uid) = rdr.anticoll()
		if timeout > 0 and clock() - start_time > timeout: break
		
	return err, uid

