from hw_lock import hw_rel, hw_acq
import sys
from loguru import logger

try:
    import Adafruit_CharLCD as LCD

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

    # Initialize the LCD using the pins above.
    logger.debug('initializing lcd module')
    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                               lcd_columns, lcd_rows, lcd_backlight)
    logger.debug('(DONE) initializing lcd module')
except:
    logger.error("error while initialising rfid module: {}".format(str(sys.exc_info())))


def print_lcd(s):
    try:
        hw_acq("lcd print")
        logger.debug('updating LCD display text to: {}'.format(s))
        lcd.clear()
        lcd.message(s)
    except:
        logger.error("error messaging on lcd: {}".format(str(sys.exc_info())))
    finally:
        hw_rel("lcd print")
