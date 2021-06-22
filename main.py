#!/usr/bin/python
import os
import sys

import RPi.GPIO as GPIO
import datetime

from button import button_thr
from client import update_thr
from rfid_lib import rfid_thr
from loguru import logger
from device_manager import manager
from pygelf import GelfTcpHandler
from dotenv import load_dotenv


load_dotenv()


logger.add('logs/log_{time}.log', rotation=datetime.timedelta(days=1), retention=30, level='INFO')
# Send logs to a remote server
if 'REMOTE_SYSLOG_IP' in os.environ:
    logger.add(GelfTcpHandler(host=os.environ['REMOTE_SYSLOG_IP'], port=os.environ['REMOTE_SYSLOG_PORT']), level='INFO')
else:
    logger.warning('no REMOTE_SYSLOG_IP configured, will write logs only to STDOUT and logs/log_*.log')

logger.info('setting up GPIO mode')
GPIO.setmode(GPIO.BCM)
logger.info('(DONE) setting up GPIO mode')

try:
    DEBUG_ON_ = False
    RUN_SERVER = True
    logger.info("initializing threads")
    manager.door_magnet.close()
    update_thr.start()
    # Сильно жрет ЦПУ
    rfid_thr.start()
    button_thr.start()
    if RUN_SERVER:
        import uvicorn
        from admin_monitoring import app
        uvicorn.run(app, host='0.0.0.0', port=8085)
except:
    manager.lcd_display.print_lcd("ERR: MAIN LOOP\n EXCEPTION")
    logger.critical("main loop exception: {}".format(sys.exc_info()))
    manager.rfid_reader.rfid_cleanup()
