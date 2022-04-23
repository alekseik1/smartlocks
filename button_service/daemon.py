import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from loguru import logger

from door_service.daemon import CONTROL_PORT, OPEN_TIME
from log_utils import setup_logger

basedir = Path(__file__).parent


def main():
    from RPi import GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.output(20, GPIO.HIGH)
    BUTTON_PIN = 16
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    while True:
        GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING)
        for action in ("unlock", "lock"):
            logger.info(f"sending {action} signal")
            r = requests.get(f"http://localhost:{CONTROL_PORT}/{action}")
            if r.status_code == 200:
                logger.debug("request completed successfully")
            elif r.status_code == 400:
                logger.warning(f"button request was not success, text={r.text}")
        time.sleep(OPEN_TIME)


if __name__ == "__main__":
    load_dotenv(basedir.parent / ".env")
    setup_logger()
    main()
