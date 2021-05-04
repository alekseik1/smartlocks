import time
import sys
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD
from threading import Lock
from contextlib import contextmanager
from loguru import logger
from log_utils import logger_wraps
from pirc522 import RFID


class UsesLock:
    lock: Lock

    def __init__(self, lock: Lock):
        self.lock = lock

    @contextmanager
    def acquire_lock(self, release_delay: int = 0):
        self.lock.acquire(blocking=True)
        try:
            yield self.lock
            if release_delay > 0:
                time.sleep(release_delay)
        finally:
            self.lock.release()


class DoorMagnet(UsesLock):
    FREEZE_AFTER_CLOSE = 2
    MAGNET_PIN = 5

    def __init__(self, lock: Lock):
        super().__init__(lock)
        GPIO.setup(self.MAGNET_PIN, GPIO.OUT)

    @staticmethod
    def _set_state(state: int):
        GPIO.output(DoorMagnet.MAGNET_PIN, state)

    @logger_wraps()
    def open(self):
        with self.acquire_lock():
            self._set_state(0)

    @logger_wraps()
    def close(self):
        with self.acquire_lock(release_delay=DoorMagnet.FREEZE_AFTER_CLOSE):
            self._set_state(1)


class LcdDisplay(UsesLock):

    # Raspberry Pi pin configuration:
    lcd_rs = 25
    lcd_en = 24
    lcd_d4 = 23
    lcd_d5 = 17
    lcd_d6 = 18
    lcd_d7 = 22
    lcd_backlight = 4

    # Define LCD column and row size for 16x2 LCD.
    lcd_columns = 16
    lcd_rows = 2

    lcd = None

    def __init__(self, lock: Lock):
        super().__init__(lock)
        # Initialize the LCD using the pins above.
        logger.debug('initializing lcd module')
        try:
            self.lcd = LCD.Adafruit_CharLCD(
                self.lcd_rs,
                self.lcd_en,
                self.lcd_d4,
                self.lcd_d5,
                self.lcd_d6,
                self.lcd_d7,
                self.lcd_columns,
                self.lcd_rows,
                self.lcd_backlight
            )
            logger.debug('(DONE) initializing lcd module')
        except:
            logger.error("error while initialising rfid module: {}".format(str(sys.exc_info())))

    def print_lcd(self, message: str):
        if not self.lcd:
            return
        logger.debug('updating LCD display text to: {}'.format(message))
        with self.acquire_lock():
            try:
                self.lcd.clear()
                self.lcd.message(message)
            except:
                logger.error("error messaging on lcd: {}".format(str(sys.exc_info())))


class RfidReader(UsesLock):
    RFID_ERR_CODE = 228
    TIMEOUT_CODE = 42

    def __init__(self, lock: Lock):
        super().__init__(lock)
        logger.debug('init RFID module')
        self.rdr = RFID(pin_rst=1, pin_irq=0, pin_mode=GPIO.BCM)
        logger.debug('(DONE) init RFID module')

    @logger_wraps()
    def wait_card(self):
        err = 1
        uid = []
        # i = 0
        try:
            while err:
                _ = time.clock()
                with self.acquire_lock():
                    (err, tt) = self.rdr.request()
                    if not err:
                        (err, uid) = self.rdr.anticoll()
                logger.debug(f'rfid found card: {tt} with error {err}')
                if tt is not None:
                    return err, uid
                logger.debug('rfid read took: {} seconds'.format(time.clock() - _), 'debug')
                """
                i += 1
                if i % 60 == 0:
                    # HACK: periodically reset RFID
                    rfid_reset(rdr)
                    i = 0
                """
                time.sleep(1)
            return err, uid
        except:
            logger.critical("error in rfid module: {}".format(str(sys.exc_info())))
            return self.RFID_ERR_CODE, uid

    @logger_wraps()
    def rfid_cleanup(self):
        try:
            self.rdr.cleanup()
            logger.info('done')
        except:
            logger.error("rfid cleanup error: {}".format(str(sys.exc_info())))

    @logger_wraps()
    def rfid_reset(self, rfid: RFID):
        # See: https://github.com/mxgxw/MFRC522-python/blob/master/MFRC522.py
        COMMAND_REG = 0x01
        PCD_RESETPHASE = 0x0F
        with self.acquire_lock():
            rfid.dev_write(COMMAND_REG, PCD_RESETPHASE)
            time.sleep(1)
            rfid.init()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DeviceManager(metaclass=Singleton):

    def __init__(self):
        # Single lock for them all
        self.lock = Lock()

        self.door_magnet = DoorMagnet(self.lock)
        self.lcd_display = LcdDisplay(self.lock)
        self.rfid_reader = RfidReader(self.lock)


manager = DeviceManager()
