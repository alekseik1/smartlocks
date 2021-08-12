Soft for washing room lock.

## Распиновка
### Если подключать руками, без платы
    # Режим GPIO.BCM
    lcd_rs = 2  #
    lcd_en = 4  #
    lcd_d4 = 3  #
    lcd_d5 = 15  #
    lcd_d6 = 14  #
    lcd_d7 = 18  #
    lcd_backlight = 17

И дальше как здесь (d0, d1, d2, d3 не используются):

![LCD Pinout](https://www.engineersgarage.com/wp-content/uploads/2019/10/5919393_orig-1.jpg)

[Статья по настройке](https://learn.adafruit.com/character-lcds/python-circuitpython)

**Нужен резистор на ~7.8 кОм для ноги V0** (уходит на `backlight`),
иначе контрастность зафакапится и ничего не будет видно на дисплее!

### Если через плату
На RFID модуль не идет RST и IRQ, поэтому нормальное считывание не работает.
Нужно попробовать тихонько провести через 4 разъема, которые не забирает плата Ethernet.

## Распиновка головы LCD
Хвост на себя, справа налево: VSS, V0, E, D5, D7, K
Хвост от себя, справа налево: дырка, A, D6, D4, RS, VDD