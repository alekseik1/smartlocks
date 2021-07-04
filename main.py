#!/usr/bin/python
import datetime
import os
import sys
import time

import RPi.GPIO as GPIO
from dotenv import load_dotenv
from loguru import logger
from pygelf import GelfTcpHandler

from device_manager import DeviceManager
from workers import ButtonThread, ListUpdateThread, RfidThread

load_dotenv()


logger.add(
    "logs/log_{time}.log",
    rotation=datetime.timedelta(days=1),
    retention=30,
    level="INFO",
)
# Send logs to a remote server
if "REMOTE_SYSLOG_IP" in os.environ:
    logger.add(
        GelfTcpHandler(
            host=os.environ["REMOTE_SYSLOG_IP"], port=os.environ["REMOTE_SYSLOG_PORT"]
        ),
        level="INFO",
    )
else:
    logger.warning(
        "no REMOTE_SYSLOG_IP configured, will write logs only to STDOUT and logs/log_*.log"
    )

logger.info("setting up GPIO mode")
GPIO.setmode(GPIO.BCM)
logger.info("(DONE) setting up GPIO mode")

try:
    DEBUG_ON_ = False
    RUN_SERVER = True
    manager = DeviceManager()
    manager.door_magnet.close()
    logger.info("initializing threads")
    # Сильно жрет ЦПУ
    logger.info(1)
    update_thread = ListUpdateThread()
    update_thread.setDaemon(True)
    logger.info(2)
    rfid_thread = RfidThread(device_manager=manager)
    rfid_thread.setDaemon(True)
    logger.info(3)
    button_thread = ButtonThread(device_manager=manager)
    button_thread.setDaemon(True)
    for thread in [rfid_thread, button_thread, update_thread]:
        logger.info(thread.name)
        thread.start()
    if RUN_SERVER:
        import uvicorn

        from admin_monitoring import app

        uvicorn.run(app, host="0.0.0.0", port=8085)
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        logger.info("keyboard interrupt, exiting")
except:
    logger.critical("main loop exception: {}".format(sys.exc_info()))
