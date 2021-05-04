from RPi import GPIO
from pirc522 import RFID
from time import sleep

rdr = RFID(
    pin_rst=1,
    pin_irq=0,
    pin_mode=GPIO.BCM
)
rdr.init()
rdr.set_antenna(True)

try:
    while True:
        # rdr.wait_for_tag()
        (error, tag_type) = rdr.request()
        print(error, tag_type)
        if not error:
            print("Tag detected")
            (error, uid) = rdr.anticoll()
            if not error:
                print("UID: " + str(uid))
        sleep(1)

except KeyboardInterrupt:
    print('Finishing')
    rdr.cleanup()
