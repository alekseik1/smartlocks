import time

import RPi.GPIO as GPIO
from pirc522 import RFID

rdr = RFID(pin_mode=GPIO.BCM, pin_rst=25, pin_irq=24)

while True:
    rdr.wait_for_tag()
    (error, tag_type) = rdr.request()
    if not error:
        print("Tag detected")
        # GPIO.setup(8, GPIO.OUT)
        # GPIO.output(8, GPIO.HIGH)
        # time.sleep(1)
        # GPIO.output(8, GPIO.LOW)
        (error, uid) = rdr.anticoll()
        if not error:
            print("UID: " + str(uid))
            # Select Tag is required before Auth
            if not rdr.select_tag(uid):
                # Auth for block 10 (block 2 of sector 2) using default shipping key A
                if not rdr.card_auth(
                    rdr.auth_a, 10, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], uid
                ):
                    # This will print something like (False, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                    print("Reading block 10: " + str(rdr.read(10)))
                    # Always stop crypto1 when done working
                    rdr.stop_crypto()

# Calls GPIO cleanup
rdr.cleanup()
