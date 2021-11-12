RFID_ERR_CODE = 228
TIMEOUT_CODE = 42

from threading import Thread
from time import sleep

from loguru import logger

from client import allowed_to_unlock, get_ip
from device_manager import manager


def uid_to_str(uid):
    # MIFARE CLASSIC
    return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])


class rfid_thread(Thread):
    def __init__(self):
        logger.debug("init RFID thread")
        Thread.__init__(self)
        self.name = "rfid thread"
        logger.debug("(DONE) init RFID thread")

    def run(self):
        last_uid = []
        same_uid_counter = 0
        uid = []

        while 1:
            manager.lcd_display.print_lcd("PLACE CARD \n ON READER")

            last_uid = uid

            err, uid = manager.rfid_reader.wait_card()
            try:

                same_uid_counter = (same_uid_counter + 1) * int(uid == last_uid)
                uid_str = uid_to_str(uid)
                logger.info("processing detected card: {}".format(uid_str))

                status, cause = allowed_to_unlock(uid_str)
                logger.info(
                    "got result to unlock: {} {}".format(str(status), str(cause))
                )
                if status:
                    if cause == "admin":
                        manager.lcd_display.print_lcd(get_ip())
                    elif cause == "last_time":
                        manager.lcd_display.print_lcd("IT IS YOUR\n LAST ENTER")
                    elif cause == "random":
                        manager.lcd_display.print_lcd("SO LUCKY TODAY")
                    else:
                        manager.lcd_display.print_lcd("YOU ARE WELCOME")
                    manager.door_magnet.open()
                    # TODO: TIMEOUT as separate variable
                    sleep(3)
                    manager.door_magnet.close()
                else:
                    if cause == "unknown_user":
                        manager.lcd_display.print_lcd("please register\n your card")
                    elif same_uid_counter == 0:
                        manager.lcd_display.print_lcd("access denied\ntry again :)")
                    elif same_uid_counter == 1:
                        manager.lcd_display.print_lcd("access denied\nsorry :(")
                    elif same_uid_counter == 2:
                        manager.lcd_display.print_lcd("access denied\nyou may go...")
                    elif same_uid_counter == 3:
                        manager.lcd_display.print_lcd("access denied\nwhat's now?!")
                    elif same_uid_counter == 4:
                        manager.lcd_display.print_lcd(
                            "ACCESS DENIED!!!\nplease go away:("
                        )
                    elif same_uid_counter == 5:
                        manager.lcd_display.print_lcd("goodbye _|___|_\n /(^_^)/")
                    elif same_uid_counter > 5:
                        manager.lcd_display.print_lcd("ACCESS DENIED")
                    sleep(1.5)
                logger.info("(DONE) processing detected card: {}".format(uid_str))

            except Exception as e:
                manager.door_magnet.open()
                logger.error(f"error in rfig thread {e}")
                # TODO: заправить на TIMEOUT
                sleep(3)
                manager.door_magnet.close()


rfid_thr = rfid_thread()
