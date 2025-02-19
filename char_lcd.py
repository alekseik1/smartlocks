#!/usr/bin/python
# Example using a character LCD connected to a Raspberry Pi or BeagleBone Black.
import sys

import Adafruit_CharLCD as LCD
from loguru import logger

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

if __name__ == '__main__':
    # Initialize the LCD using the pins above.
    logger.debug('Initializing LCD')
    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                               lcd_columns, lcd_rows, lcd_backlight)
    logger.debug('(DONE) Initializing LCD')

    try:
        message = input('Enter LCD message\n')
        while message != '0':
            logger.debug(f'sending message: {message}')
            lcd.message(message)
            message = input()
    except:
        pass
