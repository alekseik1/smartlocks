from rfid_lib import *

print_lcd("  PLACE CARD\n  ON READER")

try:
    while True:
        uid = wait_card()
        print_lcd(
            "UID: \n" + str(uid[0]) + '.' + str(uid[1]) + '.' + str(uid[2]) + '.' + str(uid[3]) + '.' + str(uid[4]))

except:
    # Calls GPIO cleanup
    rdr.cleanup()
