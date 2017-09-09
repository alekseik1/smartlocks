import sys
try: 
	import Adafruit_CharLCD as LCD
# Raspberry Pi pin configuration:
	lcd_rs        = 25 
	lcd_en        = 24
	lcd_d4        = 23
	lcd_d5        = 17
	lcd_d6        = 18
	lcd_d7        = 22
	lcd_backlight = 4

# Define LCD column and row size for 16x2 LCD.
	lcd_columns = 16
	lcd_rows    = 2

# Initialize the LCD using the pins above.
	lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)
except:
	print "ERROR WHILE INITIALISING RFID MODULE", sys.exc_info()

def print_lcd(s):
	try:
		lcd.clear()
		lcd.message(s)
	except:
		print "ERROR MESSAGING ON LCD", sys.exc_info()

