from pirc522 import RFID
import RPi.GPIO
rdr = RFID(pin_rst = 1, pin_irq = 0, pin_mode = RPi.GPIO.BCM)

from lcd_lib import*


print_lcd("PUSH THE\n    CARD")

def wait_card():
	err = 1
        while err:
                (err, tt) = rdr.request()
	return err, tt

try:
 while True:
  (error, tag_type) = wait_card()
  if not error:
    #print("Tag detected")
    (error, uid) = rdr.anticoll()
    if not error:
      print_lcd("UID: \n" + str(uid[0]) + '.' + str(uid[1]) + '.' + str(uid[2]) + '.' + str(uid[3]) + '.' + str(uid[4]))

except:
	# Calls GPIO cleanup
	rdr.cleanup()

