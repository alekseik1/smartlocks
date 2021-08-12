import adafruit_character_lcd.character_lcd as characterlcd
import board
import digitalio

# Pinout
lcd_rs = digitalio.DigitalInOut(board.D2)
lcd_en = digitalio.DigitalInOut(board.D4)
lcd_d7 = digitalio.DigitalInOut(board.D18)
lcd_d6 = digitalio.DigitalInOut(board.D14)
lcd_d5 = digitalio.DigitalInOut(board.D15)
lcd_d4 = digitalio.DigitalInOut(board.D3)
lcd_backlight = digitalio.DigitalInOut(board.D17)

# LCD size
lcd_columns = 16
lcd_rows = 2


def at_center(message, l):
    margin = (l - len(message)) // 2
    disbalance = (l - len(message)) % 2
    return " " * margin + message + " " * (margin + disbalance)


lcd = characterlcd.Character_LCD_Mono(
    lcd_rs,
    lcd_en,
    lcd_d4,
    lcd_d5,
    lcd_d6,
    lcd_d7,
    lcd_columns,
    lcd_rows,
    backlight_pin=lcd_backlight,
    backlight_inverted=True,
)
# lcd.message = "Hello,\nworld"
lcd.create_char(0, [0, 16, 9, 5, 3, 15, 0, 0])
lcd.create_char(1, [4, 4, 4, 4, 4, 31, 14, 4])
lcd.create_char(2, [0, 1, 18, 20, 24, 30, 0, 0])
lcd.message = (
    at_center("PLACE CARD", lcd_columns) + "\n" + "\x01" * 4 + "\x01" * 8 + "\x01" * 4
)
lcd.backlight = True


from threading import Lock

from device_manager import RfidReader

reader = RfidReader(Lock())
print(reader.wait_card())
