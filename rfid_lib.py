RFID_ERR_CODE = 228
TIMEOUT_CODE = 42

from threading import Thread
from time import sleep

from loguru import logger
from client import allowed_to_unlock, get_ip
from door import door_open, door_close
from hw_lock import hw_lock, hw_acq, hw_rel
from lcd_lib import print_lcd
import sys

try:
    from pirc522 import RFID
    import RPi.GPIO
    from time import clock

    logger.debug('init RFID module')
    rdr = RFID(pin_rst=1, pin_irq=0, pin_mode=RPi.GPIO.BCM)
    logger.debug('(DONE) init RFID module')
except:
    logger.critical("error initialising rfid module: {}".format(str(sys.exc_info())))


def wait_card(timeout=-1):
    err = 1
    start_time = clock()
    uid = []
    try:
        while err:
            _ = clock()
            hw_acq("rfid read")
            (err, tt) = rdr.request()
            if not err:
                (err, uid) = rdr.anticoll()
            hw_rel("rfid read")
            logger.debug(f'rfid found card: {tt} with error {err}')
            if tt is not None:
                return err, uid
            if timeout > 0 and clock() - start_time > timeout:
                break
            logger.debug('rfid read took: {} seconds'.format(clock() - _), 'debug')
            sleep(2)
        return err, uid
    except:
        logger.critical("error in rfid module: {}".format(str(sys.exc_info())))
        hw_lock.release()
        return RFID_ERR_CODE, uid


def rfid_cleanup():
    logger.info('starting')
    try:
        rdr.cleanup()
        logger.info('done')
    except:
        logger.error("rfid cleanup error: {}".format(str(sys.exc_info())))


def uid_to_str(uid):
    # MIFARE CLASSIC
    return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])


# s = ''
# for b in uid[:-1]:
#	s += str(b) + "."
# s += str(uid[len(uid)-1])
# return s

class rfid_thread(Thread):
    def __init__(self):
        logger.debug('init RFID thread')
        Thread.__init__(self)
        self.name = "rfid thread"
        logger.debug('(DONE) init RFID thread')

    def run(self):
        last_uid = []
        same_uid_counter = 0
        uid = []

        while 1:
            print_lcd("PLACE CARD \n ON READER")

            last_uid = uid

            err, uid = wait_card()
            try:

                same_uid_counter = (same_uid_counter + 1) * int(uid == last_uid)
                uid_str = uid_to_str(uid)
                logger.info("processing detected card: {}".format(uid_str))

                status, cause = allowed_to_unlock(uid_str)
                logger.info("got result to unlock: {} {}".format(str(status), str(cause)))
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
                    # TODO: заправить на TIMEOUT
                    sleep(3)
                    door_close()
                else:
                    if cause == "unknown_user":
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
                logger.info("(DONE) processing detected card: {}".format(uid_str))

            except:
                door_open()
                logger.error("error in rfig thread")
                # TODO: заправить на TIMEOUT
                sleep(3)
                door_close()


rfid_thr = rfid_thread()
