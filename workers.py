import os
import signal
import time
from threading import Thread

from loguru import logger
from RPi import GPIO

from client import allowed_to_unlock, configure, get_ip, update_list
from constants import (
    MESSAGE_LAST_ENTER,
    MESSAGE_LUCKY,
    MESSAGE_NO_REGISTRATION,
    MESSAGE_PLACE_CARD,
    MESSAGE_WELCOME,
)
from device_manager import DeviceManager


def uid_to_str(uid):
    # MIFARE CLASSIC
    return str(uid[0]) + "." + str(uid[1]) + "." + str(uid[2]) + "." + str(uid[3])


class RfidThread(Thread):
    def __init__(self, device_manager: DeviceManager):
        Thread.__init__(self)
        self.device_manager = device_manager
        self.name = "rfid thread"

    def run(self) -> None:
        same_uid_counter = 0
        last_uid = None
        while True:
            self.device_manager.lcd_display.print_lcd(MESSAGE_PLACE_CARD)

            err, uid = self.device_manager.rfid_reader.wait_card()
            try:
                if uid == last_uid:
                    same_uid_counter += 1
                uid_str = uid_to_str(uid)
                logger.info("processing detected card: {}".format(uid_str))

                status, cause = allowed_to_unlock(uid_str)
                logger.info(
                    "got result to unlock: {} {}".format(str(status), str(cause))
                )
                if status:
                    if cause == "admin":
                        self.device_manager.lcd_display.print_lcd(get_ip())
                    elif cause == "last_time":
                        self.device_manager.lcd_display.print_lcd(MESSAGE_LAST_ENTER)
                    elif cause == "random":
                        self.device_manager.lcd_display.print_lcd(MESSAGE_LUCKY)
                    else:
                        self.device_manager.lcd_display.print_lcd(MESSAGE_WELCOME)
                    self.device_manager.door_magnet.open()
                    # TODO: TIMEOUT as separate variable
                    time.sleep(3)
                    self.device_manager.door_magnet.close()
                else:
                    if cause == "unknown_user":
                        self.device_manager.lcd_display.print_lcd(
                            MESSAGE_NO_REGISTRATION
                        )
                    elif same_uid_counter == 0:
                        self.device_manager.lcd_display.print_lcd(
                            "access denied\ntry again :)"
                        )
                    elif same_uid_counter == 1:
                        self.device_manager.lcd_display.print_lcd(
                            "access denied\nsorry :("
                        )
                    elif same_uid_counter == 2:
                        self.device_manager.lcd_display.print_lcd(
                            "access denied\nyou may go..."
                        )
                    elif same_uid_counter == 3:
                        self.device_manager.lcd_display.print_lcd(
                            "access denied\nwhat's now?!"
                        )
                    elif same_uid_counter == 4:
                        self.device_manager.lcd_display.print_lcd(
                            "ACCESS DENIED!!!\nplease go away:("
                        )
                    elif same_uid_counter == 5:
                        self.device_manager.lcd_display.print_lcd(
                            "goodbye _|___|_\n /(^_^)/"
                        )
                    elif same_uid_counter > 5:
                        self.device_manager.lcd_display.print_lcd("ACCESS DENIED")
                    time.sleep(1.5)
                last_uid = uid
                logger.info("(DONE) processing detected card: {}".format(uid_str))

            except Exception as e:
                logger.error(f"error in rfig thread {e}")
                self.device_manager.door_magnet.open()
                os.kill(os.getpid(), signal.SIGINT)


class ButtonThread(Thread):
    BUTTON_PIN = 12
    TIMEOUT = 3

    def __init__(self, device_manager: DeviceManager):
        Thread.__init__(self)
        self.name = "button pressed thread"
        self.device_manager = device_manager
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def run(self):
        while 1:
            GPIO.wait_for_edge(self.BUTTON_PIN, GPIO.RISING)
            logger.info("[thread] opening door for {} seconds".format(self.TIMEOUT))
            self.device_manager.door_magnet.open()
            time.sleep(self.TIMEOUT)
            self.device_manager.door_magnet.close()
            logger.info(
                "(DONE) [thread] opening door for {} seconds".format(self.TIMEOUT)
            )


class ListUpdateThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.name = "list update thread"

    def run(self):
        configure("config.txt")
        while 1:
            logger.info("calling access list update")
            update_list()
            logger.info("(DONE) calling access list update")
            time.sleep(15 * 60)
